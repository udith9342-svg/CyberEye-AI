# CyberEye AI

**A unified, natural-language cybersecurity assistant for individuals and businesses.**

CyberEye is being developed as one central agent that understands a user's request, selects an approved security tool and returns an explainable result. Only features explicitly marked implemented below should be treated as working.

## Product vision

- **Conversational agent:** understand natural-language requests and route them to the appropriate security capability.
- **Gmail/business email intelligence:** Google OAuth with explicit consent; analyse and prioritise suspicious or useful business email. Never request a Gmail password.
- **SMS security:** analyse pasted SMS text now; direct phone SMS access requires a separate Android companion app and OS permission.
- **URL protection:** analyse user-submitted links and explain warning signs.
- **Video/deepfake checks:** user-selected video upload and validated media models.
- **Audio/voice-cloning checks:** user-selected audio upload and validated models.
- **Screen monitoring:** future permission-based desktop companion for a user-selected screen/window. Screen and call-audio capture are separate capabilities and require separate consent and platform support.
- **Unified reports:** evidence, risk assessment, uncertainty and recommended next steps.

## Current implementation status

| Capability | Status |
|---|---|
| FastAPI backend and unified chat UI | Implemented |
| Natural-language routing | Optional OpenAI model; basic keyword fallback without API key |
| URL analysis | Basic heuristic prototype |
| SMS analysis | Basic phrase-matching prototype |
| Gmail OAuth | Not configured |
| Direct SMS integration | Not implemented; manual text only |
| Email content analysis | Not implemented |
| Audio/video upload | Limited upload endpoint up to 25 MB; no analysis or retention |
| Deepfake / voice-cloning detection | Not implemented |
| Screen permission preview | Browser permission and local preview only; no screen analysis or transmission |
| Windows desktop companion | Not implemented |

**Important:** URL/SMS checks are not trained AI detection models. A low score or absence of warning signs does not prove content is safe. Media upload currently performs no authenticity assessment.

## Architecture

```text
Web chat / future desktop companion
              |
       FastAPI application
              |
     Natural-language agent
              |
       Allow-listed tool registry
       /       |       |       \
     URL      SMS    Gmail    Media / Screen
      |        |       |          |
  Baseline  Baseline  OAuth    Validated models
       \       |       |          /
          Unified risk/report layer
```

Only implemented tools are executable. Planned integrations return an explicit not-connected status.

## Optional language-model setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your API key.
3. Keep `.env` private and never commit it.
4. Start: `uvicorn backend.main:app --reload`
5. Open `http://127.0.0.1:8000`; API docs: `http://127.0.0.1:8000/docs`.

Without `OPENAI_API_KEY`, a limited keyword fallback is used. It is not a full natural-language AI model.

## Privacy and safety

- Never request or store email passwords, OTPs, private keys or account credentials.
- Gmail must use Google OAuth, minimum required scopes and explicit consent.
- Do not automatically send, delete or move emails/messages.
- Do not retain user media by default. Current upload endpoint processes bytes in memory and discards them without analysis.
- Screen capture must be explicitly initiated by the user. Current browser preview is local only and sends no screen frames to the server.
- Live call audio capture is separate from screen sharing and depends on OS, app support and consent.
- "No strong signs detected" is not proof of authenticity or safety.

## Roadmap

1. Validate agent and URL/SMS modules with tests.
2. Improve URL/SMS intelligence with documented evaluation.
3. Add pasted email analysis, then read-only Gmail OAuth.
4. Integrate and evaluate deepfake-video and voice-cloning models.
5. Build a Windows desktop companion for user-selected screen/window monitoring.
6. Evaluate privacy, permissions, false positives and false negatives before claiming real-time protection.

## Run locally

Requires Python 3.10+.

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Built by the HAXC team. Feature claims must match tested implementation status.
