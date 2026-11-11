"""
AI Model Gateway for J.A.R.V.I.S.
Handles Gemini multimodal and text API requests with multi-model fallback,
and Fish Audio high-fidelity TTS generation.
"""
import json
import base64
import struct
import urllib.request
import urllib.error
from ..config import load_config


def execute_gemini_request(api_key, model, payload, timeout=14):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        candidates = body.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "text" in part:
                    return part["text"]
        return "No text response generated."


def call_gemini(system_prompt, messages=None, max_tokens=600, temperature=0.3):
    """Calls Gemini API with automatic model fallback."""
    if messages is None:
        messages = [{"role": "user", "content": system_prompt}]
        system_prompt = "You are J.A.R.V.I.S., an intelligent personal AI assistant."
    elif isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    config = load_config()
    api_key = config.get("api_key")
    if not api_key:
        raise RuntimeError("Google Gemini API key is not configured in config.json.")

    model = config.get("model", "gemini-3.5-flash-lite")
    models_to_try = [
        model,
        "gemini-3.5-flash",
        "gemini-2.5-flash",
    ]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

    contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else msg["role"]
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}],
        })

    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }).encode("utf-8")

    last_error = None
    for cur_model in models_to_try:
        try:
            return execute_gemini_request(api_key, cur_model, payload, timeout=12)
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(last_error or "All Gemini model candidates failed.")


def generate_fish_audio_tts(text):
    """
    Calls Fish Audio TTS API.
    Returns (audio_bytes, 200) on success, or (dict, status) on fallback/error.
    """
    config = load_config()
    fish_cfg = config.get("fish_audio", {})
    api_key = fish_cfg.get("api_key", "").strip()

    if not api_key or api_key.startswith("PUT-YOUR"):
        return {"fallback": True, "message": "Fish Audio key unconfigured, using browser voice."}, 200

    model = fish_cfg.get("model", "s2.1-pro-free")
    ref_id = fish_cfg.get("reference_id", "").strip()

    payload = {
        "text": text.strip(),
        "format": "mp3",
        "mp3_bitrate": 64,
        "latency": "normal",
    }
    if ref_id:
        payload["reference_id"] = ref_id

    req = urllib.request.Request(
        "https://api.fish.audio/v1/tts",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "model": model,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=18) as resp:
            audio_bytes = resp.read()
            return audio_bytes, 200
    except Exception as e:
        return {"fallback": True, "error": str(e)}, 200


def pcm_to_wav(pcm_bytes, sample_rate=24000, num_channels=1, bits_per_sample=16):
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    data_size = len(pcm_bytes)
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,
        b'WAVE',
        b'fmt ',
        16,
        1,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size
    )
    return header + pcm_bytes


def generate_gemini_live_audio(text, voice_name=None):
    """
    Calls Google Gemini Multimodal Live Speech API using the official 'Charon' prebuilt voice.
    Returns (wav_bytes, 200) on success, or (dict, status) on fallback/error.
    """
    config = load_config()
    api_key = config.get("api_key", "").strip()
    if not api_key:
        return {"fallback": True, "message": "Gemini API key unconfigured."}, 200

    if not voice_name:
        voice_name = config.get("gemini_live_voice", "Charon")

    payload = {
        "contents": [{"parts": [{"text": text.strip()}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        }
    }

    candidates = ["gemini-2.5-flash-preview-tts", "gemini-3.1-flash-tts-preview", "gemini-3.8-flash-tts"]
    for m in candidates:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=16) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cand = data.get("candidates", [])[0]
                parts = cand.get("content", {}).get("parts", [])
                for p in parts:
                    if "inlineData" in p:
                        raw_pcm = base64.b64decode(p["inlineData"]["data"])
                        wav_bytes = pcm_to_wav(raw_pcm, 24000)
                        return wav_bytes, 200
        except Exception:
            continue

    return {"fallback": True, "message": "Gemini Live voice gateway unavailable."}, 200


# Alias for unified speech gateway
generate_speech_audio = generate_fish_audio_tts
