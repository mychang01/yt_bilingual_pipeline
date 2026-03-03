from __future__ import annotations

import re
from typing import Any

from config import MAX_WORDS_PER_LINE

FILLERS = {"um", "uh", "you know", "like", "erm", "hmm"}


def _remove_fillers(text: str) -> str:
    result = text
    for filler in FILLERS:
        result = re.sub(rf"\b{re.escape(filler)}\b", "", result, flags=re.IGNORECASE)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def _split_if_long(start: float, end: float, text: str) -> list[dict[str, Any]]:
    words = text.split()
    if len(words) <= MAX_WORDS_PER_LINE:
        return [{"start": start, "end": end, "text_en": text}]

    midpoint = len(words) // 2
    left = " ".join(words[:midpoint]).strip()
    right = " ".join(words[midpoint:]).strip()

    mid_t = start + (end - start) * (midpoint / len(words))
    rows: list[dict[str, Any]] = []
    if left:
        rows.append({"start": start, "end": mid_t, "text_en": left})
    if right:
        rows.append({"start": mid_t, "end": end, "text_en": right})
    return rows


def _fix_timestamps(subtitles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    subtitles = sorted(subtitles, key=lambda x: x["start"])
    for idx in range(1, len(subtitles)):
        prev = subtitles[idx - 1]
        cur = subtitles[idx]
        if cur["start"] < prev["end"]:
            cur["start"] = prev["end"] + 0.01
        if cur["end"] <= cur["start"]:
            cur["end"] = cur["start"] + 0.5
    return subtitles


def clean(subtitles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for block in subtitles:
        text = _remove_fillers(str(block.get("text_en", "")))
        if not text:
            continue

        start = float(block.get("start", 0.0))
        end = float(block.get("end", start + 1.0))
        output.extend(_split_if_long(start, end, text))

    return _fix_timestamps(output)
