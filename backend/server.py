"""
CivicLens backend — chains the extraction, report, and campaign agents.

Run with:
    uvicorn server:app --reload --port 8000

Endpoints:
    POST /api/analyze   -> runs the extraction agent on the sample zoning doc,
                           returns a list of structured clause records
    POST /api/report     -> body: {"clause": {...}} -> runs the report agent
    POST /api/campaign   -> body: {"clause": {...}, "report": {...}} -> runs
                           the campaign agent
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from agents.extraction_agent import extract_clauses
from agents.report_agent import draft_report
from agents.campaign_agent import draft_campaign

app = FastAPI(title="CivicLens Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo scope only — lock this down for real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_DOC_PATH = Path(__file__).parent / "sample_data" / "zoning_sample.txt"


class ReportRequest(BaseModel):
    clause: dict


class CampaignRequest(BaseModel):
    clause: dict
    report: dict


@app.post("/api/analyze")
def analyze():
    """Runs the ingestion + extraction agent step on the sample zoning document."""
    if not SAMPLE_DOC_PATH.exists():
        raise HTTPException(status_code=500, detail="Sample document not found.")

    document_text = SAMPLE_DOC_PATH.read_text()

    try:
        records = extract_clauses(document_text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Extraction agent failed: {exc}")

    return {"records": records}


@app.post("/api/report")
def report(req: ReportRequest):
    """Runs the report agent on a single clause record."""
    document_text = SAMPLE_DOC_PATH.read_text() if SAMPLE_DOC_PATH.exists() else ""

    try:
        result = draft_report(req.clause, source_context=document_text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Report agent failed: {exc}")

    return result


@app.post("/api/campaign")
def campaign(req: CampaignRequest):
    """Runs the campaign agent on a clause + its already-drafted report."""
    try:
        result = draft_campaign(req.clause, req.report)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Campaign agent failed: {exc}")

    return result


@app.get("/api/health")
def health():
    return {"status": "ok", "groq_key_configured": bool(os.environ.get("GROQ_API_KEY"))}
