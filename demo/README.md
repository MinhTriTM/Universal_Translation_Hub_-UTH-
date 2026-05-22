# MIMO-AXON Demo

Demo tổng hợp hệ sinh thái AI đa tác nhân — copy files cần thiết từ 3 dự án nguồn.

## Dự án nguồn

| Dự án | Đường dẫn | Chức năng |
|-------|----------|-----------|
| XiaoMi100T | `D:\Du_An_Mini\XiaoMi100T` | OCR + Dubbing (Gemini API) |
| DichGame | `E:\DichGame` | Game Translation Engine (LLM) |
| manga-image-translator | `E:\DichGame\Tool\manga-image-translator` | Manga/Comic Translation |

## Cài đặt

```bash
# 1. Copy files từ 3 dự án
python demo/setup.py

# 2. (Tùy chọn) Xem trước không copy
python demo/setup.py --dry-run

# 3. Chạy demo
python demo/run_demo.py
```

## Cấu trúc sau khi setup

```
demo/
├── setup.py              # Script copy files
├── run_demo.py           # Demo chính
├── README.md             # File này
├── MANIFEST.md           # Danh sách file đã copy (auto-generated)
├── xiaomi_mimo/          # Files từ XiaoMi100T
│   ├── ocr_engine.py
│   ├── dubbing_tmf.py
│   ├── dubbing_google_tts.py
│   ├── .env.example
│   └── requirements.txt
├── dichgame/             # Files từ DichGame
│   ├── server.py
│   ├── engines_logic.py
│   ├── requirements.txt
│   └── modules_core/
└── manga_translator/     # Files từ manga-image-translator
    ├── __init__.py
    ├── server/
    ├── requirements.txt
    └── .env.example
```

## Sử dụng

```bash
# Kiểm tra hệ thống
python demo/run_demo.py --check

# Xem kiến trúc modules
python demo/run_demo.py --show-modules

# Demo tương tác
python demo/run_demo.py --interactive
```

## Kiến trúc

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   XiaoMi100T    │     │    DichGame     │     │  Manga-Translator│
│  (Video/Sub)    │     │  (Game Files)   │     │  (Comic Images)  │
└────────┬────────┘     └────────┬────────┘     └────────┬─────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Gemini 2.5     │     │  LLM Engine     │     │  OCR + Inpaint  │
│  Flash Lite     │     │  (llama-cpp)    │     │  (manga-ocr)    │
└────────┬────────┘     └────────┬────────┘     └────────┬─────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Edge TTS /     │     │  Translated     │     │  Translated     │
│  Google Cloud   │     │  Game Scripts   │     │  Comic Pages    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Tác giả

**Đoàn Minh Trí** — DTHU University
