from __future__ import annotations

import argparse
from pathlib import Path

from config import NORMALIZED_DIR, OUTPUT_DIR, TRANSLATED_DIR
from core import asr, assembler, downloader, normalizer, translator, utils


def process_one_url(url: str, output_stem: str | None = None) -> tuple[Path, Path]:
    subtitles = downloader.process(url)

    if subtitles is None:
        audio_path = downloader.download_audio(url)
        subtitles = asr.transcribe(audio_path)

    normalized = normalizer.clean(subtitles)
    translated = translator.batch_translate(normalized)

    stem = output_stem or utils.safe_stem_from_url(url)
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    TRANSLATED_DIR.mkdir(parents=True, exist_ok=True)

    utils.write_json(NORMALIZED_DIR / f"{stem}.normalized.json", normalized)
    utils.write_json(TRANSLATED_DIR / f"{stem}.translated.json", translated)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    srt_path = OUTPUT_DIR / f"{stem}.bilingual.srt"
    json_path = OUTPUT_DIR / f"{stem}.bilingual.json"

    assembler.generate_srt(translated, srt_path)
    assembler.generate_json(translated, json_path)

    return srt_path, json_path


def process_one_audio(audio_path: Path, output_stem: str | None = None) -> tuple[Path, Path]:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    subtitles = asr.transcribe(audio_path)
    normalized = normalizer.clean(subtitles)
    translated = translator.batch_translate(normalized)

    stem = output_stem or audio_path.stem
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    TRANSLATED_DIR.mkdir(parents=True, exist_ok=True)

    utils.write_json(NORMALIZED_DIR / f"{stem}.normalized.json", normalized)
    utils.write_json(TRANSLATED_DIR / f"{stem}.translated.json", translated)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    srt_path = OUTPUT_DIR / f"{stem}.bilingual.srt"
    json_path = OUTPUT_DIR / f"{stem}.bilingual.json"

    assembler.generate_srt(translated, srt_path)
    assembler.generate_json(translated, json_path)

    return srt_path, json_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YouTube bilingual subtitle pipeline (Whisper + ChatGPT)")
    parser.add_argument("--url", help="Single YouTube URL")
    parser.add_argument("--folder", help="Text file containing URLs (one per line)")
    parser.add_argument("--audio", help="Local audio file path")
    parser.add_argument("--name", help="Output name stem for single URL/audio")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected_count = sum(bool(x) for x in (args.url, args.folder, args.audio))
    if selected_count != 1:
        raise SystemExit("Use exactly one of --url, --folder, or --audio")

    if args.url:
        srt_path, json_path = process_one_url(args.url, args.name)
        print(f"Done: {srt_path}")
        print(f"Done: {json_path}")
        return

    if args.audio:
        srt_path, json_path = process_one_audio(Path(args.audio), args.name)
        print(f"Done: {srt_path}")
        print(f"Done: {json_path}")
        return

    urls = [line.strip() for line in Path(args.folder).read_text(encoding="utf-8").splitlines()]
    urls = [u for u in urls if u and not u.startswith("#")]

    for idx, url in enumerate(urls, start=1):
        stem = f"batch_{idx:03d}_{utils.safe_stem_from_url(url)}"
        try:
            srt_path, json_path = process_one_url(url, stem)
            print(f"[{idx}/{len(urls)}] Done: {srt_path.name}, {json_path.name}")
        except Exception as exc:  # noqa: BLE001
            print(f"[{idx}/{len(urls)}] Failed: {url} -> {exc}")


if __name__ == "__main__":
    main()
