from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    URL = "url"
    AUDIO = "audio"
    VIDEO = "video"


class Verdict(str, Enum):
    TRUE = "true"
    FALSE = "false"
    MISLEADING = "misleading"
    UNVERIFIED = "unverified"


class AnalysisRequest(BaseModel):
    content: str = Field(..., description="Text content, URL, or base64 image")
    content_type: ContentType = ContentType.TEXT
    language: Optional[str] = Field(None, description="ISO language code override")


class ExternalFactCheck(BaseModel):
    claim_text: str = ""
    publisher_name: str = ""
    publisher_site: str = ""
    rating: str = ""
    url: str = ""
    title: str = ""


class ClaimResult(BaseModel):
    claim: str
    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    matched_misinfo: Optional[str] = None
    source_scores: list[SourceScore] = Field(default_factory=list)
    external_factchecks: list[ExternalFactCheck] = Field(default_factory=list)


class SourceScore(BaseModel):
    source: str
    url: str
    relevance: float = Field(ge=0.0, le=1.0)
    credibility: float = Field(ge=0.0, le=1.0)


class CredibilityBreakdown(BaseModel):
    ai_generation_score: float = Field(ge=0.0, le=1.0, description="Probability content is AI-generated")
    fact_evidence_score: float = Field(ge=0.0, le=1.0, description="How well facts match verified evidence")
    source_credibility_score: float = Field(ge=0.0, le=1.0, description="Trustworthiness of source")
    misinfo_pattern_score: float = Field(ge=0.0, le=1.0, description="Match against known misinfo patterns")
    emotional_language_score: float = Field(ge=0.0, le=1.0, description="Propaganda / emotional language level")
    google_factcheck_score: float = Field(0.5, ge=0.0, le=1.0, description="Google Fact Check Tools API signal")


class AudioAnalysisResult(BaseModel):
    is_voice_clone: bool
    clone_probability: float = Field(ge=0.0, le=1.0)
    spectral_anomaly_score: float = Field(ge=0.0, le=1.0)
    temporal_consistency: float = Field(ge=0.0, le=1.0)
    duration_seconds: float = 0.0


class VideoAnalysisResult(BaseModel):
    is_deepfake: bool
    deepfake_probability: float = Field(ge=0.0, le=1.0)
    face_swap_detected: bool
    lip_sync_score: float = Field(ge=0.0, le=1.0)
    temporal_consistency: float = Field(ge=0.0, le=1.0)
    frame_count_analyzed: int = 0
    duration_seconds: float = 0.0


class NewsArticle(BaseModel):
    title: str
    source: str
    url: str
    description: str = ""
    published_at: str = ""


class QdrantStats(BaseModel):
    collection: str
    hits: int = 0
    top_score: float = 0.0


class AnalysisResponse(BaseModel):
    credibility_score: float = Field(ge=0.0, le=1.0)
    verdict: Verdict
    verdict_reason: str = ""
    detected_language: str
    detection_method: str = "langdetect"
    claims: list[ClaimResult] = Field(default_factory=list)
    breakdown: CredibilityBreakdown
    explanation: str
    counter_content: str
    shareable_summary: str
    image_analysis: Optional[ImageAnalysisResult] = None
    audio_analysis: Optional[AudioAnalysisResult] = None
    video_analysis: Optional[VideoAnalysisResult] = None
    news_articles: list[NewsArticle] = Field(default_factory=list)
    external_factchecks: list[ExternalFactCheck] = Field(default_factory=list)
    processing_log: list[str] = Field(default_factory=list)
    qdrant_stats: list[QdrantStats] = Field(default_factory=list)


class ImageAnalysisResult(BaseModel):
    is_ai_generated: bool
    ai_probability: float = Field(ge=0.0, le=1.0)
    is_manipulated: bool
    manipulation_probability: float = Field(ge=0.0, le=1.0)
    similar_verified_images: list[str] = Field(default_factory=list)
    description: str = ""
    ai_reasoning: str = ""
    manipulation_reasoning: str = ""
    extracted_text: str = ""
    text_claims: list[str] = Field(default_factory=list)
    content_concerns: list[str] = Field(default_factory=list)
    is_real_photo: bool = True
    context_flags: list[str] = Field(default_factory=list)
    analysis_method: str = "heuristic"


class IngestFactRequest(BaseModel):
    text: str
    source: str
    url: str = ""
    language: str = "en"
    category: str = "general"
    credibility_score: float = Field(1.0, ge=0.0, le=1.0)


class IngestMisinfoRequest(BaseModel):
    original_claim: str
    debunk_summary: str
    verdict: Verdict = Verdict.FALSE
    language: str = "en"
    spread_count: int = 0


class IngestSourceRequest(BaseModel):
    domain: str
    trust_score: float = Field(ge=0.0, le=1.0)
    category: str = "news"


class BulkIngestRequest(BaseModel):
    facts: list[IngestFactRequest] = Field(default_factory=list)
    misinfo_patterns: list[IngestMisinfoRequest] = Field(default_factory=list)
    sources: list[IngestSourceRequest] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool
    collections: list[str]


ClaimResult.model_rebuild()
AnalysisResponse.model_rebuild()
AudioAnalysisResult.model_rebuild()
VideoAnalysisResult.model_rebuild()
