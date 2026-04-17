import logging

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AudioAnalysisResult,
    ClaimResult,
    ContentType,
    CredibilityBreakdown,
    ExternalFactCheck,
    ImageAnalysisResult,
    NewsArticle,
    QdrantStats,
    SourceScore,
    Verdict,
    VideoAnalysisResult,
)
from app.qdrant.client import get_qdrant
from app.services.audio_analyzer import analyze_audio_content
from app.services.claim_extractor import analyze_propaganda, extract_claims
from app.services.credibility_scorer import (
    build_verdict_reason,
    compute_credibility,
    google_reviews_to_score,
    score_to_verdict,
)
from app.services.explanation_engine import generate_explanation
from app.services.fact_retriever import (
    find_matching_misinfo,
    get_source_credibility,
    retrieve_evidence,
)
from app.services.google_factcheck import get_factcheck_verdict, search_claims
from app.services.image_analyzer import analyze_image_content
from app.services.language_detector import detect_language_with_method
from app.services.news_api import search_news
from app.services.translator import translate_text
from app.services.url_fetcher import fetch_url_content
from app.services.video_analyzer import analyze_video_content

logger = logging.getLogger(__name__)

MAX_CONTENT_LENGTH = 10_000
MAX_CLAIMS = 10


async def analyze_content(request: AnalysisRequest) -> AnalysisResponse:
    log: list[str] = []

    text_content = _sanitize_input(request.content, request.content_type)

    if request.content_type == ContentType.URL:
        fetched = fetch_url_content(text_content, max_length=MAX_CONTENT_LENGTH)
        if fetched != text_content:
            log.append(f"URL fetched: extracted {len(fetched)} chars of article text")
            text_content = fetched
        else:
            log.append("URL fetch: could not extract content, using raw URL")

    if request.content_type == ContentType.TEXT and not text_content.strip():
        return _empty_response("No analyzable content provided.")

    qdrant = get_qdrant()

    if request.language:
        language = request.language
        detection_method = "user_override"
        log.append(f"Language: {language} (user specified)")
    else:
        lang_input = text_content if text_content and not text_content.startswith("(") else "analysis"
        language, detection_method = detect_language_with_method(lang_input)
        log.append(f"Language detected: {language} via {detection_method}")

    image_result = None
    ai_gen_score = 0.0

    if request.content_type == ContentType.IMAGE:
        img_analysis = analyze_image_content(request.content)
        image_result = ImageAnalysisResult(**img_analysis)
        ai_gen_score = img_analysis["ai_probability"]
        method = img_analysis.get("analysis_method", "heuristic")
        log.append(f"Image analysis ({method}): AI probability {ai_gen_score:.1%}")

        extracted_text = img_analysis.get("extracted_text", "")
        text_claims_from_image = img_analysis.get("text_claims", [])
        description = img_analysis.get("description", "")

        if extracted_text.strip():
            text_content = extracted_text
            log.append(f"Image OCR: extracted {len(extracted_text)} chars of text from image")
        elif text_claims_from_image:
            text_content = ". ".join(text_claims_from_image)
            log.append(f"Image claims: {len(text_claims_from_image)} claim(s) from image content")
        elif description:
            text_content = description
            log.append(f"Image description: using Vision description for analysis")
        else:
            text_content = "(Image content submitted for analysis)"
            log.append("Image: no text or claims found in image")

    audio_result = None
    if request.content_type == ContentType.AUDIO:
        aud_analysis = analyze_audio_content(request.content)
        audio_result = AudioAnalysisResult(**aud_analysis)
        ai_gen_score = max(ai_gen_score, aud_analysis["clone_probability"])
        text_content = text_content or "(Audio content submitted for analysis)"
        log.append(f"Audio analysis: clone probability {aud_analysis['clone_probability']:.1%}")

    video_result = None
    if request.content_type == ContentType.VIDEO:
        vid_analysis = analyze_video_content(request.content)
        video_result = VideoAnalysisResult(**vid_analysis)
        ai_gen_score = max(ai_gen_score, vid_analysis["deepfake_probability"])
        text_content = text_content or "(Video content submitted for analysis)"
        log.append(f"Video analysis: deepfake probability {vid_analysis['deepfake_probability']:.1%}")

    claims = _safe_extract_claims(text_content)
    log.append(f"Claim extraction: {len(claims)} claim(s) found")

    propaganda = _safe_propaganda_analysis(text_content, language)
    emotional_score = propaganda.get("emotional_score", 0.5)
    log.append(f"Propaganda analysis: emotional score {emotional_score:.1%}")

    all_evidence: list[dict] = []
    all_misinfo: list[dict] = []
    all_external: list[dict] = []
    all_sources: list[dict] = []
    claim_results: list[ClaimResult] = []

    for claim_text in claims:
        evidence = retrieve_evidence(qdrant, claim_text, language, top_k=5)

        if language != "en":
            en_claim = translate_text(claim_text, language, "en")
            if en_claim != claim_text:
                en_evidence = retrieve_evidence(qdrant, en_claim, "en", top_k=3)
                seen_texts = {e["text"] for e in evidence}
                for e in en_evidence:
                    if e["text"] not in seen_texts:
                        evidence.append(e)
                        seen_texts.add(e["text"])
                evidence.sort(key=lambda e: e["relevance_score"], reverse=True)
                evidence = evidence[:5]

        misinfo = find_matching_misinfo(qdrant, claim_text, language, threshold=0.65)
        source_cred, matched_src = get_source_credibility(qdrant, claim_text, top_k=3)

        gfc_reviews = search_claims(claim_text, language)
        gfc_score = google_reviews_to_score(gfc_reviews)
        gfc_verdict = get_factcheck_verdict(gfc_reviews)

        all_evidence.extend(evidence)
        all_misinfo.extend(misinfo)
        all_external.extend(gfc_reviews)
        all_sources.extend(matched_src)

        best_evidence_score = max((e["relevance_score"] for e in evidence), default=0.0)
        best_misinfo_score = max((m["similarity"] for m in misinfo), default=0.0)

        claim_credibility, _ = compute_credibility(
            ai_generation_score=ai_gen_score,
            fact_evidence_score=best_evidence_score,
            source_credibility_score=source_cred,
            misinfo_pattern_score=best_misinfo_score,
            emotional_language_score=emotional_score,
            google_factcheck_score=gfc_score,
        )

        verdict_str = gfc_verdict or score_to_verdict(claim_credibility)

        source_scores = [
            SourceScore(
                source=e.get("source", "unknown"),
                url=e.get("url", ""),
                relevance=e.get("relevance_score", 0.0),
                credibility=e.get("credibility_score", 0.5),
            )
            for e in evidence[:3]
        ]

        external_fc = [
            ExternalFactCheck(
                claim_text=r.get("claim_text", ""),
                publisher_name=r.get("publisher_name", ""),
                publisher_site=r.get("publisher_site", ""),
                rating=r.get("rating", ""),
                url=r.get("url", ""),
                title=r.get("title", ""),
            )
            for r in gfc_reviews[:3]
        ]

        claim_results.append(
            ClaimResult(
                claim=claim_text,
                verdict=Verdict(verdict_str),
                confidence=claim_credibility,
                evidence=[e.get("text", "")[:200] for e in evidence[:3]],
                matched_misinfo=misinfo[0]["original_claim"] if misinfo else None,
                source_scores=source_scores,
                external_factchecks=external_fc,
            )
        )

    log.append(f"Qdrant verified_facts: {len(all_evidence)} hit(s)")
    log.append(f"Qdrant misinfo_patterns: {len(all_misinfo)} match(es) above threshold")
    log.append(f"Qdrant source_credibility: {len(all_sources)} source(s) matched")
    log.append(f"Google Fact Check: {len(all_external)} external review(s)")

    qdrant_stats = [
        QdrantStats(
            collection="verified_facts",
            hits=len(all_evidence),
            top_score=max((e["relevance_score"] for e in all_evidence), default=0.0),
        ),
        QdrantStats(
            collection="misinfo_patterns",
            hits=len(all_misinfo),
            top_score=max((m["similarity"] for m in all_misinfo), default=0.0),
        ),
        QdrantStats(
            collection="source_credibility",
            hits=len(all_sources),
            top_score=max((s["similarity"] for s in all_sources), default=0.0),
        ),
    ]

    news_query = text_content[:200] if text_content and not text_content.startswith("(") else ""
    news_articles_raw = search_news(news_query, language, max_results=5) if news_query else []
    news_articles = [
        NewsArticle(
            title=a.get("title", ""),
            source=a.get("source", ""),
            url=a.get("url", ""),
            description=a.get("description", ""),
            published_at=a.get("published_at", ""),
        )
        for a in news_articles_raw
    ]
    log.append(f"News API: {len(news_articles)} article(s) retrieved")

    avg_evidence = (
        sum(e["relevance_score"] for e in all_evidence) / len(all_evidence)
        if all_evidence else 0.0
    )
    avg_misinfo = max((m["similarity"] for m in all_misinfo), default=0.0)
    avg_source, _ = get_source_credibility(qdrant, text_content[:200], top_k=3)
    avg_gfc = google_reviews_to_score(all_external)

    overall_credibility, breakdown = compute_credibility(
        ai_generation_score=ai_gen_score,
        fact_evidence_score=avg_evidence,
        source_credibility_score=avg_source,
        misinfo_pattern_score=avg_misinfo,
        emotional_language_score=emotional_score,
        google_factcheck_score=avg_gfc,
    )

    overall_verdict = Verdict(score_to_verdict(overall_credibility))

    signal_verdict_reason = build_verdict_reason(
        score=overall_credibility,
        verdict=overall_verdict.value,
        breakdown=breakdown,
        misinfo_count=len(all_misinfo),
        external_count=len(all_external),
        evidence_count=len(all_evidence),
    )
    log.append(f"Final credibility: {overall_credibility:.1%} -> {overall_verdict.value}")
    log.append(f"Verdict reason: {signal_verdict_reason}")

    top_external = [
        ExternalFactCheck(
            claim_text=r.get("claim_text", ""),
            publisher_name=r.get("publisher_name", ""),
            publisher_site=r.get("publisher_site", ""),
            rating=r.get("rating", ""),
            url=r.get("url", ""),
            title=r.get("title", ""),
        )
        for r in all_external[:5]
    ]

    explanation_result = _safe_generate_explanation(
        content=text_content,
        claims=[c.claim for c in claim_results],
        credibility_score=overall_credibility,
        verdict=overall_verdict.value,
        evidence=all_evidence[:5],
        misinfo_matches=all_misinfo[:3],
        source_credibility=avg_source,
        language=language,
        external_reviews=all_external[:3],
    )

    llm_verdict_reason = explanation_result.get("verdict_reason", "")
    final_verdict_reason = llm_verdict_reason if llm_verdict_reason else signal_verdict_reason

    return AnalysisResponse(
        credibility_score=round(overall_credibility, 3),
        verdict=overall_verdict,
        verdict_reason=final_verdict_reason,
        detected_language=language,
        detection_method=detection_method,
        claims=claim_results,
        breakdown=breakdown,
        explanation=explanation_result["explanation"],
        counter_content=explanation_result["counter_content"],
        shareable_summary=explanation_result["shareable_summary"],
        image_analysis=image_result,
        audio_analysis=audio_result,
        video_analysis=video_result,
        news_articles=news_articles,
        external_factchecks=top_external,
        processing_log=log,
        qdrant_stats=qdrant_stats,
    )


def _sanitize_input(content: str, content_type: ContentType) -> str:
    if content_type in (ContentType.IMAGE, ContentType.AUDIO, ContentType.VIDEO):
        return ""
    text = content.strip()
    if len(text) > MAX_CONTENT_LENGTH:
        text = text[:MAX_CONTENT_LENGTH]
    return text


def _safe_extract_claims(text: str) -> list[str]:
    try:
        claims = extract_claims(text)
        if not claims:
            return [text[:500]]
        return claims[:MAX_CLAIMS]
    except Exception as e:
        logger.error("Claim extraction error: %s", e)
        return [text[:500]]


def _safe_propaganda_analysis(text: str, language: str) -> dict:
    try:
        return analyze_propaganda(text, language)
    except Exception as e:
        logger.error("Propaganda analysis error: %s", e)
        return {
            "emotional_score": 0.5,
            "propaganda_techniques": [],
            "misleading_patterns": [],
            "sensationalism_score": 0.5,
        }


def _safe_generate_explanation(
    content: str,
    claims: list[str],
    credibility_score: float,
    verdict: str,
    evidence: list[dict],
    misinfo_matches: list[dict],
    source_credibility: float,
    language: str,
    external_reviews: list[dict],
) -> dict:
    try:
        return generate_explanation(
            content=content,
            claims=claims,
            credibility_score=credibility_score,
            verdict=verdict,
            evidence=evidence,
            misinfo_matches=misinfo_matches,
            source_credibility=source_credibility,
            language=language,
            external_reviews=external_reviews,
        )
    except Exception as e:
        logger.error("Explanation generation error: %s", e)
        return {
            "explanation": f"Credibility score: {credibility_score:.0%}. Verdict: {verdict}.",
            "counter_content": "Counter-content generation unavailable.",
            "shareable_summary": f"SatyaNet: {verdict} ({credibility_score:.0%} credibility)",
        }


def _empty_response(msg: str) -> AnalysisResponse:
    return AnalysisResponse(
        credibility_score=0.5,
        verdict=Verdict.UNVERIFIED,
        verdict_reason=msg,
        detected_language="en",
        detection_method="default",
        claims=[],
        breakdown=CredibilityBreakdown(
            ai_generation_score=0.0,
            fact_evidence_score=0.0,
            source_credibility_score=0.5,
            misinfo_pattern_score=0.0,
            emotional_language_score=0.0,
            google_factcheck_score=0.5,
        ),
        explanation=msg,
        counter_content="",
        shareable_summary=msg,
        image_analysis=None,
        audio_analysis=None,
        video_analysis=None,
        news_articles=[],
        external_factchecks=[],
        processing_log=[msg],
        qdrant_stats=[],
    )
