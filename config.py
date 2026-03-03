"""Global configuration for Whisper + ChatGPT pipeline."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # optional during bootstrap
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
if load_dotenv is not None:
    load_dotenv(env_path)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").rstrip("/")
ASR_MODEL = os.getenv("ASR_MODEL", "whisper-1")
TRANSLATE_MODEL = os.getenv("TRANSLATE_MODEL", "gpt-4.1-mini")

# Runtime behavior
MAX_RETRY = int(os.getenv("MAX_RETRY", "3"))
RETRY_BACKOFF_SECONDS = float(os.getenv("RETRY_BACKOFF_SECONDS", "1"))
MAX_WORDS_PER_LINE = int(os.getenv("MAX_WORDS_PER_LINE", "20"))

# Paths
PROMPT_PATH = BASE_DIR / "prompts" / "translate_prompt.txt"
GLOSSARY_PATH = BASE_DIR / "terminology" / "glossary.json"

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
AUDIO_DIR = DATA_DIR / "audio"
NORMALIZED_DIR = DATA_DIR / "normalized"
TRANSLATED_DIR = DATA_DIR / "translated"
OUTPUT_DIR = DATA_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

# Development switches
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
