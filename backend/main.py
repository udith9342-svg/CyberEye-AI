from pathlib import Path
import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from backend.agent.orchestrator import analyze_content
from backend.agent.chat_agent import respond_to_message
from backend.agent.tool_registry import list_tools

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="CyberEye AI", description="Unified cybersecurity agent prototype. Only URL and SMS baseline checks are currently implemented.", version="0.2.0")
app.mount("/frontend", StaticFiles(directory=BASE_DIR / "frontend"), name="frontend")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

class AnalysisRequest(BaseModel):
    kind: str = Field(description="One of: url, sms, email, audio, or video")
    content: str = Field(default="", max_length=20000)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)

@app.get("/api/health")
def health():
    return {"status":"ok", "project":"CyberEye AI", "version":"0.2.0"}

@app.get("/api/capabilities")
def capabilities():
    return {"agent":{"available":True,"llm_configured":bool(os.getenv("OPENAI_API_KEY"))},
            "tools":list_tools(),
            "integrations":{"gmail":"OAuth not configured","sms":"Manual text only; Android integration not implemented","screen":"Not connected; OS permission required","audio":"Not connected; detector required","video":"Not connected; detector required"}}

@app.post("/api/chat")
def chat(request: ChatRequest):
    return respond_to_message(request.message)

@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    return analyze_content(request.kind, request.content)

@app.post("/api/upload/{media_kind}")
async def upload_media(media_kind: str, file: UploadFile = File(...)):
    if media_kind not in {"audio","video"}:
        raise HTTPException(status_code=400, detail="Use audio or video.")
    allowed = {"audio":{"audio/mpeg","audio/wav","audio/x-wav","audio/mp4","audio/ogg","audio/webm"},
               "video":{"video/mp4","video/webm","video/quicktime","video/x-matroska"}}
    if file.content_type not in allowed[media_kind]:
        raise HTTPException(status_code=415, detail="Unsupported media type. No file was analysed.")
    data = await file.read(25 * 1024 * 1024 + 1)
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Maximum upload size is 25 MB.")
    return {"status":"not_implemented","media_kind":media_kind,"filename":file.filename,"bytes_received":len(data),
            "verdict":"Inconclusive","summary":"File received in memory and discarded. No deepfake or voice-cloning analysis was performed.",
            "disclaimer":"This endpoint does not store or analyse uploaded media."}

@app.get("/api/integrations/gmail/connect")
def gmail_connect():
    return {"status":"not_configured","message":"Google OAuth credentials and redirect configuration are required. No Gmail access was attempted."}

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "frontend" / "index.html")
