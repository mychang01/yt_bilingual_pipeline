from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Callable, TypeVar
from urllib.parse import urlparse

from config import MAX_RETRY, RETRY_BACKOFF_SECONDS

T = TypeVar("T")


def retry(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRY + 1):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < MAX_RETRY:
                time.sleep(RETRY_BACKOFF_SECONDS)
    raise RuntimeError(f"Failed after {MAX_RETRY} retries: {last_error}")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_stem_from_url(url: str) -> str:
    parsed = urlparse(url)
    base = f"{parsed.netloc}_{parsed.path}" if parsed.netloc else url
    stem = re.sub(r"[^a-zA-Z0-9_-]", "_", base).strip("_")
    return stem[:80] or "video"


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h = ms // 3_600_000
    ms %= 3_600_000
    m = ms // 60_000
    ms %= 60_000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
