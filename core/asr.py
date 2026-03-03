from __future__ import annotations

from pathlib import Path
from typing import Any

from openai import OpenAI

from config import ASR_MODEL, MOCK_MODE, OPENAI_API_KEY, OPENAI_BASE_URL
from core.utils import retry


def _get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in .env.")
    base_url = OPENAI_BASE_URL or "https://api.openai.com/v1"
    return OpenAI(api_key=OPENAI_API_KEY, base_url=base_url)


def _call_whisper(audio_path: Path) -> Any:
    if MOCK_MODE:
        return {
            "segments": [
                {"start": 0.2, "end": 2.1, "text": f"Mock transcript for {audio_path.name}."}
            ]
        }

    client = _get_client()
    with audio_path.open("rb") as f:
        # verbose_json includes segment-level timestamps
        return client.audio.transcriptions.create(
            model=ASR_MODEL,
            file=f,
            response_format="verbose_json",
            language="en",
        )


def _format_to_standard(response: Any) -> list[dict[str, Any]]:
    data = response.model_dump() if hasattr(response, "model_dump") else response

    segments = data.get("segments", []) if isinstance(data, dict) else []
    if not segments:
        text = ""
        if isinstance(data, dict):
            text = str(data.get("text", "")).strip()
        if text:
            return [{"start": 0.0, "end": max(1.0, len(text) / 10.0), "text_en": text}]
        return []

    rows: list[dict[str, Any]] = []
    for seg in segments:
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", start + 0.5))
        if end <= start:
            end = start + 0.5
        rows.append(
            {
                "start": start,
                "end": end,
                "text_en": str(seg.get("text", "")).strip(),
            }
        )
    return [row for row in rows if row["text_en"]]


def transcribe(audio_path: Path) -> list[dict[str, Any]]:
    response = retry(_call_whisper, audio_path)
    results = _format_to_standard(response)
    if not results:
        raise RuntimeError("Whisper returned empty segments")
    return results
