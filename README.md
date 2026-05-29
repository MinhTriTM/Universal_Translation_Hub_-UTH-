<<<<<<< HEAD
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
=======
<div align="center">

# Universal Translation Hub (UTH)

### Hệ Thống Dịch Thuật Phổ Quát Đa Phương Tiện

**Powered by Xiaomi MiMo V2.5 — Multi-Agent Architecture**

![MiMo](https://img.shields.io/badge/Xiaomi_MiMo-V2.5_Pro-orange)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![Agents](https://img.shields.io/badge/AI_Agents-10-purple)
![Languages](https://img.shields.io/badge/Languages-6-red)

[English](README.en.md) | [中文](README.cn.md) | [Русский](README.ru.md) | [日本語](README.jp.md) | [한국어](README.kr.md)

</div>

---

## Tổng Quan

**Universal Translation Hub (UTH)** là hệ thống AI đa tác nhân (multi-agent) tổng hợp, có khả năng dịch thuật tự động cho **3 loại nội dung đa phương tiện**:

| Pipeline | Input | Output |
|----------|-------|--------|
| **Game Translation** | File game (12 engines: RPG Maker, Unity, Ren'Py, Kirikiri...) | Game đã Việt hóa hoàn chỉnh |
| **Manga/Comic Translation** | Ảnh manga/comic (JPG, PNG, PDF) | Ảnh đã dịch + render text mới |
| **Film/Video Dubbing** | Video + phụ đề (MKV, MP4, ASS, SRT) | Video có thuyết minh tiếng Việt AI |

### Tại Sao Cần Dự Án Này?

> **Vấn đề:** Hàng triệu game, manga, và phim từ Nhật Bản, Trung Quốc, Hàn Quốc chưa có bản dịch tiếng Việt. Dịch thủ công mất hàng tháng, chi phí cao, và không scalable.

> **Giải pháp:** UTH sử dụng **10 AI Sub-Agents** phối hợp tự động, powered by **Xiaomi MiMo V2.5**, để dịch bất kỳ nội dung đa phương tiện nào sang tiếng Việt trong vài phút.

---

## Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIRECTOR AGENT                                │
│              (MiMo-V2.5-Pro — Flagship Reasoning)                │
│   Phân tích yêu cầu → Chọn pipeline → Điều phối 9 sub-agents   │
└──────────┬──────────────┬──────────────┬────────────────────────┘
           │              │              │
  ┌────────▼────────┐ ┌──▼──────────┐ ┌▼──────────────┐
  │  GAME PIPELINE  │ │ MANGA PIPE  │ │  FILM PIPELINE │
  │  (12 engines)   │ │ (OCR+Render)│ │  (STT+TTS)     │
  └────────┬────────┘ └──┬──────────┘ └┬──────────────┘
           │              │              │
  ┌────────▼──────────────▼──────────────▼────────────────────────┐
  │              SHARED SERVICES LAYER                             │
  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐  │
  │  │Unified   │ │Translation│ │Glossary  │ │ MiMo Voice      │  │
  │  │Translator│ │Memory    │ │Manager   │ │ Engine (TTS)    │  │
  │  │(MiMo-V2) │ │(SQLite)  │ │(JSON)    │ │ (3 TTS models)  │  │
  │  └──────────┘ └──────────┘ └──────────┘ └─────────────────┘  │
  └───────────────────────────────────────────────────────────────┘
```

### 10 AI Sub-Agents

| # | Agent | Model MiMo | Vai trò |
|---|-------|-----------|---------|
| 1 | **Director** | MiMo-V2.5-Pro | Điều phối, reasoning, quyết định pipeline |
| 2 | **Router** | MiMo-V2.5 | Phân loại input → game/manga/film |
| 3 | **Translator** | MiMo-V2.5 | Dịch text đa ngôn ngữ (ZH/JA/KO/EN → VI) |
| 4 | **OCR Agent** | MiMo-V2.5 | Nhận diện text từ ảnh (manga) & video (subtitle) |
| 5 | **Inpainting Agent** | MiMo-V2.5 | Xóa text gốc khỏi ảnh, khôi phục nền |
| 6 | **Render Agent** | MiMo-V2.5 | Render text dịch vào ảnh/video |
| 7 | **STT Agent** | MiMo-V2.5 | Speech-to-text (chuyển giọng nói → text) |
| 8 | **Voice Agent** | MiMo-V2.5-TTS | TTS cơ bản — đọc phụ đề, thuyết minh |
| 9 | **Voice Clone** | MiMo-TTS-VoiceClone | Clone giọng — lồng tiếng nhân vật |
| 10 | **QA Agent** | MiMo-V2.5 | Đánh giá chất lượng bản dịch, phát hiện lỗi |

---

## Tích Hợp Xiaomi MiMo

### Models Sử Dụng (8/8 Models)

| Model | Sử dụng | Credits/tháng ước tính |
|-------|---------|----------------------|
| **MiMo-V2.5-Pro** | Director Agent — reasoning phức tạp | ~50M |
| **MiMo-V2.5** | Translator, OCR, QA, Router, Inpainting, Render, STT | ~200M |
| **MiMo-V2.5-TTS** | Voice Agent — TTS cơ bản | ~30M |
| **MiMo-V2.5-TTS-VoiceClone** | Clone giọng nhân vật | ~10M |
| **MiMo-V2.5-TTS-VoiceDesign** | Tạo giọng mới cho NPC/narrator | ~5M |
| **Tổng** | | **~295M/tháng** |

> **Gói Max (1.6B credits/tháng)** — Sử dụng ~18% capacity, còn dư cho batch processing và scaling.

### Tại Sao Chọn MiMo?

1. **MiMo-V2.5-Pro** — Model flagship với reasoning能力 mạnh, phù hợp cho Director Agent
2. **MiMo-V2.5** — Full-modal base model, hiểu cả text lẫn hình ảnh → lý tưởng cho OCR + Translation
3. **MiMo TTS Series** — 3 model TTS (basic, clone, design) → đủ cho mọi kịch bản lồng tiếng
4. **Off-peak 20% off** — Batch processing ban ngày Mỹ → tiết kiệm chi phí
5. **8 models trong 1 gói** — Không cần tích hợp nhiều provider, đơn giản hóa kiến trúc

---

## Trạng Thái Hiện Tại

Dự án UTH được xây dựng trên nền tảng **3 dự án đã có**:

| Dự án gốc | Trạng thái | Đóng góp cho UTH |
|-----------|-----------|------------------|
| **MIMO-AXON** (Film Dubbing) | Beta 1.0.4 | Film pipeline, VLC integration, TTS engines |
| **Antigravity Game Translator** | Đang phát triển | Game pipeline, 12 engines, Smart Pipeline |
| **manga-image-translator** | Ổn định | Manga pipeline, OCR, Inpainting, Rendering |

### Tính Năng Đã Có

- [x] 12 game engines (RPG Maker, Unity, Ren'Py, Kirikiri, CatSystem2, NScripter, TyranoBuilder, Web, NW.js, Wolf RPG, Binary)
- [x] Manga translation pipeline (5 detectors, 4 OCR models, 5 inpainters, 20+ translators)
- [x] Film dubbing với Edge-TTS, Google Cloud TTS, Piper, MeloTTS
- [x] VLC integration (realtime dubbing daemon)
- [x] Translation Memory cache (SQLite + JSON)
- [x] Vietnamese font handling (detect, subset, embed)

### Tính Năng Cần Phát Triển (cho UTH)

- [ ] Unified Director Agent (MiMo-V2.5-Pro)
- [ ] Shared Translation Memory xuyên 3 pipelines
- [ ] MiMo TTS integration (thay thế Edge-TTS/Google TTS)
- [ ] MiMo-V2.5 translation provider (thay thế Dolphin GGUF)
- [ ] Unified Dashboard
- [ ] Glossary Manager thống nhất
- [ ] QA Agent tự động đánh giá bản dịch

---

## Cài Đặt & Sử Dụng

### Yêu cầu hệ thống

| Component | Tối thiểu | Khuyến nghị |
|-----------|-----------|-------------|
| OS | Windows 10 / Ubuntu 22.04 | Windows 11 |
| Python | 3.10+ | 3.12 |
| GPU | GTX 1060 6GB | RTX 4060 8GB+ |
| RAM | 8GB | 16GB+ |
| Storage | 10GB | 50GB (cho models) |

### Cài đặt nhanh

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/universal-translation-hub.git
cd universal-translation-hub

# Cài dependencies
pip install -r requirements.txt

# Cấu hình API key
cp .env.example .env
# Edit .env: MIMO_API_KEY=your_key_here

# Chạy demo
python main.py
```

### Sử dụng

```bash
# Dịch game
python main.py --mode game --input "E:\DichGame\Sordce_Games\MyGame"

# Dịch manga
python main.py --mode manga --input "./manga_chapter_01/"

# Dịch film + thuyết minh
python main.py --mode film --input "./movie.mkv" --subtitle "./movie.ass"
```

---

## Cấu Trúc Thư Mục

```
universal-translation-hub/
├── README.vn.md          # ← Bạn đang đọc
├── README.en.md          # English
├── README.cn.md          # 中文
├── README.ru.md          # Русский
├── README.jp.md          # 日本語
├── README.kr.md          # 한국어
├── requirements.txt      # Python dependencies
├── .env.example          # Template API keys
├── main.py               # Entry point + Demo
├── src/
│   ├── __init__.py
│   ├── agents/           # 10 AI Agents
│   │   ├── director.py   # Director Agent (MiMo-V2.5-Pro)
│   │   ├── router.py     # Router Agent
│   │   ├── translator.py # Unified Translator
│   │   └── ...
│   ├── pipelines/        # 3 Translation Pipelines
│   │   ├── game/         # Game pipeline (12 engines)
│   │   ├── manga/        # Manga pipeline (OCR+Render)
│   │   └── film/         # Film pipeline (STT+TTS)
│   ├── services/         # Shared Services
│   │   ├── memory.py     # Translation Memory (SQLite)
│   │   ├── glossary.py   # Glossary Manager
│   │   └── mimo_client.py # MiMo API Client
│   └── utils/            # Utilities
├── docs/                 # Tài liệu kỹ thuật
│   ├── SRS.md            # Software Requirements Specification
│   ├── SAD.md            # Software Architecture Document
│   ├── SDP.md            # Software Development Plan
│   ├── FEASIBILITY.md    # Feasibility Study
│   └── RESOURCES.md      # Tài nguyên & Tham khảo
├── demo/                 # Demo scripts
│   └── demo_mimo.py      # Demo MiMo API
├── assets/               # Hình ảnh, diagrams
└── tests/                # Unit tests
```

---

## Lộ Trình Phát Triển

### Phase 1: Foundation (Tháng 1-2)
- Thiết lập MiMo API client
- Tạo Director Agent (MiMo-V2.5-Pro)
- Unified Translation Memory
- Tích hợp MiMo-V2.5 làm translator chính

### Phase 2: Pipeline Integration (Tháng 3-4)
- Tích hợp Game pipeline (từ DichGame)
- Tích hợp Manga pipeline (từ manga-image-translator)
- Tích hợp Film pipeline (từ MIMO-AXON)
- Router Agent phân loại tự động

### Phase 3: Voice & Quality (Tháng 5-6)
- MiMo TTS integration (basic + clone + design)
- QA Agent đánh giá bản dịch
- Glossary Manager thống nhất
- Volume ducking & audio sync

### Phase 4: Production (Tháng 7-8)
- Unified Dashboard (web UI)
- Batch processing mode
- Performance optimization
- Documentation & Release

---

## Đóng Góp Cho Xiaomi MiMo 100T

Dự án UTH đóng góp cho hệ sinh thái MiMo theo nhiều cách:

1. **Sử dụng 8/8 MiMo models** — Showcase toàn bộ năng lực của MiMo ecosystem
2. **Multi-agent architecture** — Mẫu hình (pattern) cho cộng đồng xây dựng AI agents với MiMo
3. **Open source** — Cộng đồng có thể học và đóng góp
4. **Use case thực tế** — Game/Manga/Film translation là nhu cầu lớn ở Đông Nam Á
5. **Token consumption** — Ước tính ~295M credits/tháng (~18% gói Max)

---

## Tác Giả

**Đoàn Minh Trí** — DTHU University

- GitHub: [@MinhTriTM](https://github.com/MinhTriTM)
- Email: [0024417136@student.dthu.edu.vn](mailto:0024417136@student.dthu.edu.vn)

---

## License

MIT License — Xem [LICENSE](LICENSE) để biết chi tiết.

---

<div align="center">

**Powered by Xiaomi MiMo V2.5 | Built with ❤️ for the Vietnamese gaming & anime community**

</div>
>>>>>>> 403949b0fcc53fe80bae33b2b14dfd04c8756fcc
