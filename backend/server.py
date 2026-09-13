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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable connections from your local frontend html page
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "groq_key_configured": bool(os.environ.get("GROQ_API_KEY"))}

@app.post("/api/analyze")
async def analyze_document():
    try:
        from agents.extraction_agent import extract_clauses
        
        # 1. Fallback text representation of the Bangalore zoning framework
        default_zoning_text = """
        REVISED MASTER PLAN FOR BENGALURU 2031 ZONING REGULATIONS
        CHAPTER 4: RESIDENTIAL ZONE REGULATIONS
        Clause 4.1.1: Permissible maximum height in residential mixed zones is set to 42 feet.
        Clause 4.1.2: Minimum road width requirement for high-density commercial construction is 12 meters.
        Clause 4.1.3: Floor Area Ratio (FAR) modifications allow an additional 20% coverage near transit corridors.
        """

        # 2. Try to look up the physical document file if it exists
        sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "zoning_sample.txt")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as file:
                default_zoning_text = file.read()
        elif os.path.exists(os.path.join(os.path.dirname(__file__), "zoning_sample.txt")):
            with open(os.path.join(os.path.dirname(__file__), "zoning_sample.txt"), "r", encoding="utf-8") as file:
                default_zoning_text = file.read()

        # 3. Call the extraction function normally without 'await'
        output_data = extract_clauses(document_text=default_zoning_text)
        
        # 4. Return the data payload directly
        return output_data

    except Exception as e:
        print("⚠️ THE ACTUAL AGENT ERROR IS:", str(e))
        raise HTTPException(status_code=502, detail=str(e))
