# CyberEye AI

**Unified Agentic AI Cybersecurity Platform**

CyberEye AI is a PC-first web prototype that brings several digital-safety checks into one interface. A central orchestrator routes a submitted item to the relevant security module and returns an explainable result.

## Planned capabilities

- **Business email intelligence:** authorised Gmail connection, business-context prioritisation, spam and phishing analysis.
- **Deepfake video analysis:** inspect uploaded video for possible manipulation.
- **Voice-cloning analysis:** inspect audio for possible synthetic or impersonated speech.
- **Phishing URL analysis:** assess suspicious links and explain warning signs.
- **SMS scam analysis:** assess pasted text messages for scam patterns.

## Current prototype status

The first development milestone implements the FastAPI service, a basic web interface, and transparent baseline checks for pasted URLs and SMS text. These baseline checks are **not trained AI models** and must not be presented as conclusive detection. Email, deepfake, and voice modules are integration placeholders until validated models and authorised integrations are added.

## Architecture

```text
Browser UI (HTML/CSS/JavaScript)
              |
          FastAPI API
              |
      Agent Orchestrator
        /    |     \
      URL   SMS   Future modules
        \    |     /
          Risk Engine
              |
      Explainable response
```

## Run locally

Requires Python 3.10+.

1. Open a terminal in the repository.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Start the API: `uvicorn backend.main:app --reload`
5. Open `http://127.0.0.1:8000`

The API documentation is available at `http://127.0.0.1:8000/docs`.

## Privacy and safety principles

- Never ask users to paste email passwords or account credentials.
- Gmail access must use Google OAuth and explicit consent when implemented.
- Do not retain uploaded messages, audio, or video by default.
- Do not automatically delete, send, or move user content.
- A result such as "No strong signals detected" is not a guarantee that content is safe.
- Use harmless, synthetic test samples only. Do not upload private or sensitive material to public test environments.

## Roadmap

1. Establish API and frontend foundation.
2. Improve URL and SMS analysis with documented datasets and evaluation.
3. Add email analysis on user-provided samples, then authorised Gmail OAuth.
4. Integrate and evaluate deepfake-video and voice-cloning models.
5. Add orchestration, unified risk explanations, tests, and privacy controls.

## Team

Built for the HAXC hackathon team. Contributions and validated test results will be documented as features are implemented.
