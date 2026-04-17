# SatyaNet-AI

**AI-Powered Misinformation Detection & Counter-Response System**

SatyaNet ("Satya" = Truth in Sanskrit) is a multi-modal, multilingual system that detects, explains, and counters misinformation in real time. It goes beyond passive detection to actively build trust — telling users *why* something is likely false and providing *verified alternative information*.

Built by Team Arize.

---

## Key Features

- **Three-Layer Pipeline** — Detection → Understanding → Response (not just "fake or real")
- **Multilingual** — English, Hindi (हिन्दी), Tamil (தமிழ்) with automatic language detection
- **Multi-Modal** — Text analysis and image deepfake/AI-generation detection
- **RAG Fact-Checking** — Retrieval-Augmented Generation powered by Qdrant vector search against verified facts
- **Credibility Scoring** — Weighted multi-signal score (0-100) with transparent breakdown
- **Explainability** — "Why this might be fake" structured explanations in the user's language
- **Counter-Content Generation** — Verified alternative information with citations, shareable summaries
- **WhatsApp-Ready** — Copy-paste shareable fact-check cards

---

## Architecture

```
User Input (Text / Image)
       │
       ▼
┌──────────────────────┐
│   Language Detection  │  (langdetect)
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Pipeline Orchestrator│
└──┬───────────┬───────┘
   │           │
   ▼           ▼
Text Pipeline  Image Pipeline
   │           │
   ▼           ▼
Claim Extraction (GPT-4o)    Deepfake Detection
   │
   ▼
┌──────────────────────────────────────┐
│  Qdrant RAG Fact Retrieval           │
│  ┌──────────────┐ ┌───────────────┐  │
│  │verified_facts│ │misinfo_patterns│  │
│  └──────────────┘ └───────────────┘  │
│  ┌──────────────────┐                │
│  │source_credibility│                │
│  └──────────────────┘                │
└──────────────┬───────────────────────┘
               ▼
     Credibility Scoring
               │
               ▼
   Explanation + Counter-Content (GPT-4o)
               │
               ▼
        Dashboard / API
```

## Tech Stack

| Layer        | Technology                                            |
| ------------ | ----------------------------------------------------- |
| Backend      | Python 3.11, FastAPI                                  |
| Frontend     | Next.js 14, Tailwind CSS, TypeScript                  |
| Vector DB    | **Qdrant** (3 collections, payload indexing, filtered semantic search) |
| Embeddings   | `paraphrase-multilingual-MiniLM-L12-v2` via FastEmbed |
| LLM          | Azure OpenAI GPT-4o                                   |
| Containers   | Docker Compose                                        |

---

## Qdrant Integration (Deep)

Qdrant serves as the **central knowledge backbone** with three purpose-built collections:

### Collections

1. **`verified_facts`** — Verified news, government announcements, WHO data
   - Payload: `text, source, url, language, category, credibility_score`
   - Indexed on: `language`, `category`, `source`

2. **`misinfo_patterns`** — Known debunked misinformation
   - Payload: `original_claim, debunk_summary, verdict, language, spread_count`
   - Indexed on: `language`, `verdict`

3. **`source_credibility`** — Domain/source trust ratings
   - Payload: `domain, trust_score, category`
   - Indexed on: `category`

### Features Used

- Cosine similarity search for semantic claim matching
- Payload filtering (search within language, category)
- Payload indexing for fast filtered queries
- Batch upsert for data ingestion
- Score thresholding to separate high-confidence matches from noise
- Multi-collection querying for comprehensive credibility scoring

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Azure OpenAI API key (GPT-4o deployment)

### 1. Clone & Configure

```bash
git clone https://github.com/Adit-Jain-srm/SatyaNet-AI.git
cd SatyaNet-AI
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

### 2. Start Services

```bash
docker compose up --build
```

This starts:
- **Qdrant** on `http://localhost:6333` (dashboard at `/dashboard`)
- **Backend API** on `http://localhost:8000` (docs at `/docs`)
- **Frontend** on `http://localhost:3000`

### 3. Seed the Database

```bash
curl -X POST http://localhost:8000/ingest/seed
```

This loads verified facts, misinformation patterns, and source credibility data into Qdrant.

### 4. Analyze Content

Open `http://localhost:3000` and paste text or upload an image. Try the built-in examples in English, Hindi, and Tamil.

---

## API Reference

### `POST /analyze`

Analyze content for misinformation.

```json
{
  "content": "Government has banned all UPI transactions!",
  "content_type": "text",
  "language": null
}
```

Response includes: `credibility_score`, `verdict`, `claims[]`, `breakdown`, `explanation`, `counter_content`, `shareable_summary`.

### `POST /ingest`

Bulk ingest verified facts, misinfo patterns, and source ratings.

### `POST /ingest/seed`

Load seed data from `data/*.json` files.

### `GET /health`

Health check with Qdrant connectivity status.

---

## Local Development (Without Docker)

```bash
# Terminal 1: Qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Terminal 2: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

---

## Seed Data

Pre-loaded with India-centric verified facts and misinformation patterns covering:

- **Finance**: UPI, cryptocurrency, RBI policies
- **Health**: COVID-19, vaccines, 5G conspiracy theories
- **Politics**: EVM integrity, Aadhaar, CAA
- **Scams**: WhatsApp free laptop/phone scams
- **Science**: ISRO missions

All data available in English, Hindi, and Tamil.

Source credibility ratings for 25+ domains including government (.gov.in), fact-checkers (AltNews, BoomLive), major news outlets, and social media platforms.

---

## How the Credibility Score Works

The credibility score (0.0 - 1.0) is a weighted combination of five signals:

| Signal                  | Weight | Description                                    |
| ----------------------- | ------ | ---------------------------------------------- |
| AI Generation           | 15%    | Probability content is AI-generated (inverted)  |
| Fact Evidence           | 30%    | How well claims match verified evidence (Qdrant)|
| Source Credibility      | 20%    | Trust rating of the source domain (Qdrant)      |
| Misinfo Pattern Match   | 20%    | Similarity to known misinformation (inverted)   |
| Emotional Language      | 15%    | Propaganda/sensationalism level (inverted)      |

Scores above 0.75 = **Verified True**, 0.50-0.75 = **Unverified**, 0.25-0.50 = **Misleading**, below 0.25 = **Likely False**.

---

## Project Structure

```
SatyaNet-AI/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Environment settings
│   │   ├── routers/
│   │   │   ├── analyze.py          # POST /analyze
│   │   │   ├── health.py           # GET /health
│   │   │   └── ingest.py           # POST /ingest, /ingest/seed
│   │   ├── services/
│   │   │   ├── orchestrator.py     # Pipeline orchestrator
│   │   │   ├── language_detector.py
│   │   │   ├── claim_extractor.py  # GPT-4o claim extraction
│   │   │   ├── fact_retriever.py   # Qdrant RAG engine
│   │   │   ├── credibility_scorer.py
│   │   │   ├── explanation_engine.py
│   │   │   ├── image_analyzer.py
│   │   │   └── embedder.py         # FastEmbed multilingual
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   └── qdrant/
│   │       ├── client.py           # Qdrant client singleton
│   │       ├── collections.py      # Collection + index setup
│   │       └── ingest.py           # Data ingestion
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # Main dashboard
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── AnalysisForm.tsx
│   │   │   ├── CredibilityGauge.tsx
│   │   │   ├── ExplanationCard.tsx
│   │   │   ├── CounterContent.tsx
│   │   │   ├── BreakdownChart.tsx
│   │   │   ├── ClaimCard.tsx
│   │   │   ├── VerdictBadge.tsx
│   │   │   ├── LanguageBadge.tsx
│   │   │   └── ImageAnalysis.tsx
│   │   └── lib/
│   │       ├── api.ts
│   │       └── utils.ts
│   ├── package.json
│   └── Dockerfile
├── data/
│   ├── seed_facts.json
│   ├── misinfo_patterns.json
│   └── source_credibility.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Evaluation Criteria Mapping

| Criterion        | Implementation                                                   |
| ---------------- | ---------------------------------------------------------------- |
| AI Depth         | RAG + LLM reasoning, multi-signal credibility scoring, image analysis, multilingual embeddings |
| Originality      | Three-layer architecture (detect → explain → counter), credibility breakdown transparency, shareable cards |
| Usability        | Modern dashboard, one-click examples, copy-paste shareable summaries, automatic language detection |
| Scalability      | Docker Compose, async FastAPI, Qdrant vector indexing with payload filters, stateless services |
| Documentation    | Comprehensive README, API docs (FastAPI /docs), architecture diagrams, seed data documentation |

---

## Team

Built by **Team Arize**.

## License

MIT
