# Resources and References

## Universal Translation Hub (UTH)

**Version:** 1.0
**Date:** 2026-05-22
**Author:** Doan Minh Tri — DTHU University
**AI Platform:** Xiaomi MiMo V2.5

---

## Table of Contents

1. [AI Platform — Xiaomi MiMo V2.5](#1-ai-platform--xiaomi-mimo-v25)
2. [Source Projects](#2-source-projects)
3. [Core Technologies](#3-core-technologies)
4. [AI and Machine Learning Models](#4-ai-and-machine-learning-models)
5. [Game Engine Documentation](#5-game-engine-documentation)
6. [Image Processing Tools](#6-image-processing-tools)
7. [Audio and Video Processing Tools](#7-audio-and-video-processing-tools)
8. [Web and API Frameworks](#8-web-and-api-frameworks)
9. [Database and Storage](#9-database-and-storage)
10. [Development Tools](#10-development-tools)
11. [Standards and Specifications](#11-standards-and-specifications)
12. [Academic and Research References](#12-academic-and-research-references)
13. [Community Resources](#13-community-resources)

---

## 1. AI Platform — Xiaomi MiMo V2.5

### 1.1 Official Documentation

| Resource | URL | Description |
|----------|-----|-------------|
| MiMo V2.5 Official Page | https://mimo.xiaomi.com | Product overview, features, pricing |
| MiMo API Documentation | https://mimo.xiaomi.com/docs/api | API reference for all 5 models |
| MiMo Developer Portal | https://developer.mimo.xiaomi.com | API key management, usage dashboard |
| MiMo GitHub | https://github.com/XiaoMi/MiMo | Official SDKs and examples |

### 1.2 MiMo V2.5 Models

| Model | ID | Purpose | Documentation |
|-------|----|---------|---------------|
| **MiMo V2.5-Pro** | `mimo-v2.5-pro` | Translation, text analysis, reasoning | [API Docs](https://mimo.xiaomi.com/docs/api/v2.5-pro) |
| **MiMo V2.5** | `mimo-v2.5` | OCR, VQA, image understanding, multimodal | [API Docs](https://mimo.xiaomi.com/docs/api/v2.5) |
| **MiMo TTS** | `mimo-tts` | Text-to-speech synthesis | [API Docs](https://mimo.xiaomi.com/docs/api/tts) |
| **MiMo VoiceClone** | `mimo-voice-clone` | Voice characteristic cloning | [API Docs](https://mimo.xiaomi.com/docs/api/voice-clone) |
| **MiMo VoiceDesign** | `mimo-voice-design` | Custom voice profile creation | [API Docs](https://mimo.xiaomi.com/docs/api/voice-design) |

### 1.3 MiMo API Integration

```
Base URL:       https://api.mimo.xiaomi.com/v1
Auth:           Bearer token (API key)
Format:         OpenAI-compatible (chat/completions endpoint)
Rate Limits:    Varies by plan (see pricing page)
SDK Support:    Python, JavaScript, Go
```

**Python SDK Installation:**
```bash
pip install mimo-sdk
```

**Basic Usage:**
```python
from mimo import MiMoClient

client = MiMoClient(api_key="your-api-key")

# Translation
result = await client.chat_completion(
    model="mimo-v2.5-pro",
    messages=[{"role": "user", "content": "Translate to Vietnamese: Hello world"}]
)

# OCR
text_regions = await client.ocr(
    model="mimo-v2.5",
    image="manga_page.png",
    lang="ja"
)

# TTS
audio = await client.tts(
    text="Xin chào thế giới",
    voice="vi-VN-Standard"
)
```

---

## 2. Source Projects

### 2.1 DichGame — Game Translation Pipeline

| Resource | URL | Description |
|----------|-----|-------------|
| GitHub Repository | https://github.com/user/dichgame | Main repository |
| Documentation | https://github.com/user/dichgame/wiki | Setup and usage guide |
| Issues | https://github.com/user/dichgame/issues | Bug reports and feature requests |

**Key Components Reused:**
- 12 game engine handlers (RPG Maker, Ren'Py, Unity, etc.)
- Text extraction and re-injection logic
- File format parsers (JSON, rvdata2, binary)
- Translation memory implementation

**Supported Engines:**
| Engine | File Formats | Status |
|--------|-------------|--------|
| RPG Maker MV/MZ | `.json` (data/*.json) | Stable |
| RPG Maker VX/Ace | `.rvdata2` | Stable |
| RPG Maker XP | `.rxdata` | Stable |
| RPG Maker 2003 | `.ldb`, `.lmt` | Stable |
| Ren'Py | `.rpy` | Stable |
| Unity | `.assets`, `.json` | Beta |
| Unreal Engine | `.locres`, `.po` | Beta |
| NScripter | `.nscr`, `.txt` | Stable |
| KiriKiri | `.ks`, `.tjs` | Stable |
| Wolf RPG | `.dat` | Stable |
| TyranoBuilder | `.tyrano`, `.json` | Alpha |
| GameMaker Studio | `.yy`, `.gml` | Alpha |

### 2.2 manga-image-translator — Manga Translation Pipeline

| Resource | URL | Description |
|----------|-----|-------------|
| GitHub Repository | https://github.com/zyddnys/manga-image-translator | Main repository |
| Documentation | https://github.com/zyddnys/manga-image-translator/wiki | Setup guide |
| Demo | https://cotrans.touhou.ai | Online demo |

**Key Components Reused:**
- Text detection (scene text detection models)
- OCR engine integration
- Inpainting algorithms (multiple backends)
- Text rendering with font support
- Bubble detection and segmentation

**Supported Features:**
| Feature | Status | Notes |
|---------|--------|-------|
| Text Detection | Stable | Mask-based and CRAFT detectors |
| OCR | Stable | Multiple OCR backends |
| Inpainting | Stable | AOT, Lama, SD-based |
| Text Rendering | Stable | Auto-sizing, styling |
| Vertical Text | Stable | Japanese/Chinese vertical layouts |
| Color Manga | Stable | Full color support |
| Grayscale Manga | Stable | Black and white support |

### 2.3 MIMO-AXON — Film Translation Pipeline

| Resource | URL | Description |
|----------|-----|-------------|
| GitHub Repository | https://github.com/user/mimo-axon | Main repository |
| Documentation | https://github.com/user/mimo-axon/wiki | Setup guide |

**Key Components Reused:**
- Audio extraction via FFmpeg
- Speech-to-text integration
- Subtitle generation (SRT/VTT)
- Basic TTS integration
- Audio mixing and video muxing

---

## 3. Core Technologies

### 3.1 Python

| Resource | URL | Description |
|----------|-----|-------------|
| Python 3.12 Documentation | https://docs.python.org/3.12/ | Official documentation |
| Python 3.12 Release Notes | https://docs.python.org/3.12/whatsnew/3.12.html | New features |
| asyncio Documentation | https://docs.python.org/3.12/library/asyncio.html | Async I/O |
| PyPI | https://pypi.org | Package repository |

**Key Python Features Used:**
- `asyncio` for concurrent I/O operations
- `dataclasses` for data models
- `typing` for type hints
- `pathlib` for file system operations
- `tomllib` for TOML configuration parsing
- `sqlite3` for database access

### 3.2 FastAPI

| Resource | URL | Description |
|----------|-----|-------------|
| FastAPI Documentation | https://fastapi.tiangolo.com/ | Official documentation |
| FastAPI GitHub | https://github.com/tiangolo/fastapi | Source code |
| FastAPI Tutorial | https://fastapi.tiangolo.com/tutorial/ | Getting started |
| Pydantic Documentation | https://docs.pydantic.dev/ | Data validation |

**Installation:**
```bash
pip install fastapi uvicorn[standard]
```

**Basic Usage:**
```python
from fastapi import FastAPI

app = FastAPI(title="Universal Translation Hub")

@app.post("/api/v1/translate/game")
async def translate_game(game_path: str, engine: str = "auto"):
    # Translation logic
    pass
```

### 3.3 SQLite

| Resource | URL | Description |
|----------|-----|-------------|
| SQLite Documentation | https://www.sqlite.org/docs.html | Official documentation |
| SQLite Python Tutorial | https://docs.python.org/3.12/library/sqlite3.html | Python integration |

**Key Features Used:**
- WAL mode for concurrent read/write
- Full-text search for translation memory
- JSON extension for complex data

### 3.4 SQLAlchemy

| Resource | URL | Description |
|----------|-----|-------------|
| SQLAlchemy Documentation | https://docs.sqlalchemy.org/ | Official documentation |
| SQLAlchemy 2.0 Migration | https://docs.sqlalchemy.org/en/20/changelog/migration_20.html | Migration guide |

**Installation:**
```bash
pip install sqlalchemy>=2.0
```

### 3.5 Alembic

| Resource | URL | Description |
|----------|-----|-------------|
| Alembic Documentation | https://alembic.sqlalchemy.org/ | Official documentation |

**Installation:**
```bash
pip install alembic
```

---

## 4. AI and Machine Learning Models

### 4.1 Translation Models

| Model | Provider | URL | Use Case |
|-------|----------|-----|----------|
| MiMo V2.5-Pro | Xiaomi | https://mimo.xiaomi.com | Primary translation engine |
| GPT-4 | OpenAI | https://openai.com/gpt-4 | Fallback/alternative |
| Claude | Anthropic | https://claude.ai | Fallback/alternative |
| NLLB-200 | Meta | https://github.com/facebookresearch/fairseq/tree/nllb | Local fallback (open-source) |

### 4.2 OCR Models

| Model | URL | Use Case |
|-------|-----|----------|
| MiMo V2.5 | https://mimo.xiaomi.com | Primary OCR engine |
| EasyOCR | https://github.com/JaidedAI/EasyOCR | Local OCR fallback |
| PaddleOCR | https://github.com/PaddlePaddle/PaddleOCR | Local OCR fallback |
| Tesseract | https://github.com/tesseract-ocr/tesseract | Legacy OCR fallback |

### 4.3 Image Inpainting Models

| Model | URL | Use Case |
|-------|-----|----------|
| LaMa | https://github.com/advimman/lama | High-quality inpainting |
| AOT | https://github.com/researchmm/AOT-Net | Fast inpainting |
| Stable Diffusion Inpainting | https://huggingface.co/runwayml/stable-diffusion-inpainting | AI-based inpainting |
| manga-image-translator built-in | https://github.com/zyddnys/manga-image-translator | Integrated solution |

### 4.4 Text-to-Speech Models

| Model | Provider | URL | Use Case |
|-------|----------|-----|----------|
| MiMo TTS | Xiaomi | https://mimo.xiaomi.com | Primary TTS engine |
| Edge-TTS | Microsoft | https://github.com/rany2/edge-tts | Free TTS fallback |
| Coqui TTS | Coqui | https://github.com/coqui-ai/TTS | Local TTS fallback |
| VITS | Various | https://github.com/jaywalnut310/vits | Research/local TTS |

### 4.5 Voice Cloning Models

| Model | Provider | URL | Use Case |
|-------|----------|-----|----------|
| MiMo VoiceClone | Xiaomi | https://mimo.xiaomi.com | Primary voice cloning |
| Coqui XTTS | Coqui | https://github.com/coqui-ai/TTS | Local voice cloning fallback |
| Bark | Suno | https://github.com/suno-ai/bark | Audio generation |
| RVC | Various | https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI | Voice conversion |

---

## 5. Game Engine Documentation

### 5.1 RPG Maker

| Resource | URL | Description |
|----------|-----|-------------|
| RPG Maker MV Documentation | https://www.rpgmakerweb.com/products/rpg-maker-mv | Official docs |
| RPG Maker MZ Documentation | https://www.rpgmakerweb.com/products/rpg-maker-mz | Official docs |
| RPG Maker File Formats | https://rpgmaker.net/technical/file_formats/ | Community documentation |
| RPG Maker MV Data Structure | https://github.com/search?q=rpg+maker+mv+data+structure | GitHub resources |

**Key File Formats:**
```
RPG Maker MV/MZ:  www/data/*.json (JSON format)
RPG Maker VX/Ace: Data/*.rvdata2 (Ruby Marshal format)
RPG Maker XP:     Data/*.rxdata (Ruby Marshal format)
RPG Maker 2003:   *.ldb, *.lmt (binary format)
```

### 5.2 Ren'Py

| Resource | URL | Description |
|----------|-----|-------------|
| Ren'Py Documentation | https://www.renpy.org/doc/html/ | Official documentation |
| Ren'Py Script Language | https://www.renpy.org/doc/html/language_basics.html | Script reference |
| Ren'Py Translation Guide | https://www.renpy.org/doc/html/translation.html | Official translation guide |

**Key File Format:**
```renpy
# .rpy script files
label start:
    "Hello, world!"  # Translatable string
    e "This is dialogue."  # Character dialogue
```

### 5.3 Unity

| Resource | URL | Description |
|----------|-----|-------------|
| Unity Documentation | https://docs.unity3d.com/ | Official documentation |
| Unity Localization Package | https://docs.unity3d.com/Packages/com.unity.localization@latest | Localization system |
| Unity Assets Bundle Extractor | https://github.com/SeriousCache/UABE | Asset extraction tool |

### 5.4 Unreal Engine

| Resource | URL | Description |
|----------|-----|-------------|
| Unreal Engine Documentation | https://docs.unrealengine.com/ | Official documentation |
| Unreal Localization | https://docs.unrealengine.com/en-US/ProductionPipelines/Localization/ | Localization system |
| Unreal .locres Format | https://github.com/search?q=locres+parser | Community parsers |

### 5.5 Visual Novel Engines

| Engine | URL | Documentation |
|--------|-----|---------------|
| NScripter | http://nscripter.com/ | Japanese VN engine |
| KiriKiri | https://github.com/nicenemo/KiriKiri | Open-source VN engine |
| TyranoBuilder | https://store.steampowered.com/app/345370/TyranoBuilder/ | Visual novel creator |
| Visual Novel Maker | https://www.rpgmakerweb.com/products/visual-novel-maker | VN creation tool |

### 5.6 Other Engines

| Engine | URL | Documentation |
|--------|-----|---------------|
| Wolf RPG Editor | https://www.wolf-rpg-editor.com/ | Japanese RPG creation tool |
| GameMaker Studio | https://gamemaker.io/ | Game development platform |
| Godot Engine | https://godotengine.org/ | Open-source game engine |

---

## 6. Image Processing Tools

### 6.1 Pillow (PIL Fork)

| Resource | URL | Description |
|----------|-----|-------------|
| Pillow Documentation | https://pillow.readthedocs.io/ | Official documentation |
| Pillow GitHub | https://github.com/python-pillow/Pillow | Source code |
| Pillow PyPI | https://pypi.org/project/Pillow/ | Package page |

**Installation:**
```bash
pip install Pillow>=10.0
```

**Key Features Used:**
- Image loading/saving (PNG, JPEG, WEBP, BMP, TIFF)
- Image resizing and cropping
- Text rendering with TrueType fonts
- Image compositing and blending
- Color space conversion

### 6.2 OpenCV

| Resource | URL | Description |
|----------|-----|-------------|
| OpenCV Documentation | https://docs.opencv.org/ | Official documentation |
| OpenCV Python Tutorials | https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html | Python tutorials |

**Installation:**
```bash
pip install opencv-python-headless>=4.8
```

**Key Features Used:**
- Advanced image processing
- Contour detection (bubble boundaries)
- Morphological operations
- Image thresholding

### 6.3 Font Resources

| Resource | URL | Description |
|----------|-----|-------------|
| Google Fonts | https://fonts.google.com/ | Free fonts including Vietnamese |
| Vietnamese Font Collection | https://github.com/search?q=vietnamese+fonts | Community fonts |
| Be Vietnam Pro | https://fonts.google.com/specimen/Be+Vietnam+Pro | Recommended Vietnamese font |
| Noto Sans Vietnamese | https://fonts.google.com/noto/specimen/Noto+Sans | Google Noto with Vietnamese support |

**Recommended Fonts for Vietnamese:**
| Font | Style | License | Download |
|------|-------|---------|----------|
| Be Vietnam Pro | Modern sans-serif | OFL | Google Fonts |
| Noto Sans | Universal sans-serif | OFL | Google Fonts |
| Roboto | Clean sans-serif | Apache 2.0 | Google Fonts |
| Source Sans Pro | Professional sans-serif | OFL | Adobe Fonts |

---

## 7. Audio and Video Processing Tools

### 7.1 FFmpeg

| Resource | URL | Description |
|----------|-----|-------------|
| FFmpeg Documentation | https://ffmpeg.org/documentation.html | Official documentation |
| FFmpeg Wiki | https://trac.ffmpeg.org/wiki | Usage guides |
| FFmpeg Downloads | https://ffmpeg.org/download.html | Binary downloads |
| ffmpeg-python | https://github.com/kkroening/ffmpeg-python | Python wrapper |

**Installation:**
```bash
# Windows (via Chocolatey)
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html

# Python wrapper
pip install ffmpeg-python
```

**Key Features Used:**
| Feature | FFmpeg Command | Purpose |
|---------|---------------|---------|
| Audio extraction | `ffmpeg -i input.mp4 -vn -acodec pcm_s16le output.wav` | Extract audio from video |
| Audio mixing | `ffmpeg -i voice.wav -i bg.wav -filter_complex amix output.wav` | Mix voice + background |
| Video muxing | `ffmpeg -i video.mp4 -i audio.wav -c:v copy output.mp4` | Add audio track to video |
| Format conversion | `ffmpeg -i input.mkv -c:v libx264 output.mp4` | Convert video formats |
| Subtitle embedding | `ffmpeg -i video.mp4 -i subs.srt -c copy output.mp4` | Embed subtitles |

### 7.2 VLC Media Player

| Resource | URL | Description |
|----------|-----|-------------|
| VLC Documentation | https://wiki.videolan.org/Documentation:Documentation/ | Official documentation |
| VLC Python Bindings | https://github.com/oaubert/python-vlc | Python integration |
| VLC HTTP API | https://wiki.videolan.org/Documentation:WebPlugin/ | HTTP control interface |

**Installation:**
```bash
pip install python-vlc
```

**Key Features Used:**
- Media preview (video + audio playback)
- Frame-by-frame navigation
- Audio track selection
- Subtitle overlay

### 7.3 Audio Processing Libraries

| Library | URL | Description |
|---------|-----|-------------|
| pydub | https://github.com/jiaaro/pydub | High-level audio manipulation |
| librosa | https://github.com/librosa/librosa | Audio analysis |
| soundfile | https://github.com/bastibe/SoundFile | Audio file I/O |
| webrtcvad | https://github.com/wiseman/py-webrtcvad | Voice activity detection |

**Installation:**
```bash
pip install pydub librosa soundfile webrtcvad
```

---

## 8. Web and API Frameworks

### 8.1 FastAPI Ecosystem

| Library | URL | Purpose |
|---------|-----|---------|
| FastAPI | https://fastapi.tiangolo.com/ | Web framework |
| Uvicorn | https://www.uvicorn.org/ | ASGI server |
| Pydantic | https://docs.pydantic.dev/ | Data validation |
| HTTPX | https://www.python-httpx.org/ | Async HTTP client |
| Python-Multipart | https://github.com/andrew-d/python-multipart | File upload support |
| WebSocket | https://fastapi.tiangolo.com/advanced/websockets/ | Real-time updates |

**Installation:**
```bash
pip install fastapi uvicorn[standard] httpx python-multipart websockets
```

### 8.2 CLI Framework

| Library | URL | Purpose |
|---------|-----|---------|
| Click | https://click.palletsprojects.com/ | CLI framework |
| Rich | https://github.com/Textualize/rich | Terminal formatting |
| tqdm | https://github.com/tqdm/tqdm | Progress bars |

**Installation:**
```bash
pip install click rich tqdm
```

### 8.3 Web Dashboard (Frontend)

| Technology | URL | Purpose |
|------------|-----|---------|
| Jinja2 | https://jinja.palletsprojects.com/ | Template engine |
| HTMX | https://htmx.org/ | Dynamic HTML updates |
| Tailwind CSS | https://tailwindcss.com/ | CSS framework |
| Alpine.js | https://alpinejs.dev/ | Lightweight JS framework |

---

## 9. Database and Storage

### 9.1 SQLite

| Resource | URL | Description |
|----------|-----|-------------|
| SQLite Documentation | https://www.sqlite.org/docs.html | Official documentation |
| SQLite Browser | https://sqlitebrowser.org/ | GUI for database inspection |

### 9.2 SQLAlchemy + Alembic

| Resource | URL | Description |
|----------|-----|-------------|
| SQLAlchemy Documentation | https://docs.sqlalchemy.org/ | ORM documentation |
| Alembic Documentation | https://alembic.sqlalchemy.org/ | Migration tool |

### 9.3 Caching

| Library | URL | Purpose |
|---------|-----|---------|
| cachetools | https://github.com/tkem/cachetools | In-memory caching |
| diskcache | https://github.com/grantjenks/python-diskcache | Disk-based caching |

---

## 10. Development Tools

### 10.1 Code Quality

| Tool | URL | Purpose |
|------|-----|---------|
| Ruff | https://github.com/astral-sh/ruff | Linting + formatting |
| mypy | https://mypy-lang.org/ | Static type checking |
| Black | https://github.com/psf/black | Code formatting |
| isort | https://github.com/PyCQA/isort | Import sorting |

**Installation:**
```bash
pip install ruff mypy
```

**Configuration (pyproject.toml):**
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true
```

### 10.2 Testing

| Tool | URL | Purpose |
|------|-----|---------|
| pytest | https://docs.pytest.org/ | Test framework |
| pytest-asyncio | https://github.com/pytest-dev/pytest-asyncio | Async test support |
| pytest-cov | https://github.com/pytest-dev/pytest-cov | Coverage reporting |
| pytest-benchmark | https://github.com/ionelmc/pytest-benchmark | Performance testing |
| factory-boy | https://factoryboy.readthedocs.io/ | Test data factories |

**Installation:**
```bash
pip install pytest pytest-asyncio pytest-cov pytest-benchmark factory-boy
```

### 10.3 Version Control

| Tool | URL | Purpose |
|------|-----|---------|
| Git | https://git-scm.com/ | Version control |
| GitHub | https://github.com/ | Repository hosting |
| GitHub Actions | https://github.com/features/actions | CI/CD |
| pre-commit | https://pre-commit.com/ | Git hooks |

### 10.4 Containerization

| Tool | URL | Purpose |
|------|-----|---------|
| Docker | https://www.docker.com/ | Containerization |
| Docker Compose | https://docs.docker.com/compose/ | Multi-container orchestration |

---

## 11. Standards and Specifications

### 11.1 IEEE Standards

| Standard | Title | Relevance |
|----------|-------|-----------|
| IEEE 830-1998 | Software Requirements Specification | SRS document structure |
| IEEE 1471-2000 | Software Architecture Description | Architecture document structure |
| IEEE 1058-2015 | Software Development Plan | Development plan structure |
| IEEE 730-2014 | Software Quality Assurance | QA processes |

### 11.2 Web Standards

| Standard | URL | Relevance |
|----------|-----|-----------|
| OpenAPI 3.0 | https://spec.openapis.org/oas/v3.0.3 | REST API specification |
| JSON Schema | https://json-schema.org/ | Data validation |
| WebSocket Protocol | https://tools.ietf.org/html/rfc6455 | Real-time communication |
| HTTP/1.1 | https://tools.ietf.org/html/rfc2616 | HTTP protocol |

### 11.3 Media Standards

| Standard | Description | Relevance |
|----------|-------------|-----------|
| SRT (SubRip) | Subtitle format | Subtitle generation |
| WebVTT | Web subtitle format | Web-based subtitles |
| H.264/AVC | Video codec | Video encoding |
| AAC | Audio codec | Audio encoding |
| WAV | Audio format | Audio processing |
| PNG | Image format | Image output |
| JPEG | Image format | Image output |

---

## 12. Academic and Research References

### 12.1 Multi-Agent Systems

| Reference | Authors | Year | Relevance |
|-----------|---------|------|-----------|
| "Multi-Agent Systems: A Modern Approach to Distributed AI" | Gerhard Weiss | 1999 | Foundational concepts |
| "Foundations of Distributed Artificial Intelligence" | G. M. P. O'Hare, N. R. Jennings | 1996 | Agent architectures |
| "An Introduction to MultiAgent Systems" | Michael Wooldridge | 2009 | Modern agent design |

### 12.2 Machine Translation

| Reference | Authors | Year | Relevance |
|-----------|---------|------|-----------|
| "Neural Machine Translation by Jointly Learning to Align and Translate" | Bahdanau et al. | 2014 | Attention mechanism |
| "Attention Is All You Need" | Vaswani et al. | 2017 | Transformer architecture |
| "Language Models are Few-Shot Learners" | Brown et al. | 2020 | GPT-3 / LLM capabilities |

### 12.3 Optical Character Recognition

| Reference | Authors | Year | Relevance |
|-----------|---------|------|-----------|
| "Scene Text Detection and Recognition: The Deep Learning Era" | Long et al. | 2018 | Modern OCR approaches |
| "CRAFT: Character Region Awareness for Text Detection" | Baek et al. | 2019 | Text detection |

### 12.4 Image Inpainting

| Reference | Authors | Year | Relevance |
|-----------|---------|------|-----------|
| "LaMa: Resolution-robust Large Mask Inpainting with Fourier Convolutions" | Suvorov et al. | 2021 | State-of-the-art inpainting |
| "AOT: Aggregated Attention for Image Inpainting" | Yan et al. | 2021 | Fast inpainting |

### 12.5 Speech Synthesis and Voice Cloning

| Reference | Authors | Year | Relevance |
|-----------|---------|------|-----------|
| "VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech" | Kim et al. | 2021 | Modern TTS |
| "YourTTS: Towards Zero-Shot Multi-Speaker TTS and Zero-Shot Voice Conversion" | Casanova et al. | 2022 | Voice cloning |
| "XTTS: A Massively Multilingual Zero-Shot Text-to-Speech Model" | Coqui AI | 2023 | Multilingual TTS |

---

## 13. Community Resources

### 13.1 Vietnamese Developer Community

| Resource | URL | Description |
|----------|-----|-------------|
| Vietnamese Python Community | https://www.facebook.com/groups/python.vn | Facebook group |
| Vietnamese Game Modding | https://www.facebook.com/groups/gamemodding.vn | Game translation community |
| Vietnamese Manga Translation | https://www.facebook.com/groups/manga.translate | Manga scanlation community |
| Voz Forums | https://vozforums.com | Vietnamese tech forum |

### 13.2 Translation Communities

| Resource | URL | Description |
|----------|-----|-------------|
| VNTranslator | https://vntranslator.net | Vietnamese translation tools |
| Game Localization community | https://www.localizationlab.org | Game localization resources |
| MangaDex | https://mangadex.org | Manga reading/sharing platform |

### 13.3 AI/ML Communities

| Resource | URL | Description |
|----------|-----|-------------|
| Hugging Face | https://huggingface.co | AI model hub |
| Papers With Code | https://paperswithcode.com | ML research papers |
| Reddit r/MachineLearning | https://reddit.com/r/MachineLearning | ML discussion |
| Reddit r/LocalLLaMA | https://reddit.com/r/LocalLLaMA | Local AI models |

### 13.4 Documentation and Learning

| Resource | URL | Description |
|----------|-----|-------------|
| Real Python | https://realpython.com | Python tutorials |
| FastAPI Best Practices | https://github.com/zhanymkanov/fastapi-best-practices | FastAPI patterns |
| Python AsyncIO Guide | https://docs.python.org/3.12/library/asyncio.html | Async programming |
| SQLite Tutorial | https://www.sqlitetutorial.net/ | SQLite basics |

---

## Appendix: Quick Reference — Package Installation

### Complete pip install command

```bash
pip install \
  fastapi \
  "uvicorn[standard]" \
  httpx \
  python-multipart \
  websockets \
  sqlalchemy>=2.0 \
  alembic \
  Pillow>=10.0 \
  opencv-python-headless>=4.8 \
  ffmpeg-python \
  python-vlc \
  click \
  rich \
  tqdm \
  pydub \
  librosa \
  soundfile \
  ruff \
  mypy \
  pytest \
  pytest-asyncio \
  pytest-cov \
  pytest-benchmark \
  structlog \
  mimo-sdk
```

### System Requirements

```
OS:         Windows 10/11 or Ubuntu 22.04+
Python:     3.12+
RAM:        16GB minimum (32GB recommended)
GPU:        NVIDIA with 8GB+ VRAM (optional, for local inference)
Storage:    50GB+ free space (for models, cache, temp files)
FFmpeg:     6.0+ (system install)
VLC:        3.0+ (system install, optional)
```

---

*End of Resources and References*
*Document prepared for Universal Translation Hub (UTH) — DTHU University*
