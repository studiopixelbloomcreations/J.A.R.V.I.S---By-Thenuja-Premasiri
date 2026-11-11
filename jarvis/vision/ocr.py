"""
Visual Understanding & OCR Engine for J.A.R.V.I.S.
Leverages Gemini Multimodal Vision to inspect screens, explain errors, and extract text.
"""
import json
import base64
import urllib.request
from ..config import load_config


def analyze_screen_image(image_base64_or_path, prompt="Describe what is visible on this screen in detail."):
    """
    Submits a screenshot to Gemini Vision model for comprehensive screen analysis,
    error diagnosis, button identification, or visual Q&A.
    """
    config = load_config()
    api_key = config.get("api_key")
    if not api_key:
        return {"status": "error", "error": "Gemini API key not configured."}

    # Extract raw base64 data
    if image_base64_or_path.startswith("data:image/"):
        b64_data = image_base64_or_path.split(",", 1)[1]
    elif len(image_base64_or_path) > 300:
        b64_data = image_base64_or_path
    else:
        # It is a path
        with open(image_base64_or_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")

    models_to_try = [
        config.get("model", "gemini-3.5-flash-lite"),
        "gemini-3.5-flash",
        "gemini-2.5-flash",
    ]
    # Deduplicate
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

    system_instruction = (
        "You are J.A.R.V.I.S., an advanced visual perception engine for a Windows PC. "
        "Analyze the provided screenshot with precision. Identify active windows, dialogs, error messages, "
        "buttons, input fields, and layout elements. Be concise, technical, and immediately actionable."
    )

    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": b64_data
                    }
                }
            ]
        }],
        "generationConfig": {
            "maxOutputTokens": 800,
            "temperature": 0.2
        }
    }).encode("utf-8")

    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        if "text" in part:
                            return {
                                "status": "success",
                                "analysis": part["text"],
                                "model": model
                            }
        except Exception as e:
            last_error = str(e)
            continue

    return {"status": "error", "error": f"Vision analysis failed: {last_error}"}
