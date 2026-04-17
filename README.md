# SatyaNet-AI

**AI-Powered Misinformation Detection & Counter-Response System**

SatyaNet ("Satya" = Truth in Sanskrit) is a multi-modal, multilingual misinformation detection and counter-response system. It goes beyond passive detection to actively build trust -- telling users *why* something is misleading, providing *verified alternative information*, and explaining the reasoning behind every verdict.

Built by **Team Arize**.

---

## Key Features

- **Three-Layer Pipeline** -- Detection, Understanding, Response (not just a binary true/false label)
- **Multi-Modal** -- Text, image (GPT-4o Vision), audio, video, and URL analysis
- **Multilingual** -- English, Hindi, Tamil with automatic language detection (Azure Translator + langdetect fallback)
- **RAG Fact-Checking** -- Retrieval-Augmented Generation via Qdrant vector search across 3 collections with payload filtering
- **External Fact-Check Aggregation** -- Google Fact Check Tools API + News API for live evidence
- **Reasoned Verdicts** -- Every verdict includes a human-readable reason citing specific evidence and signals
- **Explainability** -- Structured "Why This Rating" explanations with chain-of-thought LLM reasoning
- **Counter-Content** -- Verified alternative information with source citations, WhatsApp-shareable summaries
- **Transparency** -- Full pipeline trace showing every step of the analysis process

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
| + Google Fact Check Tools API                |
| + News API (live articles)                   |
+---------------------+------------------------+
                      |
                      v
+---------------------------+
| 6-Signal Credibility      |
| Scoring Engine            |
| + Verdict Reasoning       |
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

---

## Credibility Scoring

The credibility score (0-100) is computed from 6 weighted signals:

| Signal | Weight | Source | Direction |
|--------|--------|--------|-----------|
| AI Generation | 10% | Image/audio analyzers | Lower is better (inverted) |
| Fact Evidence | 20% | Qdrant `verified_facts` | Higher is better |
| Source Credibility | 12% | Qdrant `source_credibility` | Higher is better |
| Misinfo Pattern | 13% | Qdrant `misinfo_patterns` | Lower is better (inverted) |
| Emotional Language | 10% | GPT-4o propaganda analysis | Lower is better (inverted) |
| Google Fact Check | 35% | Google Fact Check Tools API | Higher is better (strongest external signal) |

### Verdict Scale

| Score Range | Verdict | Meaning |
|------------|---------|---------|
| 75-100 | **Verified True** | Strong evidence supports the claims; corroborated by trusted sources |
| 50-74 | **Unverified** | Insufficient evidence to confirm or deny; proceed with caution |
| 30-49 | **Misleading** | Contains factual inaccuracies, missing context, or matches known misinformation patterns |
| 0-29 | **Likely False** | Contradicted by verified evidence; flagged by external fact-checkers |

Every verdict includes a **verdict reason** -- a human-readable sentence explaining *why* that specific verdict was assigned, citing the dominant signals. For example:

> "Rated Misleading because: matches known debunked misinformation (92% similarity); uses highly emotional/propaganda language (85%); source has low credibility rating."

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

20 verified facts + 14 misinformation patterns + 25 source credibility ratings covering:

- **Finance**: UPI, cryptocurrency, RBI policies
- **Health**: COVID-19, vaccines, 5G conspiracy theories
- **Politics**: EVM integrity, Aadhaar, CAA
- **Scams**: WhatsApp free laptop/phone scams
- **Science**: ISRO missions

All data in English, Hindi, and Tamil.

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
