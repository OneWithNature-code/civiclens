# CivicLens — Municipal Policy Intelligence

**Problem statement:** Civic Policy & Municipal Transparency — agents that ingest city
council data dumps, parse zoning laws, and autonomously draft localized impact reports
and citizen response campaigns.

## What this is

CivicLens runs a three-agent pipeline over a real municipal zoning document:

1. **Extraction agent** reads raw zoning/council text and parses it into structured,
   confidence-scored clause records (id, title, affected area, category, plain-language
   summary).
2. **Report agent** takes a single clause and drafts a localized impact report — what
   changes, who's affected, likely effects, and what a human reviewer should verify
   before publishing.
3. **Campaign agent** takes a clause + its report and drafts a citizen response campaign
   kit — talking points, an outreach message draft, and suggested channels — explicitly
   framed as a starting point for human editing, not a final document.

Every one of these is a real LLM call (via Groq), not hardcoded output. The dashboard UI
shows the pipeline running live: ingest → extract → validate → publish, then lets a
human reviewer inspect any extracted clause and trigger the report/campaign agents on
demand.

## Why this design

- **Human-in-the-loop by design, not by accident.** Every agent output is explicitly
  labeled as a draft needing review — this matches how municipal transparency tools
  actually need to work: agents accelerate analysis, humans still decide what goes public.
- **Traceable outputs.** Every clause the extraction agent produces links back to the
  same source document used by the report and campaign agents, so nothing is invented
  independently at each stage.
- **Scoped for a real demo, not a slideware pitch.** Rather than claiming to handle
  "massive city data dumps" with no evidence, this ships one real sample zoning document
  end-to-end through all three agents, so judges can watch it actually work.

## Architecture

```
frontend/index.html          Dashboard UI (vanilla JS, no build step)
        |
        | fetch()
        v
backend/server.py            FastAPI app, 3 endpoints
        |
        +-- agents/extraction_agent.py   raw text -> structured clauses (JSON)
        +-- agents/report_agent.py       clause -> impact report (JSON)
        +-- agents/campaign_agent.py     clause + report -> campaign kit (JSON)
        |
        v
llm_client.py                 Shared wrapper around Groq's chat completions API
        |
        v
sample_data/zoning_sample.txt Sample zoning document (real-style council extract)
```

## Running it

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your free Groq API key (console.groq.com/keys)

uvicorn server:app --reload --port 8000
```

Check it's alive: `curl http://localhost:8000/api/health`

### 2. Frontend

Just open `frontend/index.html` in a browser (or serve it with any static server).
It talks to `http://localhost:8000` by default — override by setting
`window.CIVICLENS_API_BASE` before the script runs if you deploy the backend elsewhere.

### 3. Demo flow

1. Click **Run analysis** — watch the pipeline steps go live and the extraction agent
   populate the review queue and clause table with real parsed output.
2. Click any clause in the queue to inspect it in the detail drawer.
3. Click **Draft impact report** — the report agent generates a real report for that
   clause.
4. Click **Generate resident response campaign** — the campaign agent drafts a kit
   grounded in that clause and report.

## Judging criteria mapping

| Criterion | How this addresses it |
|---|---|
| Problem Understanding & Impact | Pipeline targets the exact workflow named in the brief: ingest → parse zoning law → draft reports/campaigns |
| Agentic AI Implementation | Three chained LLM agents, each with a distinct role, real reasoning over real input, structured outputs |
| Technical Implementation | FastAPI backend, clean agent separation, real API integration, error handling on every endpoint |
| Solution Effectiveness & Usability | One click from raw document to review-ready report and campaign draft |
| Demo & Presentation | Live pipeline visualization makes the agent handoffs visible, not hidden behind a "processing..." spinner |

## Known limitations (be upfront about these if asked)

- Single sample document, not a full ingestion pipeline for arbitrary file formats/scale.
- No persistent database — state lives in the browser session.
- No auth — this is a demo, not a production deployment.
- Sentiment/map panels on the overview page are illustrative rather than derived from the
  agent output (the extraction/report/campaign flow is the real part).
