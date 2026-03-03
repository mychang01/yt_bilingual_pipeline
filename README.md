# YouTube 雙語字幕流程（EN -> ZH）

將 YouTube 影片或本地音訊轉為中英雙語字幕的可執行流程。  
本專案使用 `yt-dlp` 下載/擷取字幕、OpenAI Whisper 做語音轉寫、GPT 產生中文字幕，最終輸出 `.srt` 與 `.json`。

## 專案簡介（繁體中文）

這是一個以「可落地執行」為核心的字幕管線：

1. 優先讀取 YouTube 原生字幕（含自動字幕）
2. 若無字幕則下載音訊並執行 ASR（Whisper）
3. 清洗英文字幕（移除口頭禪、修正時間軸、切分長句）
4. 翻譯為中文（可套用術語表）
5. 輸出雙語結果（SRT + JSON）

適合情境：雙語學習、內容在地化、課程逐字稿、短影音字幕製作。

## English Overview

This project is a practical pipeline for generating bilingual subtitles:

1. Try native YouTube subtitles first
2. Fallback to audio download + Whisper ASR if subtitles are unavailable
3. Normalize subtitle segments (filler removal, timestamp fixing, long-line split)
4. Translate to Chinese with prompt + glossary
5. Export bilingual outputs as `.srt` and `.json`

## 功能特色

- 輸入模式：
  - 單一 YouTube 連結
  - 批次網址檔（每行一個 URL）
  - 本地音訊檔
- 自動回退邏輯：
  - 有字幕：直接擷取並解析
  - 無字幕：下載音訊 + Whisper 轉寫
- 輸出格式：
  - 雙語 `.srt`
  - 結構化 `.json`
- 環境參數可配置：
  - 模型、重試策略、字幕切分上限

## 檔案架構圖（Architecture Map）

```text
yt_bilingual_pipeline/
├── main.py                     # CLI 入口與整體流程編排
├── config.py                   # .env 載入、模型/路徑/重試設定
├── requirements.txt            # 相依套件
├── .env.example                # 環境變數範本
├── prompts/
│   └── translate_prompt.txt    # 翻譯提示詞模板
├── terminology/
│   └── glossary.json           # 術語表（提升翻譯一致性）
├── core/
│   ├── __init__.py
│   ├── downloader.py           # YouTube 字幕/音訊擷取（yt-dlp）
│   ├── asr.py                  # Whisper 轉寫客戶端
│   ├── normalizer.py           # 英文字幕清洗與時間軸修正
│   ├── translator.py           # GPT 翻譯
│   ├── assembler.py            # 輸出 SRT/JSON 組裝
│   └── utils.py                # 重試、JSON、時間格式等工具
├── data/
│   ├── raw/                    # 下載到的字幕原檔（.vtt/.srt）
│   ├── audio/                  # 下載到的音訊
│   ├── normalized/             # 清洗後字幕（json）
│   ├── translated/             # 翻譯後字幕（json）
│   └── output/                 # 最終雙語輸出（.srt/.json）
└── logs/                       # 預留日誌資料夾
```

## Project Structure (English)

```text
yt_bilingual_pipeline/
├── main.py                     # CLI entrypoint and pipeline orchestration
├── config.py                   # .env loading, model/path/retry settings
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── prompts/
│   └── translate_prompt.txt    # Translation prompt template
├── terminology/
│   └── glossary.json           # Domain glossary for translation consistency
├── core/
│   ├── __init__.py
│   ├── downloader.py           # YouTube subtitle/audio retrieval (yt-dlp)
│   ├── asr.py                  # Whisper transcription client
│   ├── normalizer.py           # Subtitle cleanup and timestamp normalization
│   ├── translator.py           # GPT translation
│   ├── assembler.py            # Bilingual SRT/JSON assembly
│   └── utils.py                # Retry, JSON, and time-format helpers
├── data/
│   ├── raw/                    # Downloaded subtitle files (.vtt/.srt)
│   ├── audio/                  # Downloaded audio artifacts
│   ├── normalized/             # Normalized subtitle JSON
│   ├── translated/             # Translated subtitle JSON
│   └── output/                 # Final bilingual outputs (.srt/.json)
└── logs/                       # Reserved log directory
```

## 流程圖（Processing Flow）

```text
輸入（--url / --folder / --audio）
        |
        v
[downloader.process(url)] ---- 找到字幕？ ---- 是 --> 解析字幕
        | 否
        v
[download_audio + asr.transcribe]
        |
        v
[normalizer.clean]
        |
        v
[translator.batch_translate]
        |
        v
[assembler.generate_srt / generate_json]
        |
        v
data/output/*.bilingual.srt + *.bilingual.json
```

## 執行需求

- 建議 Python 3.10 以上
- 建議系統可用 `ffmpeg`（音訊處理較穩定）
- 可用的 OpenAI API Key
- 可連線 YouTube 與 OpenAI API

## 安裝方式

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 環境變數

`.env` 範例：

```bash
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=
ASR_MODEL=whisper-1
TRANSLATE_MODEL=gpt-4.1-mini

MAX_RETRY=3
RETRY_BACKOFF_SECONDS=1
MAX_WORDS_PER_LINE=20

MOCK_MODE=false
```

說明：

- `OPENAI_BASE_URL` 留空時，預設使用官方 OpenAI 端點。
- `MOCK_MODE=true` 可跳過真實 API 呼叫，便於本地測試流程。

## 使用方式

### 1. 單一 YouTube 連結

```bash
python3 main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. 批次網址檔

`urls.txt` 範例：

```txt
https://www.youtube.com/watch?v=AAAA
https://www.youtube.com/watch?v=BBBB
# 這行是註解
```

執行：

```bash
python3 main.py --folder urls.txt
```

### 3. 本地音訊檔

```bash
python3 main.py --audio /path/to/audio.mp3 --name custom_output_name
```

## Usage (English)

### 1. Process a single YouTube URL

```bash
python3 main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. Process a batch URL file

`urls.txt` example:

```txt
https://www.youtube.com/watch?v=AAAA
https://www.youtube.com/watch?v=BBBB
# comment line
```

Run:

```bash
python3 main.py --folder urls.txt
```

### 3. Process a local audio file

```bash
python3 main.py --audio /path/to/audio.mp3 --name custom_output_name
```

## 輸出內容

每個處理項目會產生：

- `data/normalized/<stem>.normalized.json`
- `data/translated/<stem>.translated.json`
- `data/output/<stem>.bilingual.srt`
- `data/output/<stem>.bilingual.json`

## 常見問題排查

- `OPENAI_API_KEY is missing`
  - 檢查 `.env` 是否設定，並確認 key 有效。
- `yt-dlp` 下載失敗（含 403）
  - 先更新 `yt-dlp`，再重試。
  - 檢查網路與區域限制。
- OpenAI 連線錯誤
  - 確認能連外至 OpenAI。
  - 若透過代理/閘道，請設定有效的 `OPENAI_BASE_URL`（需含 `https://`）。

## 隱私與成本提醒

- 當 `MOCK_MODE=false` 時，音訊/文字內容會送至 OpenAI 進行轉寫與翻譯。
- API 呼叫會依模型與資料量產生成本，請自行控管使用量。

## 授權

請自行補上授權條款（例如 MIT）。
