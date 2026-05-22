<div align="center">

# Universal Translation Hub (UTH)

### Universal Multi-Media Translation System

**Powered by Xiaomi MiMo V2.5 — Multi-Agent Architecture**

![MiMo](https://img.shields.io/badge/Xiaomi_MiMo-V2.5_Pro-orange)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![Agents](https://img.shields.io/badge/AI_Agents-10-purple)
![Languages](https://img.shields.io/badge/Languages-6-red)

[Tiếng Việt](README.vn.md) | [中文](README.cn.md) | [Русский](README.ru.md) | [日本語](README.jp.md) | [한국어](README.kr.md)

</div>

---

## Overview

**Universal Translation Hub (UTH)** is a multi-agent AI system that automatically translates **3 types of multimedia content**:

| Pipeline | Input | Output |
|----------|-------|--------|
| **Game Translation** | Game files (12 engines: RPG Maker, Unity, Ren'Py, Kirikiri...) | Fully localized Vietnamese game |
| **Manga/Comic Translation** | Manga/comic images (JPG, PNG, PDF) | Translated images with rendered text |
| **Film/Video Dubbing** | Video + subtitles (MKV, MP4, ASS, SRT) | Video with AI Vietnamese voiceover |

### Why This Project?

> **Problem:** Millions of games, manga, and films from Japan, China, and Korea lack Vietnamese translations. Manual translation takes months, is expensive, and doesn't scale.

> **Solution:** UTH uses **10 AI Sub-Agents** working together automatically, powered by **Xiaomi MiMo V2.5**, to translate any multimedia content into Vietnamese in minutes.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIRECTOR AGENT                                │
│              (MiMo-V2.5-Pro — Flagship Reasoning)                │
│   Analyze request → Select pipeline → Coordinate 9 sub-agents   │
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
  │  └──────────┘ └──────────┘ └──────────┘ └─────────────────┘  │
  └───────────────────────────────────────────────────────────────┘
```

### 10 AI Sub-Agents

| # | Agent | MiMo Model | Role |
|---|-------|-----------|------|
| 1 | **Director** | MiMo-V2.5-Pro | Orchestration, reasoning, pipeline selection |
| 2 | **Router** | MiMo-V2.5 | Classify input → game/manga/film |
| 3 | **Translator** | MiMo-V2.5 | Multi-language translation (ZH/JA/KO/EN → VI) |
| 4 | **OCR Agent** | MiMo-V2.5 | Text recognition from images (manga) & video (subtitle) |
| 5 | **Inpainting Agent** | MiMo-V2.5 | Remove original text, restore background |
| 6 | **Render Agent** | MiMo-V2.5 | Render translated text into images |
| 7 | **STT Agent** | MiMo-V2.5 | Speech-to-text conversion |
| 8 | **Voice Agent** | MiMo-V2.5-TTS | Basic TTS — subtitle reading, narration |
| 9 | **Voice Clone** | MiMo-TTS-VoiceClone | Character voice cloning |
| 10 | **QA Agent** | MiMo-V2.5 | Translation quality assessment |

---

## Xiaomi MiMo Integration

### Models Used (8/8)

| Model | Usage | Est. Credits/Month |
|-------|-------|-------------------|
| **MiMo-V2.5-Pro** | Director Agent — complex reasoning | ~50M |
| **MiMo-V2.5** | Translator, OCR, QA, Router, Inpainting, Render, STT | ~200M |
| **MiMo-V2.5-TTS** | Voice Agent — basic TTS | ~30M |
| **MiMo-TTS-VoiceClone** | Character voice cloning | ~10M |
| **MiMo-TTS-VoiceDesign** | New voice creation for NPCs/narrator | ~5M |
| **Total** | | **~295M/month** |

> **Max Plan (1.6B credits/month)** — Uses ~18% capacity, plenty for batch processing and scaling.

### Why MiMo?

1. **MiMo-V2.5-Pro** — Flagship model with strong reasoning, perfect for Director Agent
2. **MiMo-V2.5** — Full-modal base model, understands both text and images — ideal for OCR + Translation
3. **MiMo TTS Series** — 3 TTS models (basic, clone, design) — covers all voiceover scenarios
4. **Off-peak 20% off** — Batch processing during US daytime saves costs
5. **8 models in 1 plan** — No need to integrate multiple providers

---

## Current Status

UTH is built on top of **3 existing projects**:

| Source Project | Status | Contribution to UTH |
|---------------|--------|---------------------|
| **MIMO-AXON** (Film Dubbing) | Beta 1.0.4 | Film pipeline, VLC integration, TTS engines |
| **Antigravity Game Translator** | In development | Game pipeline, 12 engines, Smart Pipeline |
| **manga-image-translator** | Stable | Manga pipeline, OCR, Inpainting, Rendering |

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/universal-translation-hub.git
cd universal-translation-hub
pip install -r requirements.txt
cp .env.example .env
# Edit .env: MIMO_API_KEY=your_key_here
python main.py
```

---

## Roadmap

| Phase | Timeline | Focus |
|-------|----------|-------|
| Phase 1 | Month 1-2 | Foundation, MiMo API integration |
| Phase 2 | Month 3-4 | Pipeline integration (Game, Manga, Film) |
| Phase 3 | Month 5-6 | Voice & Quality (TTS, QA, Glossary) |
| Phase 4 | Month 7-8 | Polish & Release v1.0 |

---

## Author

**Đoàn Minh Trí** — DTHU University

---

## License

MIT License — See [LICENSE](LICENSE) for details.

---

<div align="center">

**Powered by Xiaomi MiMo V2.5 | Built with ❤️ for the Vietnamese gaming & anime community**

</div>
