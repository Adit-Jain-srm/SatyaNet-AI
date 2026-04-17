"""Web search fact verification via Bright Data SERP API + GPT-4o analysis."""

import json
import logging
import re
from typing import Optional

import httpx
from openai import AzureOpenAI

from app.config import settings
from app.services.retry_utils import retry_call

logger = logging.getLogger(__name__)

BRIGHTDATA_ENDPOINT = "https://api.brightdata.com/request"


def search_web(claim: str, num_results: int = 5) -> Optional[dict]:
    """
    Search the web for a claim using Bright Data SERP API.
    Returns raw HTML body for GPT-4o analysis.
    
    Returns:
        {
            "query": claim,
            "status": "success" | "no_results",
            "results_html": HTML string,
        }
    """
    logger.info(f"search_web called for: {claim[:50]}")
    logger.info(f"Credentials check: token={bool(settings.brightdata_api_token)}, zone={bool(settings.brightdata_serp_zone)}")
    
    if not settings.brightdata_api_token or not settings.brightdata_serp_zone:
        logger.warning("Bright Data credentials not configured; skipping web search")
        return None

    try:
        google_url = f"https://www.google.com/search?q={claim.replace(' ', '+')}"
        logger.info(f"Making Bright Data request for: {claim}")
        
        resp = retry_call(
            lambda: httpx.post(
                BRIGHTDATA_ENDPOINT,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.brightdata_api_token}",
                },
                json={
                    "zone": settings.brightdata_serp_zone,
                    "url": google_url,
                    "format": "json",
                },
                timeout=settings.external_http_timeout_seconds,
            ),
            attempts=settings.external_http_retries,
        )

        if resp.status_code != 200:
            logger.error(f"Bright Data API returned {resp.status_code}")
            return None

        response_data = resp.json()
        logger.info(f"Bright Data response received")
        
        # Extract raw HTML body (Google search page)
        html_body = response_data.get("body", "")
        if isinstance(html_body, str) and len(html_body) > 100:
            logger.info(f"HTML response received ({len(html_body)} chars)")
            return {
                "query": claim,
                "status": "success",
                "results_html": html_body,
            }
        else:
            logger.warning("Empty or invalid response body from Bright Data")
            return None

    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return None




def verify_claim_via_web(claim: str, language: str = "en") -> Optional[dict]:
    """
    End-to-end web verification: search + analyze with GPT-4o.
    
    Returns structured evidence dict with:
    - web_verified: bool
    - web_confidence: 0-1
    - web_evidence_text: str
    - web_source_urls: [str]
    - collection: "web_search"
    """
    search_results = search_web(claim, num_results=5)
    if not search_results:
        logger.info(f"No search results for claim: {claim}")
        return None

    # Use GPT-4o to analyze the search results and extract facts
    analysis = _analyze_web_results_with_gpt(claim, search_results)
    if not analysis:
        logger.info(f"GPT analysis failed for claim: {claim}")
        return None

    # Convert to evidence format compatible with credibility scorer
    return {
        "web_verified": analysis.get("verified", False),
        "web_confidence": analysis.get("confidence", 0.0),
        "web_evidence_text": analysis.get("evidence_summary", ""),
        "web_extracted_answer": analysis.get("extracted_answer", ""),
        "web_source_urls": analysis.get("source_urls", []),
        "web_reasoning": analysis.get("reasoning", ""),
        "collection": "web_search",
        "relevance_score": analysis.get("confidence", 0.0),
    }


def _analyze_web_results_with_gpt(claim: str, search_results: dict) -> Optional[dict]:
    """
    Use GPT-4o to directly analyze web search HTML and extract verification information.
    First extract readable text content from HTML, then analyze.
    """
    try:
        html_body = search_results.get("results_html", "")
        if not html_body:
            logger.warning("No HTML body available for GPT analysis")
            return None

        # Extract readable text from HTML
        readable_text = _extract_readable_text_from_html(html_body)
        if not readable_text or len(readable_text) < 100:
            logger.warning(f"Could not extract readable text from HTML (got {len(readable_text)} chars)")
            return None

        # Limit to first 3000 chars to avoid token limits
        text_preview = readable_text[:3000]
        logger.info(f"Extracted {len(readable_text)} chars of readable text, using first 3000")

        client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )

        prompt = f"""You are a fact verification expert. Analyze the Google search results text and verify the claim.

CLAIM: "{claim}"

GOOGLE SEARCH RESULTS TEXT:
{text_preview}

Based on the search results visible above:
1. Is the claim verified/supported by these results? (true/false)
2. What key fact from the results supports or contradicts the claim?
3. How confident are you (0-100)? Be confident if:
   - Multiple sources consistently confirm the claim
   - Authoritative sources (Wikipedia, news, official) are mentioned
   - The claim is directly stated in the results

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "verified": true,
    "confidence": 85,
    "extracted_answer": "short answer from results",
    "evidence_summary": "brief summary of evidence",
    "source_urls": ["google.com", "wikipedia.org"],
    "reasoning": "why you are confident"
}}"""

        response = retry_call(
            lambda: client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},
                timeout=settings.openai_timeout_seconds,
            ),
            attempts=settings.openai_retries,
        )

        result_text = response.choices[0].message.content
        logger.debug(f"GPT response: {result_text[:200]}")
        
        result = json.loads(result_text)

        # Normalize confidence to 0-1
        result["confidence"] = min(100, max(0, result.get("confidence", 50))) / 100.0
        
        logger.info(f"GPT web analysis: verified={result.get('verified')}, confidence={result['confidence']:.2f}")
        return result

    except Exception as e:
        logger.warning(f"GPT web analysis failed: {e}")
        return None


def _extract_readable_text_from_html(html: str) -> str:
    """
    Extract readable text content from Google search HTML.
    Removes script/style tags and extracts visible text.
    """
    try:
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags but keep newlines
        html = re.sub(r'<[^>]+>', '\n', html)
        
        # Decode HTML entities
        html = html.replace('&quot;', '"')
        html = html.replace('&amp;', '&')
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&nbsp;', ' ')
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in html.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        # Keep only the first reasonable portion (search results are at the top)
        # Take first 4000 chars which should contain multiple search results
        return text[:4000]
        
    except Exception as e:
        logger.error(f"Failed to extract readable text: {e}")
        return ""
