# SatyaNet-AI — Lessons Learned

## Session 1

### Lesson: .env path resolution
- **Problem**: pydantic-settings couldn't find `.env` from `backend/` subdirectory
- **Fix**: Use tuple in `model_config`: `("../.env", ".env")` to search parent directory first
- **Rule**: Always test config loading from the working directory where `uvicorn` runs

### Lesson: Dependency version conflicts
- **Problem**: Strict pinned versions (`==`) caused resolution failures (fastembed vs Pillow)
- **Fix**: Use compatible ranges (`>=x.y,<z.0`) instead of strict pins for hackathon projects
- **Rule**: Pin loosely in hackathons, strictly in production

### Lesson: Qdrant Cloud vs Local
- **Problem**: Switching from local Docker Qdrant to Cloud requires API key auth
- **Fix**: Client init checks `if settings.qdrant_api_key` and passes it to `QdrantClient(url=..., api_key=...)`
- **Rule**: Always make auth optional so both local and cloud work from the same code

### Lesson: Azure Translator auth
- **Problem**: Azure Translator key returned 401 across all regions
- **Root cause**: The key may need the resource-specific endpoint (not global) or may not be provisioned yet
- **Fix**: Built graceful fallback — Azure Translator is primary, langdetect is secondary. System works correctly either way.
- **Rule**: Always build services with fallback chains. Never hard-depend on a single external API.

### Lesson: Azure Translator SDK vs REST
- **Problem**: `TextTranslationClient` SDK doesn't have a `detect_language` method
- **Fix**: Use REST API directly (`httpx.post` to `api.cognitive.microsofttranslator.com/detect`)
- **Rule**: Check the actual SDK methods (`dir(Client)`) before writing code. Don't assume method names.

### Lesson: Google Fact Check API integration
- **Key insight**: Google Fact Check Tools API (`/v1alpha1/claims:search`) returns reviews from real fact-checkers (AltNews, Snopes, PolitiFact, etc.)
- **Scoring**: Converted textual ratings ("False", "Misleading", "True") into 0-1 scores using keyword matching
- **Rule**: External APIs like this should override internal heuristics when they have strong signal (consensus "False" from multiple publishers)
- **Edge case**: API may return 0 results for obscure claims -- always have Qdrant RAG as fallback

### Lesson: Edge case handling in analysis pipeline
- **Problem**: Empty strings, special characters, very long inputs could crash the pipeline
- **Fix**: Added `_sanitize_input()`, `_safe_extract_claims()`, `_safe_propaganda_analysis()` wrappers, and `_empty_response()` for blank input
- **Rule**: Every external service call should be wrapped in try/except with sensible defaults

### Lesson: News API integration
- **Value**: Live news article retrieval provides real-time evidence that complements static Qdrant data and Google Fact Check reviews
- **Key decision**: Use `sortBy=relevancy` (not `publishedAt`) to get the most topically relevant articles
- **Rule**: Three evidence sources (Qdrant vectors + Google Fact Check + News API) is stronger than any single source

### Lesson: Multi-modal file uploads
- **Problem**: Audio/video files can't be base64-encoded in JSON requests (too large, binary)
- **Fix**: Added `POST /analyze/upload` endpoint using FastAPI's `UploadFile` + `Form` parameters for multipart uploads
- **Rule**: Always provide both JSON API (for text/small images) and multipart upload (for large media files)

### Lesson: Parallel subagent execution for large features
- **Approach**: Backend services + frontend components built simultaneously by separate subagents
- **Result**: Both completed in parallel, zero merge conflicts because they touch different directories
- **Rule**: When adding a new modality (audio/video), backend service + frontend component + schema changes are independent and can parallelize

### Lesson: Frontend animation library
- **Problem**: CSS-only animations lack interruptibility and stagger control
- **Fix**: Use framer-motion with `layoutId`, `AnimatePresence`, spring physics for premium feel
- **Rule**: For hackathon demos, animations are high-impact low-effort differentiators
