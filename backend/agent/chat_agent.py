"""Natural-language request router for CyberEye AI."""
import json
import os
import re
from typing import Any
from backend.agent.orchestrator import analyze_content

SYSTEM_PROMPT = """You are CyberEye AI, a cautious cybersecurity assistant.
Return ONLY JSON: {"intent":"url|sms|email|audio|video|screen|gmail|general","content":"item to analyse or empty"}.
Choose url for a link, sms for a text message, email for email text, audio for audio/voice, video for video/deepfake, screen for screen monitoring, gmail for Gmail connection/inbox, general for other questions.
Never claim an unimplemented integration or detector works. Never request passwords, OTPs or private keys."""

def _fallback_intent(message: str) -> dict[str, str]:
    text, lower = message.strip(), message.lower()
    match = re.search(r"(https?://[^\s]+|www\.[^\s]+|[a-z0-9.-]+\.[a-z]{2,}(?:/[^\s]*)?)", text, re.I)
    if any(x in lower for x in ("gmail", "inbox", "connect my email", "email account")):
        return {"intent": "gmail", "content": ""}
    if any(x in lower for x in ("screen", "monitor my display", "share my screen")):
        return {"intent": "screen", "content": ""}
    if any(x in lower for x in ("deepfake", "video", "clip")):
        return {"intent": "video", "content": ""}
    if any(x in lower for x in ("voice", "audio", "recording")):
        return {"intent": "audio", "content": ""}
    if any(x in lower for x in ("email", "mail message")):
        return {"intent": "email", "content": text}
    if any(x in lower for x in ("sms", "text message", "scam message")):
        return {"intent": "sms", "content": text}
    if match:
        return {"intent": "url", "content": match.group(0).rstrip(".,);]")}
    return {"intent": "general", "content": ""}

def _classify(message: str) -> tuple[dict[str, str], str]:
    if os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model=os.getenv("CYBEREYE_AGENT_MODEL", "gpt-4o-mini"),
                messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":message[:12000]}],
                response_format={"type":"json_object"}, temperature=0,
            )
            parsed: Any = json.loads(response.choices[0].message.content or "{}")
            intent = str(parsed.get("intent", "general")).lower()
            content = str(parsed.get("content", ""))
            if intent in {"url","sms","email","audio","video","screen","gmail","general"}:
                return {"intent":intent,"content":content[:20000]}, "llm"
        except Exception:
            pass
    return _fallback_intent(message), "basic_fallback"

def respond_to_message(message: str) -> dict:
    """Route user intent to implemented tools or honest integration placeholders."""
    selected, mode = _classify(message)
    intent, content = selected["intent"], selected["content"]
    if intent in {"url", "sms"}:
        result = analyze_content(intent, content or message)
        return {"reply":f"I checked the {intent.upper()} using the currently available baseline rules. Please review the evidence and limitations.", "intent":intent, "agent_mode":mode, "result":result}
    planned = {
        "email":("Email intelligence","Pasted email analysis and Gmail OAuth are not connected yet. Gmail will require explicit Google OAuth permission; never share your Gmail password."),
        "gmail":("Gmail integration","Gmail OAuth is not configured yet. It requires a Google Cloud OAuth client, secure token handling and explicit consent."),
        "audio":("Audio / voice analysis","Audio upload and voice-cloning detection are not connected. No authenticity analysis was performed."),
        "video":("Video / deepfake analysis","Video upload and deepfake detection are not connected. No authenticity analysis was performed."),
        "screen":("Screen monitoring","Screen monitoring requires a permission-based desktop companion and analysis pipeline. It is not active."),
    }
    if intent in planned:
        title, detail = planned[intent]
        return {"reply":f"{title}: {detail}", "intent":intent, "agent_mode":mode, "result":{"status":"not_implemented","verdict":"Not connected","risk_score":None,"signals":[],"summary":detail,"disclaimer":"No detection or monitoring was performed."}}
    return {"reply":"I'm CyberEye AI. Ask me to check a suspicious URL or analyse an SMS. Gmail, email, audio, video and screen integrations are not connected yet.", "intent":"general", "agent_mode":mode, "result":None}
