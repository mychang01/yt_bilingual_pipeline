from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL

from config import AUDIO_DIR, RAW_DIR


def check_subtitle(url: str) -> bool:
    with YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    return bool(info.get("subtitles") or info.get("automatic_captions"))


def _download_subtitle_file(url: str) -> Path | None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-US"],
        "subtitlesformat": "vtt/srt",
        "outtmpl": str(RAW_DIR / "%(id)s.%(ext)s"),
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        requested = info.get("requested_subtitles") or {}
        for _, sub in requested.items():
            filepath = sub.get("filepath")
            if filepath:
                p = Path(filepath)
                if p.exists():
                    return p

    candidates = sorted(RAW_DIR.glob("*.vtt")) + sorted(RAW_DIR.glob("*.srt"))
    return candidates[-1] if candidates else None


def _to_seconds(ts: str) -> float:
    ts = ts.replace(",", ".")
    parts = ts.split(":")
    if len(parts) != 3:
        return 0.0
    h, m, s = parts
    return int(h) * 3600 + int(m) * 60 + float(s)


def _parse_subtitle_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.split(r"\n\s*\n", text.strip())
    rows: list[dict[str, Any]] = []

    for block in blocks:
        lines = [line.strip("\ufeff") for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        if "-->" in lines[0]:
            time_line_index = 0
        elif len(lines) > 1 and "-->" in lines[1]:
            time_line_index = 1
        else:
            continue

        time_line = lines[time_line_index]
        segs = [p.strip() for p in time_line.split("-->")]
        if len(segs) != 2:
            continue

        start = _to_seconds(segs[0].split(" ")[0])
        end = _to_seconds(segs[1].split(" ")[0])
        content = " ".join(lines[time_line_index + 1 :]).strip()
        if not content or content.upper() == "WEBVTT":
            continue

        rows.append({"start": start, "end": end, "text_en": content})

    return rows


def load_subtitle(url: str) -> list[dict[str, Any]] | None:
    subtitle_path = _download_subtitle_file(url)
    if subtitle_path is None:
        return None
    parsed = _parse_subtitle_file(subtitle_path)
    return parsed or None


def process(url: str) -> list[dict[str, Any]] | None:
    if not check_subtitle(url):
        return None
    return load_subtitle(url)


def download_audio(url: str) -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "outtmpl": str(AUDIO_DIR / "%(id)s.%(ext)s"),
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Audio not found: {path}")
    return path
