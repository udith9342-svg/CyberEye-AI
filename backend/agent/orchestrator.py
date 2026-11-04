from backend.modules.url_detection.url_analyzer import analyze_url
from backend.modules.sms_security.sms_analyzer import analyze_sms
from backend.agent.risk_engine import build_result


def analyze_content(kind: str, content: str) -> dict:
    """Route a user-submitted item to its module; unsupported modules stay explicit."""
    kind = kind.strip().lower()
    if kind == "url":
        signals = analyze_url(content)
    elif kind == "sms":
        signals = analyze_sms(content)
    elif kind in {"email", "audio", "video"}:
        return {
            "module": kind,
            "status": "not_implemented",
            "verdict": "Inconclusive",
            "risk_score": None,
            "summary": f"The {kind} analysis module is planned but is not implemented yet.",
            "signals": [],
            "disclaimer": "No detection was performed. Do not treat this as a security assessment.",
        }
    else:
        return {"error": "Unsupported analysis type. Use url, sms, email, audio, or video."}
    return build_result(kind, signals)
