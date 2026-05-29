# Universal Translation Hub (UTH)

Hệ thống dịch thuật phổ quát đa phương tiện — Powered by Xiaomi MiMo V2.5 + Local AI Models.

**Tác giả:** Đoàn Minh Trí — DTHU University | **License:** MIT (2026)

## Tính năng

| Pipeline | Input | Output |
|----------|-------|--------|
| 🎮 **Game** | Game files (12 engines: RPG Maker, Unity, Ren'Py, Kirikiri...) | Localized Vietnamese game |
| 📖 **Manga** | Manga images (JPG, PNG, PDF) | Translated images with Vietnamese text |
| 🎬 **Film** | Video + subtitles (MKV, MP4, ASS, SRT) | Video with AI Vietnamese voiceover |

## Manga Pipeline

Hỗ trợ 2 chế độ:

| Engine | Mô tả | Ưu điểm |
|--------|-------|---------|
| **manga-image-translator** | Pipeline hoàn chỉnh (detection, OCR, inpainting, rendering, colorization) | Chất lượng cao, tự động |
| **Manual** | manga-ocr + OpenCV + provider | Fallback, tùy chỉnh cao |

## Cài đặt

```bash
cd XiaoMimo
pip install -r requirements.txt

# Optional
pip install manga-ocr    # Manga OCR (cho manual pipeline)
pip install pysubs2      # Subtitle parsing
```

## Sử dụng

```bash
# Auto-detect pipeline
python main.py --input "E:\Games\MyGame" --provider local

# Game
python main.py --mode game --input "E:\Games\MyGame" --provider local

# Manga (mặc định dùng manga-image-translator)
python main.py --mode manga --input "./manga_folder/" --source-lang ja

# Film
python main.py --mode film --input "./movie.mkv" --subtitle "./movie.ass"

# Demo
python main.py --demo
```

## Providers

| Provider | Mô tả | Yêu cầu |
|----------|-------|---------|
| `local` | AG-Translator backend (Dolphin/HyMT) | `cd E:\DichGame\Backend && python server.py` |
| `mimo` | Xiaomi MiMo V2.5 API | `MIMO_API_KEY` env |
| `auto` | Tự động chọn | Một trong hai |

## Kiến trúc

```
main.py → src/
  ├─ providers/     # Translation providers (MiMo + Local)
  ├─ pipelines/     # Game / Manga / Film pipelines
  │   └─ manga_image_translator_wrapper.py  # manga-image-translator integration
  ├─ agents/        # AI agent wrappers (Director, Translator, OCR, TTS, QA)
  ├─ memory/        # Translation Memory (SQLite)
  └─ utils/         # File detector, subtitle parser
```

## Web GUI

```bash
python server.py
# Mở http://localhost:8000
```

## Tài liệu

- [SRS](docs/vi/01-requirements-analysis-SRS.md) | [SAD](docs/vi/02-system-architecture-SAD.md) | [SDP](docs/vi/03-project-plan-SDP.md)
