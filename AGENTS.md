# SatyaNet-AI — Agent Instructions

## Project Context
AI-powered misinformation detection and counter-response system by Team Arize.
Supports English, Hindi, Tamil. Multi-modal: text, image, audio, video, URL.
Uses Qdrant Cloud for RAG, Azure OpenAI GPT-4o, Google Fact Check API, News API, Azure Translator, FastAPI backend, Next.js frontend.

## Workflow Orchestration

### 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management
- Plan First: Write plan to `tasks/todo.md` with checkable items
- Verify Plan: Check in before starting implementation
- Track Progress: Mark items complete as you go
- Explain Changes: High-level summary at each step
- Document Results: Add review section to `tasks/todo.md`
- Capture Lessons: Update `tasks/lessons.md` after corrections

## Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Architecture Rules

### Backend
- Python 3.11+ / FastAPI in `backend/`
- Venv at `.venv/` (root level)
- Config via pydantic-settings, .env at repo root
- All services in `backend/app/services/`, routers in `backend/app/routers/`

### Qdrant
- **Use Qdrant Cloud** — URL and API key in `.env`
- Three collections: `verified_facts`, `misinfo_patterns`, `source_credibility`
- Always use payload filtering (language, category) for efficient queries
- Embeddings via FastEmbed `paraphrase-multilingual-MiniLM-L12-v2` (384 dims, cosine)

### Google Fact Check Tools API
- Integrated as `google_factcheck.py` service -- searches external fact-checkers globally
- Contributes 25% weight to credibility score via `google_factcheck_score`
- Returns structured `ExternalFactCheck` objects with publisher, rating, URL
- If Google says "False", it can override the score-based verdict
- Graceful degradation: empty list returned on API failure

### News API
- Integrated as `news_api.py` service -- fetches live news articles as corroborating evidence
- Searches newsapi.org/v2/everything with claim text, returns title/source/url/description
- Articles displayed in a dedicated NewsArticles component on the frontend
- Graceful degradation: empty list on API failure

### Image Analysis (GPT-4o Vision)
- `image_analyzer.py` uses GPT-4o Vision as primary analysis with heuristic fallback
- Vision API provides: AI generation detection, manipulation detection, OCR (text extraction), image description, content concerns, context flags
- Extracted text from images feeds into the claim verification pipeline (Qdrant RAG + Google Fact Check)
- For a real photo: correctly identifies as authentic with high confidence
- For AI-generated images: detects synthetic characteristics
- Heuristic fallback: noise uniformity, symmetry, frequency analysis when Vision API unavailable

### Audio & Video Analysis
- `audio_analyzer.py` -- Spectral flatness, temporal consistency, silence ratio heuristics for voice clone detection
- `video_analyzer.py` -- Block-level noise variance for deepfake frame analysis
- Both return structured result models (`AudioAnalysisResult`, `VideoAnalysisResult`)
- File upload via `POST /analyze/upload` (multipart form data)

### Frontend
- Next.js 14 + Tailwind CSS in `frontend/`
- framer-motion for all animations
- Glass-morphism design with dark theme (bg: #07080a)
- All components in `frontend/src/components/`
- 5 input modes: Text, Image, Audio, Video, URL
- Media uploads via file picker with drag-to-upload zone

### Multilingual
- Azure Translator as primary language detection (fallback: langdetect)
- GPT-4o generates explanations in detected language
- Seed data exists in EN, HI, TA

## Special Notes
- Qdrant special prizes: demonstrate deep integration (payload indexes, filtered search, multi-collection queries)
- The "twist" is the Response Layer: explain WHY content is fake + provide verified alternatives
- Frontend should feel like an award-winning site: subtle animations, glass effects, microinteractions
