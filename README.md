# SatyaNet-AI

**AI-Powered Misinformation Detection & Counter-Response System**

SatyaNet ("Satya" = Truth in Sanskrit) is a multi-modal, multilingual misinformation detection and counter-response system. It goes beyond passive detection to actively build trust -- telling users *why* something is misleading, providing *verified alternative information*, and explaining the reasoning behind every verdict.

Built by **Team Arize**.

---

## Key Features

- **Three-Layer Pipeline** -- Detection, Understanding, Response (not just a binary true/false label)
- **Multi-Modal** -- Text, image (GPT-4o Vision), audio, video, and URL analysis
- **Multilingual** -- Automatic detection supports any detected language code (Azure Translator + langdetect fallback)
- **RAG Fact-Checking** -- Retrieval-Augmented Generation via Qdrant vector search across 3 collections with payload filtering
- **Live Web Verification** -- Bright Data SERP retrieval + GPT web evidence extraction for time-sensitive claims
- **External Fact-Check Aggregation** -- Google Fact Check Tools API + News API for corroboration
- **GPT Final Judge** -- Final credibility score and verdict come from GPT holistic reasoning (non-weighted in code)
- **Reasoned Verdicts** -- Every verdict includes a human-readable reason citing concrete evidence/signals
- **Explainability** -- Structured "Why This Rating" explanations with chain-of-thought LLM reasoning
- **Counter-Content** -- Verified alternative information with source citations, WhatsApp-shareable summaries
- **Transparency** -- Full pipeline trace showing every step of the analysis process
- **Reliability Hardening** -- Retry + timeout controls across OpenAI, Qdrant, Bright Data, News API, Google Fact Check, and Translator calls

---

## Architecture

```
User Input (Text / Image / Audio / Video / URL)
       |
       v
+---------------------------+
| Input Handler             |
| - URL: fetch article text |
| - Image: GPT-4o Vision   |
| - Audio/Video: heuristics |
+------------+--------------+
             |
             v
+---------------------------+
| Language Detection        |
| Azure Translator -> lang  |
| detect fallback           |
+------------+--------------+
             |
             v
+---------------------------+
| Claim Extraction (GPT-4o) |
| Chain-of-thought prompting |
| + Propaganda Analysis      |
+------------+--------------+
             |
             v
+----------------------------------------------+
| Multi-Source Evidence Retrieval               |
|                                              |
| Qdrant Cloud (3 collections):               |
|   verified_facts    [language-filtered]      |
|   misinfo_patterns  [language-filtered]      |
|   source_credibility [score-thresholded]     |
|                                              |
| + Cross-lingual search (translate -> EN)     |
| + Bright Data web retrieval + GPT extraction |
| + Google Fact Check Tools API                |
| + News API (live articles)                   |
+---------------------+------------------------+
                      |
                      v
+---------------------------+
| Diagnostic Signals        |
| (AI/web/fact/source/      |
| misinfo/emotion/GFC)      |
+------------+--------------+
             |
             v
+---------------------------+
| GPT Final Judge           |
| - credibility_score       |
| - verdict                 |
| - verdict_reason          |
+------------+--------------+
             |
             v
+---------------------------+
| Response Generation       |
| (GPT-4o)                  |
| - Structured explanation  |
| - Counter-content         |
| - WhatsApp summary        |
| - Verdict reason          |
+---------------------------+
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI |
| Frontend | Next.js 14, Tailwind CSS, Framer Motion, TypeScript |
| Vector DB | **Qdrant Cloud** (3 collections, payload indexing, filtered semantic search, score thresholds) |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` via FastEmbed (384 dims, cosine) |
| LLM | Azure OpenAI GPT-4o (text + vision) |
| Fact-Checking | Google Fact Check Tools API |
| News | News API (live article retrieval) |
| Translation | Azure Translator (detection + cross-lingual search) |

---

## Qdrant Integration

Qdrant serves as the **central knowledge backbone** with three purpose-built collections, all using payload-indexed filtered vector search:

### Collections

| Collection | Purpose | Payload Indexes | Query Features |
|-----------|---------|----------------|---------------|
| `verified_facts` | Verified news, government data, WHO facts | `language`, `category`, `source` | Language-filtered search (user lang OR English), score threshold 0.25 |
| `misinfo_patterns` | Known debunked misinformation | `language`, `verdict` | Language-filtered search, client-side similarity threshold 0.65 |
| `source_credibility` | Domain/source trust ratings | `category` | Score threshold 0.3, similarity-weighted trust averaging |

### Features Used

- Cosine similarity search with `paraphrase-multilingual-MiniLM-L12-v2` embeddings
- Payload filtering (`language`, `category`) on every query
- Payload indexing (KEYWORD type) for fast filtered search
- Server-side `score_threshold` to eliminate low-quality matches
- Batch upsert for bulk data ingestion
- Multi-collection querying (3 parallel searches per claim)
- Cross-lingual search: non-English claims are translated to English and searched again, results merged and deduplicated
- Configurable timeout + retry behavior to reduce transient network failures

---

## Credibility Decisioning

SatyaNet now uses a two-stage decision strategy:

1. **Diagnostic signal layer** computes evidence/safety signals for transparency:
   - AI generation score
   - Web search verification score
   - Fact evidence score
   - Source credibility score
   - Misinfo pattern score
   - Emotional language score
   - Google fact-check score

2. **GPT final judge layer** receives these signals + raw evidence and produces:
   - `credibility_score` (0-1)
   - `verdict` (`true|false|misleading|unverified`)
   - `verdict_reason`

This avoids hardcoded final weighting while still exposing full signal breakdown for auditability.

---

## Bias & Hallucination Controls (Layer-wise)

### Layer 1 — Input & Detection Guardrails
- Normalize and bound input length per modality to reduce prompt injection surface.
- Detect language first, then keep prompts and outputs in detected language to reduce translation drift.

### Layer 2 — Evidence Grounding
- Retrieve from three Qdrant collections with payload filters and thresholds.
- Merge cross-lingual and English evidence to reduce mono-language bias.
- Add live web corroboration (Bright Data) for current events.
- Pull external fact-check labels and news context before final decision.

### Layer 3 — Decision Controls
- Pass structured evidence and scores to GPT as explicit context.
- Require constrained JSON schema for score/verdict output.
- Fall back to signal-based verdict if final GPT scoring fails.

### Layer 4 — Response Controls
- Generate explanation/counter-content from the same evidence context used for verdicting.
- Include verdict reasons and pipeline logs so users can inspect why a decision was made.
- Return conservative defaults when upstream components fail.

### Layer 5 — Reliability Controls
- Centralized retry/backoff for transient timeout/network errors.
- Configurable timeouts for OpenAI, Qdrant, and external HTTP services.
- Graceful degradation rather than hard failures for optional integrations.

---

## Source Strategy & Citations

SatyaNet intentionally uses multiple source classes to reduce single-source bias:

- **Structured internal retrieval**: `verified_facts`, `misinfo_patterns`, `source_credibility`
- **External fact checks**: Google Fact Check Tools API publishers
- **Live web context**: Bright Data SERP retrieval + GPT extraction
- **News corroboration**: News API
- **Optional authority references in responses**: government portals, institutional sites, and publisher URLs returned from evidence

For production use, maintain a vetted allowlist/weighting policy for high-trust sources (public health agencies, election commissions, central banks, courts, major wire services).

---

## Prompting Strategy

SatyaNet uses advanced prompting techniques across all LLM calls:

### Claim Extraction
- **Chain-of-thought**: Forces step-by-step reasoning (identify language, determine domain, separate facts from opinions)
- **Structured output**: Returns language, domain, claims array, and skipped_reasons
- **Implicit claim extraction**: Catches claims that are implied but not stated directly

### Propaganda Analysis
- **Expert persona**: Trained on Institute for Propaganda Analysis taxonomy
- **Structured evidence**: Each detected technique includes quoted evidence and severity rating
- **Multi-dimensional scoring**: Emotional score + sensationalism score + technique-level breakdown

### Explanation Generation
- **Three-layer context**: System prompt establishes the Response Layer role in the pipeline
- **Evidence grounding**: All Qdrant collection hits, Google reviews, and similarity scores are passed as structured context
- **Step-by-step reasoning**: Prompt asks the LLM to ASSESS, find EVIDENCE, match PATTERNS, identify missing CONTEXT, then generate the verdict reason
- **Multi-output**: Single prompt generates explanation, counter-content, shareable summary, and verdict reason

### Image Analysis (GPT-4o Vision)
- **Forensics expert persona**: Analyzes for AI generation, manipulation, OCR, content concerns, and context flags
- **Structured JSON output**: 12 fields covering every aspect of image authenticity
- **Heuristic fallback**: Pixel-level analysis (noise uniformity, symmetry, frequency) when Vision API is unavailable

---

## Quick Start

### Prerequisites

- Python 3.11+ with venv
- Node.js 18+
- Azure OpenAI API key (GPT-4o deployment)
- Qdrant Cloud account (or local Docker)

### 1. Clone and Configure

```bash
git clone https://github.com/Adit-Jain-srm/SatyaNet-AI.git
cd SatyaNet-AI
cp .env.example .env
# Edit .env with your credentials
```

### 2. Backend

```bash
python -m venv .venv
.venv/Scripts/pip install -r backend/requirements.txt  # Windows
# or: .venv/bin/pip install -r backend/requirements.txt  # Mac/Linux

cd backend
../.venv/Scripts/uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Seed Database

```bash
curl -X POST http://localhost:8000/ingest/seed
```

### 5. Analyze

Open `http://localhost:3000` and try the built-in examples in English, Hindi, and Tamil.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/analyze` | Analyze text/URL content for misinformation |
| `POST` | `/analyze/upload` | Upload image/audio/video files for analysis |
| `POST` | `/ingest` | Bulk ingest facts, misinfo patterns, sources |
| `POST` | `/ingest/seed` | Load seed data from `data/*.json` |
| `GET` | `/health` | Health check with Qdrant connectivity |

Full API documentation available at `http://localhost:8000/docs` (Swagger UI).

---

## Seed Data

Current local datasets (JSON) are larger than the original prototype and include multilingual entries.
At the time of writing:

- `seed_facts.json`: 156 entries
- `misinfo_patterns.json`: 150 entries
- `source_credibility.json`: 171 entries

### Should we delete data if it feels too large?

Not by default. These files are not large enough to require destructive trimming for runtime health.
Instead, prefer:

- deduplicate near-identical entries,
- archive low-quality/outdated records to a separate file,
- maintain a "high-confidence" active subset for strict production mode.

Data quality matters more than raw count. Blind deletion can increase hallucinations by reducing grounding coverage.

Coverage categories include:

- **Finance**: UPI, cryptocurrency, RBI policies
- **Health**: COVID-19, vaccines, 5G conspiracy theories
- **Politics**: EVM integrity, Aadhaar, CAA
- **Scams**: WhatsApp free laptop/phone scams
- **Science**: ISRO missions

All data in English, Hindi, and Tamil.

---

## Monetization Paths

SatyaNet can generate revenue through multiple product models:

1. **B2B API (usage-based)**  
   - Charge per verification call and per premium evidence mode (web + multimodal).

2. **Enterprise Compliance Suite (subscription)**  
   - Dashboard for media houses, election teams, and brands; SLA, audit logs, and governance controls.

3. **Social Platform Moderation Plugin**  
   - Per-seat + throughput pricing for moderation teams and trust & safety operations.

4. **Browser/WhatsApp Fact-Check Assistant (freemium)**  
   - Free basic checks, paid "deep verification" with expanded source coverage and report export.

5. **White-label SDK for Newsrooms/EdTech/Civic Apps**  
   - Annual licensing for branded explainability and counter-content workflows.

6. **Data & Insight Products**  
   - Trend reports on misinformation narratives by region/language/domain (privacy-safe aggregated analytics).

Recommended go-to-market order: **B2B API -> Enterprise dashboard -> Consumer freemium extension**.

---

## Evaluation Criteria Mapping

| Criterion | Implementation |
|-----------|---------------|
| **AI Depth** | GPT-4o Vision for images, chain-of-thought claim extraction, 6-signal credibility engine, RAG with Qdrant, cross-lingual evidence retrieval, propaganda analysis with technique taxonomy |
| **Originality** | Three-layer architecture (detect/understand/respond), verdict reasoning (not just labels), pipeline trace transparency, multi-source evidence fusion (Qdrant + Google FC + News API) |
| **Usability** | 5-modality input (text/image/audio/video/URL), one-click examples in 3 languages, WhatsApp deep-link sharing, loading skeletons, real-time Qdrant health indicator |
| **Scalability** | Qdrant Cloud vector search, async FastAPI, stateless services, Docker Compose, payload-indexed filtered queries |
| **Documentation** | Comprehensive README, API docs (FastAPI /docs), AGENTS.md, lessons.md, pipeline trace in every response |

---

## Team

Built by **Team Arize**.

## License

MIT
