def build_result(module: str, signals: list[dict]) -> dict:
    """Conservative rule-based prototype scoring; not a probability or AI model."""
    score = min(100, sum(item.get("weight", 0) for item in signals))
    if score >= 60:
        verdict = "High Risk"
    elif score >= 30:
        verdict = "Suspicious"
    else:
        verdict = "No strong signals detected"
    return {
        "module": module,
        "status": "baseline_prototype",
        "verdict": verdict,
        "risk_score": score,
        "summary": "This result is based on simple prototype rules, not a trained AI model.",
        "signals": [{"label": x["label"], "detail": x["detail"]} for x in signals],
        "disclaimer": "A low score does not prove content is safe. Verify links and requests independently.",
    }
