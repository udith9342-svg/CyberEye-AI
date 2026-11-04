from urllib.parse import urlparse

SUSPICIOUS_WORDS = ("verify", "login", "secure", "update", "wallet", "password", "otp", "bank")


def analyze_url(value: str) -> list[dict]:
    value = value.strip()
    if not value:
        return [{"label": "Empty input", "detail": "Enter a URL to analyse.", "weight": 0}]
    candidate = value if "://" in value else f"https://{value}"
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    signals = []
    if parsed.scheme != "https":
        signals.append({"label": "No HTTPS", "detail": "The supplied URL does not use HTTPS.", "weight": 20})
    if not host or "." not in host or " " in host:
        signals.append({"label": "Unusual URL format", "detail": "The URL does not contain a recognisable hostname.", "weight": 35})
    if host.startswith("xn--") or ".xn--" in host:
        signals.append({"label": "Punycode hostname", "detail": "The hostname uses internationalised encoding; inspect it carefully for lookalike characters.", "weight": 30})
    if host.count("-") >= 3:
        signals.append({"label": "Many hyphens in hostname", "detail": "Multiple hyphens can be a warning sign; this alone does not prove phishing.", "weight": 15})
    matched = [word for word in SUSPICIOUS_WORDS if word in host]
    if matched:
        signals.append({"label": "Sensitive terms in hostname", "detail": "Hostname contains: " + ", ".join(matched), "weight": 15})
    if not signals:
        signals.append({"label": "No simple warning pattern found", "detail": "The basic rules found no listed warning signs. This does not establish that the site is legitimate.", "weight": 0})
    return signals
