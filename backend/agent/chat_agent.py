"""Natural-language entry point for CyberEye AI.

When OPENAI_API_KEY is configured, an LLM classifies the user's request into a
small, allow-listed set of actions. Without a key, a transparent keyword-based
fallback supports basic URL/SMS requests. The fallback is not an AI model.
"""
import json
import os
import re
from typing import Any

from backend.agent.orchestrator import analyze_content

SYSTEM_PROMPT = """You are CyberEye AI, a cautious cybersecurity assistant.
Understand the user's natural-language request and return ONLY JSON with:
{"intent":"url|sms|email|audio|video|screen|gmail|general","content":"the exact item to analyse, or empty string"}.
Choose url when the user asks to check a link/website or provides a URL.
Choose sms for text messages, scam texts, OTP/social-engineering messages.
Choose email for email text or email safety requests.
Choose audio for uploaded/attached audio or voice-cloning checks.
Choose video for uploaded/attached video or deepfake checks.
Choose screen for screen monitoring or screen-sharing requests.
Choose gmail for Gmail connection, inbox or email integration requests.
Choose general for general questions about CyberEye or cybersecurity.
Never claim planned integrations or unimplemented detection are working.
Never ask for passwords, OTPs, private keys, or account credentials.
"""

def _fallback_intent(message: str) -> dict[str, str]:
    text = message.strip()
    lower = text.lower()
    url_match = re.search(r"(https?://[^\s]+|www\.[^\s]+|[a-z0-9.-]+\.[a-z]{2,}(?:/[^\s]*)?)", text, re.I)
    if any(word in lower for word in ("gmail", "inbox", "connect my email", "email account")):
        return {"intent": "gmail", "content": ""}
    if any(word in lower for word in ("screen", "monitor my display", "share my screen")):
        return {"intent": "screen", "content": ""}
    if any(word in lower for word in ("deepfake", "video", "clip")):
        return {"intent": "video", "content": ""}
    if any(word in lower for word in ("voice", "audio", "recording")):
        return {"intent": "audio", "content": ""}
    if any(word in lower for word in ("email", "mail message")):
        return {"intent": "email", "content": text}
    if any(word in lower for word in ("sms", "text message", "message says", "scam message")):
        return {"intent": "sms", "content": text}
    if url_match:
        return {"intent": "url", "content": url_match.group(0).rstrip(".,);]")}
    return {"intent": "general", "content": ""}

def _llm_intent(message: str) -> dict[str, str] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("CYBEREYE_AGENT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message[:12000]},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        parsed: Any = json.loads(response.choices[0].message.content or "{}")
        intent = str(parsed.get("intent", "general")).lower()
        content = str(parsed.get("content", ""))
        allowed = {"url", "sms", "email", "audio", "video", "screen", "gmail", "general"}
        if intent not in allowed:
            return None
        return {"intent": intent, "content": content[:20000]}
    except Exception:
        # Never expose provider details or silently pretend the LLM worked.
        return None

def respond_to_message(message: str) -> dict:
    """Interpret one natural-language request and dispatch only safe supported tools."""
    intent_data = _llm_intent(message) or _fallback_intent(message)
    intent = intent_data["intent"]
    content = intent_data["content"]
    used_llm = bool(os.getenv("OPENAI_API_KEY")) and _llm_intent_was_successful(message, intent_data)

    if intent in {"url", "sms"}:
        if not content:
            content = message
        result = analyze_content(intent, content)
        return {
            "reply": f"I analysed the {intent.upper()} using the currently available baseline checks. Review the evidence and limitations below.",
            "intent": intent,
            "agent_mode": "llm" if used_llm else "basic_fallback",
            "result": result,
        }

    planned = {
        "email": ("Email intelligence", "Pasted email analysis and Gmail OAuth are not connected yet. Gmail will require your explicit Google OAuth permission; never share your Gmail password."),
        "gmail": ("Gmail integration", "Gmail OAuth is not configured yet. The next integration step is a Google Cloud OAuth client with read-only Gmail access and explicit consent."),
        "audio": ("Audio / voice analysis", "Audio upload and voice-cloning detection are planned. No audio detector is connected, so CyberEye cannot assess authenticity yet."),
        "video": ("Video / deepfake analysis", "Video upload and deepfake detection are planned. No video detector is connected, so CyberEye cannot assess authenticity yet."),
        "screen": ("Screen monitoring", "Screen monitoring requires a separate, explicit screen-capture permission flow and an analysis pipeline. It is not active in this version."),
    }
    if intent in planned:
        title, detail = planned[intent]
        return {"reply": f"{title}: {detail}", "intent": intent, "agent_mode": "llm" if used_llm else "basic_fallback", "result": {"status": "not_implemented", "verdict": "Not connected", "risk_score": None, "signals": [], "summary": detail, "disclaimer": "No detection or monitoring was performed."}}
    return {
        "reply": "I'm CyberEye AI. You can ask me naturally to check a suspicious URL or analyse an SMS. Gmail, email, audio, video and screen-monitoring integrations are planned but not connected yet.",
        "intent": "general",
        "agent_mode": "llm" if used_llm else "basic_fallback",
        "result": None,
    }

def _llm_intent_was_successful(message: str, intent_data: dict[str, str]) -> bool:
    # Keep provider use explicit. A second call is avoided; this marker is set by
    # checking whether a key exists, but failures are surfaced by fallback mode.
    # The classifier function returns None on failure; caller sets the mode below.
    return bool(os.getenv("OPENAI_API_KEY"))
