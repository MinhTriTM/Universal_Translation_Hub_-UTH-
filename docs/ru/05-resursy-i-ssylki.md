# Ресурсы и ссылки
## Universal Translation Hub (UTH)

| Поле | Значение |
|------|----------|
| **Версия** | 1.0 |
| **Автор** | Doan Minh Tri — DTHU University |
| **Дата** | 2026-05-22 |
| **Статус** | Черновик |

---

## Содержание

1. [MiMo V2.5 — AI-платформа](#1-mimo-v25--ai-платформа)
2. [Исходные проекты](#2-исходные-проекты)
3. [Технологии и фреймворки](#3-технологии-и-фреймворки)
4. [AI-модели и инструменты](#4-ai-модели-и-инструменты)
5. [Документация игровых движков](#5-документация-игровых-движков)
6. [Стандарты и спецификации](#6-стандарты-и-спецификации)
7. [Инструменты разработки](#7-инструменты-разработки)
8. [Учебные ресурсы](#8-учебные-ресурсы)

---

## 1. MiMo V2.5 — AI-платформа

### 1.1 Официальные ресурсы Xiaomi MiMo

| Ресурс | URL | Описание |
|--------|-----|----------|
| MiMo GitHub | https://github.com/XiaomiMiMo/MiMo | Официальный репозиторий |
| MiMo Documentation | https://mimo.xiaomi.com/docs | Документация платформы |
| MiMo V2.5 Release | https://github.com/XiaomiMiMo/MiMo/releases/tag/v2.5 | Релиз V2.5 |
| MiMo HuggingFace | https://huggingface.co/XiaomiMiMo | Модели на HuggingFace |
| MiMo Community | https://community.mimo.xiaomi.com | Сообщество разработчиков |

### 1.2 Модели MiMo V2.5

| Модель | HuggingFace ID | Размер | Назначение |
|--------|---------------|--------|-----------|
| MiMo V2.5-Pro | `XiaomiMiMo/mimo-v2.5-pro` | ~14 ГБ | Основной LLM, перевод, рассуждение |
| MiMo V2.5 | `XiaomiMiMo/mimo-v2.5` | ~7 ГБ | Лёгкий LLM, OCR, маршрутизация |
| MiMo TTS | `XiaomiMiMo/mimo-tts` | ~3 ГБ | Синтез речи (Text-to-Speech) |
| MiMo VoiceClone | `XiaomiMiMo/mimo-voice-clone` | ~2 ГБ | Клонирование голоса |
| MiMo VoiceDesign | `XiaomiMiMo/mimo-voice-design` | ~1 ГБ | Дизайн и настройка голоса |

### 1.3 Установка MiMo

```bash
# Клонирование репозитория
git clone https://github.com/XiaomiMiMo/MiMo.git
cd MiMo

# Установка зависимостей
pip install -r requirements.txt

# Загрузка моделей (через HuggingFace CLI)
pip install huggingface_hub
huggingface-cli download XiaomiMiMo/mimo-v2.5-pro --local-dir models/mimo-v2.5-pro
huggingface-cli download XiaomiMiMo/mimo-v2.5 --local-dir models/mimo-v2.5
huggingface-cli download XiaomiMiMo/mimo-tts --local-dir models/mimo-tts
huggingface-cli download XiaomiMiMo/mimo-voice-clone --local-dir models/mimo-voice-clone
huggingface-cli download XiaomiMiMo/mimo-voice-design --local-dir models/mimo-voice-design
```

### 1.4 Пример использования MiMo

```python
# Пример: Загрузка и использование MiMo V2.5-Pro
from mimo import MiMoModel

# Загрузка модели
model = MiMoModel.from_pretrained(
    "XiaomiMiMo/mimo-v2.5-pro",
    device="cuda",
    dtype="float16"
)

# Перевод текста
result = model.translate(
    text="Hello, how are you?",
    source_lang="en",
    target_lang="vi",
    context="Дружеский разговор"
)
print(result.translated_text)  # "Xin chào, bạn khỏe không?"
```

---

## 2. Исходные проекты

### 2.1 MIMO-AXON (Фильмы)

| Ресурс | URL | Описание |
|--------|-----|----------|
| GitHub Repository | https://github.com/user/MIMO-AXON | Основной репозиторий |
| Documentation | /docs/README.md | Документация проекта |
| Issues | https://github.com/user/MIMO-AXON/issues | Баг-трекер |

**Компоненты для интеграции:**
- STT-модуль (распознавание речи)
- TTS-модуль (синтез речи)
- VoiceClone-модуль (клонирование голоса)
- FFmpeg-интеграция (обработка видео)
- Система таймкодов

**Структура:**
```
MIMO-AXON/
├── stt/                    # Speech-to-Text
│   ├── whisper_engine.py   # Движок Whisper
│   └── diarization.py      # Разделение говорящих
├── tts/                    # Text-to-Speech
│   ├── synthesis.py        # Синтез речи
│   └── prosody.py          # Просодия
├── voice_clone/            # Клонирование голоса
│   ├── encoder.py          # Энкодер голоса
│   └── synthesizer.py      # Синтезатор
├── video/                  # Обработка видео
│   ├── extractor.py        # Извлечение аудио
│   ├── muxer.py            # Миксинг аудио/видео
│   └── subtitle.py         # Субтитры
└── utils/                  # Утилиты
    ├── audio.py            # Аудиообработка
    └── timecode.py         # Таймкоды
```

### 2.2 DichGame (Игры)

| Ресурс | URL | Описание |
|--------|-----|----------|
| GitHub Repository | https://github.com/user/DichGame | Основной репозиторий |
| Documentation | /docs/README.md | Документация |
| Engine Plugins | /engines/ | Плагины движков |

**Компоненты для интеграции:**
- 12 парсеров игровых движков
- Система плагинов
- Форматы файлов игр
- Глоссарий терминов

**Поддерживаемые движки:**

| Движок | Форматы | Файл парсера |
|--------|---------|-------------|
| Ren'Py | .rpy, .rpyc | `renpy_parser.py` |
| RPG Maker | .json, .rvdata2 | `rpgmaker_parser.py` |
| Unity | .txt, .json, .xml | `unity_parser.py` |
| Unreal Engine | .locres, .po | `unreal_parser.py` |
| NScripter | .txt (nsa/ns2) | `nscripter_parser.py` |
| KiriKiri | .ks, .tjs | `kirikiri_parser.py` |
| YU-RIS | .ybn, .mes | `yuris_parser.py` |
| CatSystem2 | .cst, .cs2 | `catsystem2_parser.py` |
| TyranoBuilder | .tyrano | `tyrano_parser.py` |
| Construct | .json | `construct_parser.py` |
| Godot | .tres, .translation | `godot_parser.py` |
| Custom/Text | .txt, .csv, .xml, .json | `custom_parser.py` |

### 2.3 manga-image-translator (Манга)

| Ресурс | URL | Описание |
|--------|-----|----------|
| GitHub Repository | https://github.com/zyddnys/manga-image-translator | Основной репозиторий |
| Documentation | https://github.com/zyddnys/manga-image-translator/wiki | Wiki |
| Models | https://github.com/zyddnys/manga-image-translator/releases | Предобученные модели |

**Компоненты для интеграции:**
- OCR-движок (распознавание текста манги)
- Inpainting-движок (удаление текста)
- Render-движок (наложение текста)
- Детектор текстовых блоков
- Система стилей шрифтов

**Структура:**
```
manga-image-translator/
├── ocr/                    # OCR
│   ├── manga_ocr.py        # Основной OCR
│   ├── detector.py         # Детектор текста
│   └── recognizer.py       # Распознаватель
├── inpainting/             # Инпейнтинг
│   ├── base.py             # Базовый класс
│   ├── anime_inpaint.py    # Аниме-инпейнтинг
│   └── lama_inpaint.py     # LaMa-инпейнтинг
├── render/                 # Рендер
│   ├── text_render.py      # Рендер текста
│   ├── font_manager.py     # Менеджер шрифтов
│   └── layout.py           # Компоновка
├── translate/              # Перевод
│   ├── base.py             # Базовый переводчик
│   └── google_trans.py     # Google Translate
└── utils/                  # Утилиты
    ├── image.py            # Обработка изображений
    └── text.py             # Обработка текста
```

---

## 3. Технологии и фреймворки

### 3.1 Язык программирования

| Технология | Версия | URL | Лицензия |
|-----------|--------|-----|----------|
| Python | 3.12 | https://www.python.org/downloads/release/python-3120/ | PSF License |
| pip | 24.0+ | https://pip.pypa.io/ | MIT |

### 3.2 Веб-фреймворк

| Технология | Версия | URL | Лицензия |
|-----------|--------|-----|----------|
| FastAPI | 0.110+ | https://fastapi.tiangolo.com/ | MIT |
| Uvicorn | 0.27+ | https://www.uvicorn.org/ | BSD-3 |
| Pydantic | 2.6+ | https://docs.pydantic.dev/ | MIT |
| Starlette | 0.36+ | https://www.starlette.io/ | BSD-3 |

### 3.3 База данных

| Технология | Версия | URL | Лицензия |
|-----------|--------|-----|----------|
| SQLite | 3.45+ | https://www.sqlite.org/ | Public Domain |
| SQLAlchemy | 2.0+ | https://www.sqlalchemy.org/ | MIT |
| Alembic | 1.13+ | https://alembic.sqlalchemy.org/ | MIT |

### 3.4 Обработка медиа

| Технология | Версия | URL | Лицензия |
|-----------|--------|-----|----------|
| FFmpeg | 6.1+ | https://ffmpeg.org/ | LGPL/GPL |
| FFmpeg-python | 0.2+ | https://github.com/kkroening/ffmpeg-python | Apache 2.0 |
| VLC | 3.0+ | https://www.videolan.org/vlc/ | GPL |
| python-vlc | 3.0+ | https://github.com/oaubert/python-vlc | GPL |
| Pillow | 10.2+ | https://pillow.readthedocs.io/ | MIT-CMU |
| OpenCV | 4.9+ | https://opencv.org/ | Apache 2.0 |

### 3.5 AI/ML фреймворки

| Технология | Версия | URL | Лицензия |
|-----------|--------|-----|----------|
| PyTorch | 2.2+ | https://pytorch.org/ | BSD-3 |
| Transformers | 4.38+ | https://huggingface.co/docs/transformers/ | Apache 2.0 |
| HuggingFace Hub | 0.20+ | https://huggingface.co/docs/huggingface_hub/ | Apache 2.0 |
| ONNX Runtime | 1.17+ | https://onnxruntime.ai/ | MIT |
| Whisper | 20231117+ | https://github.com/openai/whisper | MIT |

### 3.6 Асинхронность и очереди

| Технология | Версия | URL | Лицензия |
|-----------|--------|-----|----------|
| asyncio | (stdlib) | https://docs.python.org/3/library/asyncio.html | PSF |
| aiofiles | 23.2+ | https://github.com/Tinche/aiofiles | Apache 2.0 |
| Celery (опционально) | 5.3+ | https://docs.celeryq.dev/ | BSD-3 |

### 3.7 Тестирование

| Технология | Версия | URL | Лицензия |
|-----------|--------|-----|----------|
| pytest | 8.0+ | https://docs.pytest.org/ | MIT |
| pytest-asyncio | 0.23+ | https://github.com/pytest-dev/pytest-asyncio | Apache 2.0 |
| pytest-cov | 4.1+ | https://pytest-cov.readthedocs.io/ | MIT |
| httpx | 0.27+ | https://www.python-httpx.org/ | BSD-3 |
| locust | 2.23+ | https://locust.io/ | MIT |

---

## 4. AI-модели и инструменты

### 4.1 Модели для перевода

| Модель | URL | Размер | Языки | Назначение |
|--------|-----|--------|-------|-----------|
| MiMo V2.5-Pro | HuggingFace | ~14 ГБ | Мультиязычный | Основной перевод |
| MiMo V2.5 | HuggingFace | ~7 ГБ | Мультиязычный | Лёгкий перевод |
| OPUS-MT | https://github.com/Helsinki-NLP/Opus-MT | ~300 МБ/пара | Пары языков | Fallback-перевод |
| NLLB-200 | https://github.com/facebookresearch/fairseq/tree/nllb | ~3-12 ГБ | 200 языков | Альтернатива |

### 4.2 Модели для OCR

| Модель | URL | Назначение |
|--------|-----|-----------|
| MiMo V2.5 (OCR) | HuggingFace | OCR для манги |
| Manga OCR | https://github.com/kha-white/manga-ocr | Специализированный OCR |
| Tesseract | https://github.com/tesseract-ocr/tesseract | Общий OCR (fallback) |
| PaddleOCR | https://github.com/PaddlePaddle/PaddleOCR | Многоязычный OCR |

### 4.3 Модели для STT

| Модель | URL | Размер | Языки |
|--------|-----|--------|-------|
| Whisper Large-v3 | https://github.com/openai/whisper | ~3 ГБ | 99 языков |
| Whisper Medium | https://github.com/openai/whisper | ~1.5 ГБ | 99 языков |
| MiMo V2.5 (STT) | HuggingFace | ~7 ГБ | Мультиязычный |

### 4.4 Модели для TTS

| Модель | URL | Языки | Назначение |
|--------|-----|-------|-----------|
| MiMo TTS | HuggingFace | Мультиязычный | Основной TTS |
| VITS | https://github.com/jaywalnut310/vits | Мультиязычный | Альтернатива |
| Coqui TTS | https://github.com/coqui-ai/TTS | Мультиязычный | Open-source TTS |
| Bark | https://github.com/suno-ai/bark | EN, JA, ZH, KO | Экспрессивный TTS |

### 4.5 Модели для инпейнтинга

| Модель | URL | Назначение |
|--------|-----|-----------|
| LaMa | https://github.com/advimman/lama | Инпейнтинг общего назначения |
| MiGaintext | https://github.com/baharest-asr/manga-inpainting | Инпейнтинг манги |
| MAT | https://github.com/fenglinglwb/MAT | Маскированный инпейнтинг |

### 4.6 Модели для клонирования голоса

| Модель | URL | Назначение |
|--------|-----|-----------|
| MiMo VoiceClone | HuggingFace | Клонирование голоса |
| MiMo VoiceDesign | HuggingFace | Дизайн голоса |
| Coqui XTTS | https://github.com/coqui-ai/TTS | Клонирование (open-source) |
| So-VITS-SVC | https://github.com/svc-develop-team/so-vits-svc | Клонирование пения |

---

## 5. Документация игровых движков

### 5.1 Ren'Py

| Ресурс | URL |
|--------|-----|
| Официальный сайт | https://www.renpy.org/ |
| Документация | https://www.renpy.org/doc/html/ |
| Формат .rpy | https://www.renpy.org/doc/html/language_basics.html |
| Формат .rpyc | https://github.com/CensoredUsername/unrpyc |
| Перевод Ren'Py | https://www.renpy.org/doc/html/translation.html |
| GitHub | https://github.com/renpy/renpy |

### 5.2 RPG Maker

| Ресурс | URL |
|--------|-----|
| Официальный сайт | https://www.rpgmakerweb.com/ |
| Формат .rvdata2 | RPG Maker VX Ace |
| Формат .json | RPG Maker MV/MZ |
| Инструменты | https://github.com/search?q=rpg+maker+translator |
| RPG Maker MV Docs | https://docs.google.com/document/d/1v0P2Hq0RVGOaDjGjHZ0nHfYb3-0FWxqY/edit |

### 5.3 Unity

| Ресурс | URL |
|--------|-----|
| Unity Localization | https://docs.unity3d.com/Packages/com.unity.localization@1.0/manual/ |
| AssetStudio (извлечение) | https://github.com/Perfare/AssetStudio |
| Формат .txt/.json | Unity TextMeshPro |
| Формат .xml | Unity XML Localization |

### 5.4 Unreal Engine

| Ресурс | URL |
|--------|-----|
| Localization Dashboard | https://docs.unrealengine.com/5.0/en-US/localization-dashboard-in-unreal-engine/ |
| Формат .locres | Unreal Localization Resource |
| Формат .po | Portable Object (gettext) |
| UE Localization Tool | https://docs.unrealengine.com/5.0/en-US/localizing-your-project-in-unreal-engine/ |

### 5.5 NScripter

| Ресурс | URL |
|--------|-----|
| Официальный сайт | http://nscripter.com/ |
| Формат .txt | NScripter script format |
| ONScripter | https://github.com/krkrz/onscripter |
| Инструменты | https://github.com/search?q=nscripter+tools |

### 5.6 KiriKiri

| Ресурс | URL |
|--------|-----|
| Официальный сайт | http://kikyou.info/kr2/ |
| Формат .ks | KiriKiri Script |
| Формат .tjs | TJS2 Script |
| Куратор | https://github.com/Dir-A/Kirikiroid2 |
| Инструменты | https://github.com/search?q=kirikiri+tools |

### 5.7 YU-RIS

| Ресурс | URL |
|--------|-----|
| Официальный сайт | http://visualnovel.jpn.org/ |
| Формат .ybn | YU-RIS Binary |
| Формат .mes | YU-RIS Message |
| Инструменты | https://github.com/search?q=yu-ris+tools |

### 5.8 CatSystem2

| Ресурс | URL |
|--------|-----|
| Официальный сайт | http://hengine.petitgames.jp/ |
| Формат .cst | CatSystem2 Text |
| Формат .cs2 | CatSystem2 Script |
| Инструменты | https://github.com/search?q=catsystem2+tools |

### 5.9 TyranoBuilder

| Ресурс | URL |
|--------|-----|
| Официальный сайт | https://tyranobuilder.com/ |
| Формат .tyrano | Tyrano Script |
| TyranoScript | https://tyrano.jp/ |
| Инструменты | https://github.com/search?q=tyranobuilder+tools |

### 5.10 Construct

| Ресурс | URL |
|--------|-----|
| Официальный сайт | https://www.construct.net/ |
| Формат .json | Construct 3 project |
| Construct 3 Docs | https://www.construct.net/en/make-games/manuals/construct-3 |
| Инструменты | https://github.com/search?q=construct+translator |

### 5.11 Godot

| Ресурс | URL |
|--------|-----|
| Официальный сайт | https://godotengine.org/ |
| Документация | https://docs.godotengine.org/ |
| Формат .tres | Godot Text Resource |
| Формат .translation | Godot Translation |
| Локализация | https://docs.godotengine.org/en/stable/tutorials/i18n/localization_using_gettext.html |
| GitHub | https://github.com/godotengine/godot |

---

## 6. Стандарты и спецификации

### 6.1 IEEE стандарты

| Стандарт | Название | URL | Применение |
|----------|----------|-----|-----------|
| IEEE 830-1998 | SRS | https://standards.ieee.org/ieee/830/1329/ | Спецификация требований |
| IEEE 1471-2000 | SAD | https://standards.ieee.org/ieee/1471/1/ | Архитектура |
| IEEE 1058-1998 | SDP | https://standards.ieee.org/ieee/1058/3740/ | План разработки |
| IEEE 730-2014 | SQAP | https://standards.ieee.org/ieee/730/6835/ | Обеспечение качества |

### 6.2 Спецификации форматов

| Формат | Спецификация | URL |
|--------|-------------|-----|
| JSON | RFC 8259 | https://tools.ietf.org/html/rfc8259 |
| XML | W3C XML 1.0 | https://www.w3.org/TR/xml/ |
| UTF-8 | RFC 3629 | https://tools.ietf.org/html/rfc3629 |
| SRT (субтитры) | SRT Format | https://docs.fileformat.com/video/srt/ |
| ASS (субтитры) | ASS Format | http://www.tcax.org/docs/ass-specs.htm |
| PO (gettext) | GNU gettext | https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html |

### 6.3 Стандарты качества перевода

| Стандарт | Описание | URL |
|----------|----------|-----|
| BLEU | Bilingual Evaluation Understudy | https://aclanthology.org/P02-1040/ |
| METEOR | Metric for Evaluation of Translation with Explicit ORdering | https://aclanthology.org/W05-0909/ |
| TER | Translation Edit Rate | https://aclanthology.org/2006.amta-papers.25/ |
| COMET | Crosslingual Optimized Metric for Evaluation of Translation | https://github.com/Unbabel/COMET |

---

## 7. Инструменты разработки

### 7.1 IDE и редакторы

| Инструмент | URL | Лицензия |
|-----------|-----|----------|
| VS Code | https://code.visualstudio.com/ | MIT |
| PyCharm | https://www.jetbrains.com/pycharm/ | Proprietary (Community — бесплатная) |
| Cursor | https://cursor.sh/ | Proprietary |

### 7.2 Контроль версий

| Инструмент | URL | Лицензия |
|-----------|-----|----------|
| Git | https://git-scm.com/ | GPL-2.0 |
| GitHub | https://github.com/ | Proprietary |

### 7.3 CI/CD

| Инструмент | URL | Лицензия |
|-----------|-----|----------|
| GitHub Actions | https://github.com/features/actions | Proprietary |
| Pre-commit | https://pre-commit.com/ | MIT |
| Ruff | https://github.com/astral-sh/ruff | MIT |

### 7.4 Контейнеризация (опционально)

| Инструмент | URL | Лицензия |
|-----------|-----|----------|
| Docker | https://www.docker.com/ | Apache 2.0 |
| NVIDIA Container Toolkit | https://github.com/NVIDIA/nvidia-container-toolkit | Apache 2.0 |

### 7.5 Мониторинг и логирование

| Инструмент | URL | Лицензия |
|-----------|-----|----------|
| Loguru | https://github.com/Delgan/loguru | MIT |
| Rich | https://github.com/Textualize/rich | MIT |
| TensorBoard | https://www.tensorflow.org/tensorboard | Apache 2.0 |

### 7.6 Управление зависимостями

| Инструмент | URL | Лицензия |
|-----------|-----|----------|
| pip | https://pip.pypa.io/ | MIT |
| Poetry | https://python-poetry.org/ | MIT |
| uv | https://github.com/astral-sh/uv | Apache 2.0 |

---

## 8. Учебные ресурсы

### 8.1 MiMo и LLM

| Ресурс | URL | Описание |
|--------|-----|----------|
| MiMo Quick Start | https://mimo.xiaomi.com/docs/quickstart | Быстрый старт |
| MiMo API Reference | https://mimo.xiaomi.com/docs/api | API-справочник |
| MiMo Examples | https://github.com/XiaomiMiMo/MiMo/tree/main/examples | Примеры кода |
| HuggingFace Course | https://huggingface.co/course | Курс по HuggingFace |

### 8.2 NLP и перевод

| Ресурс | URL | Описание |
|--------|-----|----------|
| Stanford NLP | https://nlp.stanford.edu/ | Курс NLP |
| HuggingFace NLP Course | https://huggingface.co/learn/nlp-course | NLP курс |
| Machine Translation Guide | https://machinetranslate.org/ | Гид по машинному переводу |

### 8.3 OCR и компьютерное зрение

| Ресурс | URL | Описание |
|--------|-----|----------|
| OpenCV Tutorial | https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html | Туториал OpenCV |
| Manga OCR Paper | https://arxiv.org/abs/2211.05508 | Статья о OCR манги |
| YOLO Documentation | https://docs.ultralytics.com/ | Детекция объектов |

### 8.4 Обработка видео и аудио

| Ресурс | URL | Описание |
|--------|-----|----------|
| FFmpeg Documentation | https://ffmpeg.org/documentation.html | Документация FFmpeg |
| Whisper Documentation | https://github.com/openai/whisper/blob/main/README.md | Документация Whisper |
| Audio Processing Guide | https://pytorch.org/tutorials/beginner/audio_preprocessing_tutorial.html | Аудиообработка |

### 8.5 Разработка игр и VN

| Ресурс | URL | Описание |
|--------|-----|----------|
| Ren'Py Tutorial | https://www.renpy.org/doc/html/quickstart.html | Туториал Ren'Py |
| Godot Documentation | https://docs.godotengine.org/ | Документация Godot |
| Visual Novel Dev | https://visualnoveldev.com/ | Разработка VN |

### 8.6 Python и FastAPI

| Ресурс | URL | Описание |
|--------|-----|----------|
| Python Documentation | https://docs.python.org/3/ | Документация Python |
| FastAPI Tutorial | https://fastapi.tiangolo.com/tutorial/ | Туториал FastAPI |
| AsyncIO Guide | https://docs.python.org/3/library/asyncio.html | AsyncIO |
| Pydantic Documentation | https://docs.pydantic.dev/ | Pydantic v2 |

---

## Приложение A: Быстрые ссылки

### Команды для начала работы

```bash
# Клонировать проект
git clone https://github.com/user/XiaoMimo.git
cd XiaoMimo

# Установить зависимости
pip install -r requirements.txt

# Загрузить модели MiMo
python scripts/download_models.py

# Инициализировать БД
python -m alembic upgrade head

# Запустить сервер
python main.py

# Открыть GUI
# http://localhost:8000
```

### Полезные команды FFmpeg

```bash
# Извлечь аудио из видео
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav

# Объединить видео с новым аудио
ffmpeg -i input.mp4 -i new_audio.wav -c:v copy -c:a aac output.mp4

# Конвертировать формат
ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4

# Добавить субтитры
ffmpeg -i input.mp4 -vf subtitles=subs.srt output.mp4
```

### Полезные команды Python

```bash
# Запустить тесты
pytest tests/ -v --cov=agents

# Форматировать код
ruff format .

# Проверить типы
mypy agents/ --ignore-missing-imports

# Запустить линтер
ruff check .
```

---

*Конец документа ресурсов и ссылок*
