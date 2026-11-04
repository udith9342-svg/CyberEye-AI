SCAM_PATTERNS = {
    "Urgent action": ("immediately", "urgent", "act now", "suspended", "blocked"),
    "Credential or OTP request": ("share otp", "send otp", "password", "pin", "verify your account"),
    "Prize or reward claim": ("you won", "claim prize", "lottery", "free gift"),
    "Payment pressure": ("pay now", "processing fee", "refund fee", "account will be closed"),
}


def analyze_sms(value: str) -> list[dict]:
    text = value.strip().lower()
    if not text:
        return [{"label": "Empty input", "detail": "Paste a message to analyse.", "weight": 0}]
    signals = []
    for label, phrases in SCAM_PATTERNS.items():
        hits = [phrase for phrase in phrases if phrase in text]
        if hits:
            signals.append({"label": label, "detail": "Matched phrase(s): " + ", ".join(hits), "weight": 20})
    if not signals:
        signals.append({"label": "No listed scam phrase found", "detail": "The basic rules found no listed phrase. New or carefully worded scams may not be detected.", "weight": 0})
    return signals
