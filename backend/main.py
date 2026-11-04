from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agent.orchestrator import analyze_content

app = FastAPI(
    title="CyberEye AI API",
    description="Unified cybersecurity analysis prototype. Baseline checks are not conclusive AI detection.",
    version="0.1.0",
)

# Local development only. Restrict origins before deploying publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AnalysisRequest(BaseModel):
    kind: str = Field(description="One of: url, sms, email, audio, video")
    content: str = Field(default="", max_length=20000)


@app.get("/api/health")
def health():
    return {"status": "ok", "project": "CyberEye AI", "version": "0.1.0"}


@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    return analyze_content(request.kind, request.content)


@app.get("/")
def home():
    from fastapi.responses import FileResponse
    from pathlib import Path
    return FileResponse(Path(__file__).resolve().parent.parent / "frontend" / "index.html")
