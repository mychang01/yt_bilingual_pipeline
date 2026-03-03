from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.utils import srt_time


def generate_srt(subtitles: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    for i, block in enumerate(subtitles, start=1):
        start = srt_time(float(block.get("start", 0.0)))
        end = srt_time(float(block.get("end", 0.0)))
        text_en = str(block.get("text_en", "")).strip()
        text_zh = str(block.get("text_zh", "")).strip()

        lines.append(str(i))
        lines.append(f"{start} --> {end}")
        lines.append(text_en)
        if text_zh:
            lines.append(text_zh)
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_json(subtitles: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(subtitles, ensure_ascii=False, indent=2), encoding="utf-8")
