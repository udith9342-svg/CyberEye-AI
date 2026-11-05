"""Allow-listed CyberEye analysis tools.

Only implemented tools are callable. Integrations that need OAuth, native
permissions or validated ML models are deliberately listed as unavailable.
"""
from backend.agent.orchestrator import analyze_content

AVAILABLE_TOOLS = {
    "analyze_url": {"module": "url", "implemented": True},
    "analyze_sms": {"module": "sms", "implemented": True},
    "analyze_email": {"module": "email", "implemented": False},
    "analyze_audio": {"module": "audio", "implemented": False},
    "analyze_video": {"module": "video", "implemented": False},
    "monitor_screen": {"module": "screen", "implemented": False},
    "connect_gmail": {"module": "gmail", "implemented": False},
}

def list_tools() -> list[dict]:
    return [{"name": name, **details} for name, details in AVAILABLE_TOOLS.items()]

def run_tool(name: str, content: str = "") -> dict:
    tool = AVAILABLE_TOOLS.get(name)
    if not tool:
        return {"status": "rejected", "message": "Unknown tool. This action is not permitted."}
    if not tool["implemented"]:
        return {"status": "not_implemented", "message": f"{name} is not connected yet. No action was performed."}
    return analyze_content(tool["module"], content)
