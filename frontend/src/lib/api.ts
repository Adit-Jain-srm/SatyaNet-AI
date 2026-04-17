const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SourceScore {
  source: string;
  url: string;
  relevance: number;
  credibility: number;
}

export interface ExternalFactCheck {
  claim_text: string;
  publisher_name: string;
  publisher_site: string;
  rating: string;
  url: string;
  title: string;
}

export interface ClaimResult {
  claim: string;
  verdict: "true" | "false" | "misleading" | "unverified";
  confidence: number;
  evidence: string[];
  matched_misinfo: string | null;
  source_scores: SourceScore[];
  external_factchecks: ExternalFactCheck[];
}

export interface CredibilityBreakdown {
  ai_generation_score: number;
  web_search_score: number;
  fact_evidence_score: number;
  source_credibility_score: number;
  misinfo_pattern_score: number;
  emotional_language_score: number;
  google_factcheck_score: number;
}

export interface ImageAnalysisResult {
  is_ai_generated: boolean;
  ai_probability: number;
  is_manipulated: boolean;
  manipulation_probability: number;
  similar_verified_images: string[];
  description: string;
  ai_reasoning: string;
  manipulation_reasoning: string;
  extracted_text: string;
  text_claims: string[];
  content_concerns: string[];
  is_real_photo: boolean;
  context_flags: string[];
  analysis_method: string;
}

export interface AudioAnalysisResult {
  is_voice_clone: boolean;
  clone_probability: number;
  spectral_anomaly_score: number;
  temporal_consistency: number;
  duration_seconds: number;
}

export interface VideoAnalysisResult {
  is_deepfake: boolean;
  deepfake_probability: number;
  face_swap_detected: boolean;
  lip_sync_score: number;
  temporal_consistency: number;
  frame_count_analyzed: number;
  duration_seconds: number;
}

export interface NewsArticle {
  title: string;
  source: string;
  url: string;
  description: string;
  published_at: string;
}

export interface QdrantStats {
  collection: string;
  hits: number;
  top_score: number;
}

export interface AnalysisResponse {
  credibility_score: number;
  verdict: "true" | "false" | "misleading" | "unverified";
  verdict_reason: string;
  detected_language: string;
  detection_method: string;
  claims: ClaimResult[];
  breakdown: CredibilityBreakdown;
  explanation: string;
  counter_content: string;
  shareable_summary: string;
  image_analysis: ImageAnalysisResult | null;
  audio_analysis: AudioAnalysisResult | null;
  video_analysis: VideoAnalysisResult | null;
  external_factchecks: ExternalFactCheck[];
  news_articles: NewsArticle[];
  processing_log: string[];
  qdrant_stats: QdrantStats[];
}

export interface AnalysisRequest {
  content: string;
  content_type: "text" | "image" | "url" | "audio" | "video";
  language?: string;
}

export async function analyzeContent(
  request: AnalysisRequest
): Promise<AnalysisResponse> {
  const res = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Analysis failed: ${error}`);
  }
  return res.json();
}

export async function analyzeFile(
  file: File,
  contentType: string
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("content_type", contentType);
  const res = await fetch(`${API_URL}/analyze/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Analysis failed: ${error}`);
  }
  return res.json();
}

export async function seedDatabase(): Promise<{ seeded: Record<string, number> }> {
  const res = await fetch(`${API_URL}/ingest/seed`, { method: "POST" });
  if (!res.ok) throw new Error("Seeding failed");
  return res.json();
}

export async function checkHealth(): Promise<{
  status: string;
  qdrant_connected: boolean;
  collections: string[];
}> {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}
