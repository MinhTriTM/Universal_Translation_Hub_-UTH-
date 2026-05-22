# Software Requirements Specification (SRS)
## Requirements Specification — Universal Translation Hub (UTH)

**Version:** 1.0
**Date:** 2026-05-22
**Author:** Doan Minh Tri
**Reference Standard:** IEEE 830-1998

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for the **Universal Translation Hub (UTH)** project — a multi-agent AI system for universal translation of games, manga, and films.

### 1.2 Scope
UTH supports automated translation for 3 types of content:
- **Game**: 12 game engines (RPG Maker, Unity, Ren'Py, Kirikiri, CatSystem2, NScripter, TyranoBuilder, Web/HTML5, NW.js, Wolf RPG, Binary)
- **Manga/Comic**: OCR -> Translation -> Inpainting -> Render
- **Film/Video**: STT -> Translation -> TTS -> Audio Sync

### 1.3 Definitions & Terminology

| Term | Definition |
|------|-----------|
| Agent | An autonomous AI actor with a specific goal |
| Pipeline | A sequential or parallel processing chain |
| TTS | Text-to-Speech (Speech synthesis) |
| STT | Speech-to-Text (Speech recognition) |
| OCR | Optical Character Recognition |
| Inpainting | Removing original text and restoring the image background |
| Translation Memory | A database storing existing translations |
| Glossary | A unified terminology table |

### 1.4 References
- IEEE 830-1998: Software Requirements Specification
- IEEE 1471-2000: Software Architecture Documentation
- Xiaomi MiMo V2.5 API Documentation
- DichGame Project Documentation
- manga-image-translator Documentation
- MIMO-AXON Project Documentation

---

## 2. Overall Description

### 2.1 System Perspective
UTH is a client-server system running on the user's machine, connecting to the Xiaomi MiMo API for AI processing. The system has 3 parallel pipelines, orchestrated by a Director Agent.

### 2.2 Key Functions
1. **FR-01**: Automatically identify the input content type (game/manga/film)
2. **FR-02**: Extract text from game files (12 engines)
3. **FR-03**: OCR text from manga/comic images
4. **FR-04**: STT from audio/video
5. **FR-05**: Translate multilingual text into Vietnamese
6. **FR-06**: Inpainting (remove original text from images)
7. **FR-07**: Render translated text into images
8. **FR-08**: TTS — generate Vietnamese speech
9. **FR-09**: Voice clone — clone character voices
10. **FR-10**: Synchronize audio with video
11. **FR-11**: Translation Memory — cache translations
12. **FR-12**: Glossary Manager — manage terminology
13. **FR-13**: Automated QA — evaluate translation quality
14. **FR-14**: Unified Dashboard — monitor all pipelines

### 2.3 User Characteristics

| User Type | Description |
|-----------|-------------|
| Gamer | Wants to localize Chinese/Japanese games without coding knowledge |
| Manga reader | Wants to read high-quality Vietnamese manga |
| Film viewer | Wants to watch Chinese/Japanese films with Vietnamese dubbing |
| Developer | Wants to integrate UTH into their workflow |

### 2.4 Constraints
- Runs on Windows 10/11 (primary), Linux (secondary)
- Requires NVIDIA GPU (CUDA) for local processing
- Requires internet for MiMo API calls
- Python 3.10+

### 2.5 Assumptions and Dependencies
- Xiaomi MiMo API is always available (99.9% uptime)
- User has an NVIDIA GPU with CUDA support
- Game/manga/video files are not DRM-protected or copyrighted

---

## 3. Functional Requirements

### 3.1 Director Agent (FR-01)

**Description:** The main agent, using MiMo-V2.5-Pro, orchestrating the entire system.

| ID | Requirement | Priority |
|----|------------|----------|
| FR-01.1 | Accept input from the user (file/directory path) | P0 |
| FR-01.2 | Classify the content type (game/manga/film) | P0 |
| FR-01.3 | Select the appropriate pipeline | P0 |
| FR-01.4 | Coordinate sub-agents in the correct order | P0 |
| FR-01.5 | Handle errors and retry when a sub-agent fails | P1 |
| FR-01.6 | Report progress in real time | P1 |

### 3.2 Game Pipeline (FR-02)

**Description:** Translate games from 12 different engines.

| ID | Requirement | Priority |
|----|------------|----------|
| FR-02.1 | Automatically identify the game engine (magic bytes, file signature) | P0 |
| FR-02.2 | Extract text from game files | P0 |
| FR-02.3 | Translate text via MiMo-V2.5 | P0 |
| FR-02.4 | Inject the translation back into the game files | P0 |
| FR-02.5 | Handle Vietnamese fonts (detect, subset, embed) | P0 |
| FR-02.6 | Repackage the complete game | P1 |
| FR-02.7 | Support batch processing (multiple games simultaneously) | P2 |

### 3.3 Manga Pipeline (FR-03, FR-06, FR-07)

**Description:** Translate manga/comic images from scans.

| ID | Requirement | Priority |
|----|------------|----------|
| FR-03.1 | Detect text bubbles in images | P0 |
| FR-03.2 | OCR text from images | P0 |
| FR-03.3 | Translate text via MiMo-V2.5 | P0 |
| FR-03.4 | Remove original text (inpainting) | P0 |
| FR-03.5 | Render translated text into images | P0 |
| FR-03.6 | Support 26 source languages | P1 |
| FR-03.7 | Batch processing (entire chapters/volumes) | P1 |

### 3.4 Film Pipeline (FR-04, FR-08, FR-09, FR-10)

**Description:** Automatically translate and dub films/videos.

| ID | Requirement | Priority |
|----|------------|----------|
| FR-04.1 | OCR hard-coded subtitles from video | P0 |
| FR-04.2 | STT — convert speech to text | P0 |
| FR-04.3 | Translate text via MiMo-V2.5 | P0 |
| FR-04.4 | TTS — generate Vietnamese speech | P0 |
| FR-04.5 | Synchronize TTS audio with the original video | P0 |
| FR-04.6 | Volume ducking (lower film volume when TTS is speaking) | P1 |
| FR-04.7 | Voice clone — clone character voices | P1 |
| FR-04.8 | VLC integration — real-time dubbing | P2 |

### 3.5 Shared Services (FR-11, FR-12, FR-13)

| ID | Requirement | Priority |
|----|------------|----------|
| FR-11.1 | Store translations in SQLite database | P0 |
| FR-11.2 | Search for existing translations (fuzzy match) | P0 |
| FR-11.3 | Automatically reuse previous translations | P0 |
| FR-12.1 | Manage terminology (CRUD) | P1 |
| FR-12.2 | Apply glossary before translation | P1 |
| FR-12.3 | Export/Import glossary (JSON, CSV) | P2 |
| FR-13.1 | Automatically evaluate translations (1-10 score) | P1 |
| FR-13.2 | Detect translation errors (wrong meaning, missing sentences) | P1 |
| FR-13.3 | Suggest translation improvements | P2 |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Target Value |
|----|------------|-------------|
| NFR-01 | Translation time per game text sentence | < 2 seconds |
| NFR-02 | Processing time per manga page | < 30 seconds |
| NFR-03 | Translation time per film episode (45 min) | < 30 minutes |
| NFR-04 | MiMo API response time | < 5 seconds (P95) |
| NFR-05 | Concurrent pipelines | Minimum 3 (parallel) |

### 4.2 Reliability

| ID | Requirement | Target Value |
|----|------------|-------------|
| NFR-06 | Uptime (when internet is available) | 99.5% |
| NFR-07 | Retry on API failure | 3 attempts, exponential backoff |
| NFR-08 | Data integrity | No loss of original files on error |
| NFR-09 | Translation Memory durability | SQLite WAL mode |

### 4.3 Scalability

| ID | Requirement |
|----|------------|
| NFR-10 | Add new game engines without modifying core code |
| NFR-11 | Add new languages without modifying the translator |
| NFR-12 | Add new AI providers (OpenAI, DeepSeek, etc.) without modifying the pipeline |

### 4.4 Security

| ID | Requirement |
|----|------------|
| NFR-13 | API keys stored in .env, not committed to git |
| NFR-14 | No uploading of game/manga/video files to the cloud |
| NFR-15 | MiMo API calls over HTTPS |

### 4.5 Usability

| ID | Requirement |
|----|------------|
| NFR-16 | CLI interface for developers |
| NFR-17 | Web Dashboard for general users |
| NFR-18 | Progress bar for batch processing |
| NFR-19 | Error messages in Vietnamese, easy to understand |

---

## 5. System Interfaces

### 5.1 Xiaomi MiMo API
- Endpoint: `https://api.mimo.xiaomi.com/v1/`
- Models: MiMo-V2.5-Pro, MiMo-V2.5, MiMo-V2.5-TTS, MiMo-TTS-VoiceClone, MiMo-TTS-VoiceDesign
- Auth: API Key (Bearer token)
- Format: OpenAI-compatible API

### 5.2 External Tools
- **FFmpeg**: Video/audio processing
- **VLC**: Media playback + HTTP API
- **SQLite**: Local database
- **espeak-ng**: Phonemization for TTS

---

## 6. Data Requirements

### 6.1 Translation Memory Database
```sql
CREATE TABLE translations (
    id INTEGER PRIMARY KEY,
    source_text TEXT NOT NULL,
    source_lang TEXT NOT NULL,
    target_text TEXT NOT NULL,
    target_lang TEXT DEFAULT 'vi',
    context TEXT,
    pipeline TEXT,  -- 'game', 'manga', 'film'
    quality_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 Glossary Database
```sql
CREATE TABLE glossary (
    id INTEGER PRIMARY KEY,
    term TEXT NOT NULL,
    translation TEXT NOT NULL,
    category TEXT,  -- 'character', 'place', 'skill', 'item'
    source_lang TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Supporting Documentation
- [SAD.md](../SAD.md) — System Architecture
- [SDP.md](../SDP.md) — Development Plan
- [FEASIBILITY.md](../FEASIBILITY.md) — Feasibility Study
- [RESOURCES.md](../RESOURCES.md) — Resources & References
