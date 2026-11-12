"""
Bilingual Sinhala-English Neural Translation Bridge for J.A.R.V.I.S.
Provides seamless translation from Sinhala speech/text to English
to preserve full knowledge extraction, reasoning, and British butler voice delivery.
"""
import re
from .gateway import call_gemini

SINHALA_CHAR_REGEX = re.compile(r'[\u0D80-\u0DFF]')
WAKE_WORDS_REGEX = re.compile(r'^(hey\s+)?(jarvis|ජාවිස්|ජාර්විස්)[,\s:]*', flags=re.IGNORECASE)


def is_sinhala_text(text: str) -> bool:
    """Returns True if the input string contains Sinhala Unicode characters."""
    if not text:
        return False
    return bool(SINHALA_CHAR_REGEX.search(text))


def clean_wake_word(text: str) -> str:
    """Removes leading wake words in either English or Sinhala."""
    if not text:
        return ""
    return WAKE_WORDS_REGEX.sub('', text.strip()).strip()


def translate_sinhala_to_english(text: str) -> str:
    """
    Translates Sinhala speech/text accurately into natural, fluent English.
    Preserves speaker perspective (e.g. personal statements stay in first-person).
    """
    if not text:
        return ""

    cleaned = clean_wake_word(text)
    if not cleaned:
        return ""

    if not is_sinhala_text(cleaned):
        return cleaned

    prompt = (
        "You are an expert bilingual Sinhala to English translation engine for J.A.R.V.I.S.\n"
        "Translate the following Sinhala statement accurately into fluent, natural English.\n"
        "Maintain first-person perspective ('I', 'my') if the speaker refers to themselves.\n"
        "Output ONLY the direct English translation without introductory remarks, explanations, quotes, or markdown tags.\n\n"
        f"Sinhala text: {cleaned}"
    )

    try:
        translated = call_gemini(prompt, max_tokens=300, temperature=0.1)
        res = translated.strip().strip('"').strip("'").strip()
        if res:
            return res
    except Exception as e:
        print(f"  ⚠ Sinhala translation failed: {e}")

    return cleaned
