# Tài Nguyên & Tham Khảo — Universal Translation Hub (UTH)

**Phiên bản:** 1.0
**Ngày:** 2026-05-22

---

## 1. Xiaomi MiMo

| Tài liệu | URL |
|----------|-----|
| MiMo 100T Program | https://100t.xiaomimimo.com/ |
| MiMo API Documentation | https://mimo.xiaomi.com/docs |
| MiMo V2.5 Model Card | https://mimo.xiaomi.com/models |
| MiMo TTS Documentation | https://mimo.xiaomi.com/tts |

---

## 2. Dự án hiện có (Source code)

| Dự án | Vị trí | Đóng góp |
|-------|--------|----------|
| MIMO-AXON | `D:\Du_An_Mini\XiaoMi100T` | Film pipeline, TTS, VLC |
| DichGame | `E:\DichGame` | Game pipeline, 12 engines |
| manga-image-translator | `E:\DichGame\Tool\manga-image-translator` | Manga pipeline, OCR |

---

## 3. Công nghệ & Framework

| Công nghệ | URL | Phiên bản |
|-----------|-----|-----------|
| Python | https://www.python.org/ | 3.12+ |
| FastAPI | https://fastapi.tiangolo.com/ | 0.110+ |
| SQLite | https://www.sqlite.org/ | 3.45+ |
| FFmpeg | https://ffmpeg.org/ | 6.0+ |
| VLC | https://www.videolan.org/ | 3.0+ |
| PyTorch | https://pytorch.org/ | 2.3+ |
| OpenCV | https://opencv.org/ | 4.10+ |

---

## 4. AI Models & APIs

| Model/API | URL | Sử dụng |
|-----------|-----|---------|
| MiMo V2.5-Pro | Xiaomi MiMo API | Director reasoning |
| MiMo V2.5 | Xiaomi MiMo API | Translation, OCR |
| MiMo TTS | Xiaomi MiMo API | Text-to-Speech |
| OpenAI Whisper | https://github.com/openai/whisper | STT fallback |
| Edge-TTS | https://github.com/rany2/edge-tts | TTS fallback |
| manga-ocr | https://github.com/kha-white/manga-ocr | OCR fallback |

---

## 5. Tài liệu kỹ thuật tham khảo

| Tiêu đề | Nguồn | Chủ đề |
|---------|-------|--------|
| IEEE 830-1998 | IEEE | Software Requirements Specification |
| IEEE 1471-2000 | IEEE | Software Architecture Documentation |
| IEEE 1058-1998 | IEEE | Software Development Plan |
| Designing Data-Intensive Applications | Martin Kleppmann | System design patterns |
| Building Multi-Agent Systems | Google DeepMind | Agent architecture |

---

## 6. Game Engine Documentation

| Engine | Documentation |
|--------|--------------|
| RPG Maker MV/MZ | https://rpgmakerofficial.com/ |
| Unity | https://docs.unity3d.com/ |
| Ren'Py | https://www.renpy.org/doc/ |
| Kirikiri | https://krkrdoc.web.fc2.com/ |
| CatSystem2 | http://catsys2.com/ |

---

## 7. Image Processing

| Tool | URL | Sử dụng |
|------|-----|---------|
| LaMa inpainting | https://github.com/advimman/lama | Remove text |
| CRAFT text detection | https://github.com/clovaai/CRAFT-pytorch | Detect text |
| Stable Diffusion | https://github.com/CompVis/stable-diffusion | Inpainting |

---

## 8. Audio Processing

| Tool | URL | Sử dụng |
|------|-----|---------|
| FFmpeg | https://ffmpeg.org/ | Audio/video processing |
| Piper TTS | https://github.com/rhasspy/piper | Local TTS |
| MeloTTS | https://github.com/myshell-ai/MeloTTS | Local TTS |
| espeak-ng | https://github.com/espeak-ng/espeak-ng | Phonemization |
