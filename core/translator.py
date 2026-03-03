from __future__ import annotations

from typing import Any

from openai import OpenAI

from config import (
    GLOSSARY_PATH,
    MOCK_MODE,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    PROMPT_PATH,
    TRANSLATE_MODEL,
)
from core.utils import read_json, retry


def _get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in .env.")
    base_url = OPENAI_BASE_URL or "https://api.openai.com/v1"
    return OpenAI(api_key=OPENAI_API_KEY, base_url=base_url)


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _load_glossary() -> dict[str, Any]:
    if not GLOSSARY_PATH.exists():
        return {}
    return read_json(GLOSSARY_PATH)


def _build_user_content(text_en: str) -> str:
    prompt = _load_prompt()
    glossary = _load_glossary()
    glossary_text = "\n".join(f"- {k}: {v}" for k, v in glossary.items()) or "(empty)"

    return (
        f"{prompt}\n\n"
        f"[Glossary]\n{glossary_text}\n\n"
        f"[Input]\n{text_en}\n\n"
        "[Output]"
    )


def _translate_block(text_en: str) -> str:
    if MOCK_MODE:
        return f"[MOCK_ZH] {text_en}"

    client = _get_client()
    resp = client.chat.completions.create(
        model=TRANSLATE_MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": "You are a professional subtitle translator."},
            {"role": "user", "content": _build_user_content(text_en)},
        ],
    )

    content = resp.choices[0].message.content if resp.choices else None
    if not content:
        raise RuntimeError(f"Translation content empty: {resp}")
    return content.strip()


def batch_translate(subtitles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for block in subtitles:
        text_en = str(block.get("text_en", "")).strip()
        if not text_en:
            continue

        text_zh = retry(_translate_block, text_en)
        results.append(
            {
                "start": float(block.get("start", 0.0)),
                "end": float(block.get("end", 0.0)),
                "text_en": text_en,
                "text_zh": text_zh,
            }
        )
    return results
