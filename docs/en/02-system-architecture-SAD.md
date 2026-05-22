# Software Architecture Document (SAD)
## System Architecture Document — Universal Translation Hub (UTH)

**Version:** 1.0
**Date:** 2026-05-22
**Author:** Doan Minh Tri
**Reference Standard:** IEEE 1471-2000 (ISO/IEC 42010)

---

## 1. Architecture Overview

### 1.1 Stakeholders & Concerns

| Stakeholder | Concerns |
|-------------|----------|
| End user | Ease of use, speed, high translation quality |
| Developer | Modular, easily extensible, easy to maintain |
| Xiaomi MiMo | Efficient use of MiMo ecosystem, token consumption |
| Community | Open source, easy to contribute |

### 1.2 Viewpoints

This document describes the architecture from 4 viewpoints:
1. **Logical View** — Module structure, agent responsibilities
2. **Process View** — Runtime behavior, data flow
3. **Physical View** — Deployment, hardware
4. **Development View** — Code structure, build, test

---

## 2. Logical View — Logical Architecture

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│    CLI (argparse)  │  Web Dashboard (FastAPI + HTML)     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   ORCHESTRATION LAYER                    │
│    Director Agent (MiMo-V2.5-Pro)                       │
│    Router Agent  │  QA Agent  │  Progress Reporter       │
└────────┬──────────┬──────────┬──────────────────────────┘
         │          │          │
┌────────▼────┐ ┌──▼───────┐ ┌▼──────────────┐
│ GAME PIPE   │ │ MANGA    │ │ FILM PIPELINE  │
│ LINE        │ │ PIPELINE │ │                │
│ ┌─────────┐ │ │ ┌──────┐ │ │ ┌────────────┐ │
│ │Detector │ │ │ │Detect│ │ │ │ SubtitleOCR│ │
│ │Extractor│ │ │ │OCR   │ │ │ │ AudioSTT   │ │
│ │Translator│ │ │ │Inpaint│ │ │ │ Translator │ │
│ │Injector │ │ │ │Render│ │ │ │ TTS/Voice  │ │
│ │Packager │ │ │ └──────┘ │ │ │ AudioSync  │ │
│ └─────────┘ │ │          │ │ └────────────┘ │
└─────────────┘ └──────────┘ └────────────────┘
         │          │          │
┌────────▼──────────▼──────────▼──────────────────────────┐
│                   SERVICES LAYER                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │MiMo API  │ │Translation│ │Glossary  │ │File I/O   │  │
│  │Client    │ │Memory    │ │Manager   │ │Handler    │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────┘
         │
┌────────▼────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                   │
│  SQLite  │  FFmpeg  │  VLC HTTP API  │  File System     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Agent Design Pattern

Each Agent implements a common interface:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class AgentTask:
    task_id: str
    task_type: str
    input_data: Any
    context: dict

@dataclass
class AgentResult:
    task_id: str
    success: bool
    output_data: Any
    error: str | None
    metrics: dict

class BaseAgent(ABC):
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model  # MiMo model identifier

    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute the task and return the result"""
        pass

    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """Check whether the agent can handle this task type"""
        pass
```

### 2.3 MiMo API Client

```python
class MiMoClient:
    """Client wrapper for Xiaomi MiMo API — OpenAI-compatible format"""

    def __init__(self, api_key: str, base_url: str = "https://api.mimo.xiaomi.com/v1"):
        self.api_key = api_key
        self.base_url = base_url

    async def chat_completion(self, model: str, messages: list, **kwargs) -> str:
        """Call the MiMo chat completion API"""
        pass

    async def tts(self, text: str, voice: str = "vi-VN-Standard") -> bytes:
        """Call the MiMo TTS API, return audio bytes"""
        pass

    async def voice_clone(self, audio_sample: bytes, text: str) -> bytes:
        """Clone a voice from an audio sample"""
        pass
```

---

## 3. Process View — Processing Flows

### 3.1 Game Translation Flow

```
User Input (game folder)
    │
    ▼
[Router Agent] ──detect engine──▶ [Engine Type?]
    │                                    │
    ▼                                    ▼
[Game Pipeline]                    ┌─────┴─────┐
    │                              │12 engines │
    ▼                              └───────────┘
[TextExtractor Agent]
    │  extract text from .json/.rxdata/.xp3/...
    ▼
[Translator Agent] ◀──check──▶ [Translation Memory]
    │  MiMo-V2.5 translates ZH/JA/KO → VI
    ▼
[QA Agent] ──quality score──▶ [If score < 7: retry]
    │
    ▼
[TextInjector Agent]
    │  inject VI text back into game files
    ▼
[Font Handler]
    │  detect, subset, embed Vietnamese font
    ▼
[Packager Agent]
    │  repack game files
    ▼
Output (Vietnamese game)
```

### 3.2 Manga Translation Flow

```
User Input (image folder)
    │
    ▼
[Router Agent] ──detect──▶ [Image files?]
    │
    ▼
[Manga Pipeline]
    │
    ├─▶ [TextDetector Agent] ── find text bubbles
    │       │
    ▼       ▼
[OCR Agent] ◀──bubble regions──┘
    │  MiMo-V2.5 reads text from image
    ▼
[Translator Agent] ◀──check──▶ [Translation Memory]
    │  MiMo-V2.5 translates → VI
    ▼
[QA Agent]
    │
    ▼
[Inpainting Agent]
    │  remove original text, restore background
    ▼
[Render Agent]
    │  render Vietnamese text into bubbles
    ▼
Output (Vietnamese manga images)
```

### 3.3 Film Dubbing Flow

```
User Input (video + subtitle)
    │
    ▼
[Router Agent] ──detect──▶ [Video + Subtitle?]
    │
    ▼
[Film Pipeline]
    │
    ├─▶ [SubtitleOCR Agent] ── if hard sub exists
    │       │
    ├─▶ [STT Agent] ── if audio speech exists
    │       │
    ▼       ▼
[Translator Agent] ◀──subtitle text──┘
    │  MiMo-V2.5 translates → VI
    ▼
[QA Agent]
    │
    ▼
[Voice Agent]
    │  MiMo-V2.5-TTS generates Vietnamese audio
    │  (option: VoiceClone for character voices)
    ▼
[AudioSync Agent]
    │  sync TTS audio with original timeline
    │  apply volume ducking
    ▼
[FFmpeg Mixer]
    │  mix TTS audio + original audio
    ▼
Output (Vietnamese dubbed video)
```

---

## 4. Physical View — Deployment

### 4.1 Deployment Diagram

```
┌─────────────────────────────────────────────┐
│              User's Machine                  │
│    (Windows 11 / Ubuntu 22.04)              │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │     UTH Application (Python 3.12)    │   │
│  │                                      │   │
│  │  ┌─────────┐  ┌─────────┐           │   │
│  │  │CLI      │  │Web UI   │           │   │
│  │  │(argparse│  │(FastAPI)│           │   │
│  │  └────┬────┘  └────┬────┘           │   │
│  │       └──────┬─────┘                │   │
│  │              │                       │   │
│  │  ┌───────────▼───────────────────┐  │   │
│  │  │     Director + 9 Agents       │  │   │
│  │  └───────────┬───────────────────┘  │   │
│  │              │                       │   │
│  │  ┌───────────▼───────────────────┐  │   │
│  │  │     Services Layer            │  │   │
│  │  │  (MiMo Client, TM, Glossary)  │  │   │
│  │  └───────────┬───────────────────┘  │   │
│  └──────────────┼──────────────────────┘   │
│                 │                           │
│  ┌──────────────▼──────────────────────┐   │
│  │     Local Infrastructure            │   │
│  │  SQLite │ FFmpeg │ VLC │ File System│   │
│  └─────────────────────────────────────┘   │
└────────────────────┬────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────┐
│         Xiaomi MiMo Cloud API               │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐  │
│  │V2.5-Pro │ │V2.5     │ │TTS/Voice     │  │
│  │(Reason) │ │(General)│ │Clone/Design  │  │
│  └─────────┘ └─────────┘ └──────────────┘  │
└─────────────────────────────────────────────┘
```

### 4.2 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Intel i5 / AMD Ryzen 5 | Intel i7 / AMD Ryzen 7 |
| GPU | NVIDIA GTX 1060 6GB | NVIDIA RTX 4060 8GB+ |
| RAM | 8GB | 16GB+ |
| Storage | 10GB free | 50GB free (for models) |
| Network | 10 Mbps | 50 Mbps+ |

---

## 5. Development View — Code Structure

### 5.1 Module Dependency Graph

```
main.py
  ├── src/agents/
  │     ├── base.py          (BaseAgent ABC)
  │     ├── director.py      → depends: all agents
  │     ├── router.py        → depends: pipelines
  │     ├── translator.py    → depends: mimo_client, memory
  │     ├── ocr_agent.py     → depends: mimo_client
  │     ├── inpainting.py    → depends: mimo_client
  │     ├── render.py        → depends: mimo_client
  │     ├── stt_agent.py     → depends: mimo_client
  │     ├── voice_agent.py   → depends: mimo_client
  │     └── qa_agent.py      → depends: mimo_client
  ├── src/pipelines/
  │     ├── game/            → depends: agents, services
  │     ├── manga/           → depends: agents, services
  │     └── film/            → depends: agents, services
  ├── src/services/
  │     ├── mimo_client.py   → no internal deps
  │     ├── memory.py        → depends: sqlite3
  │     ├── glossary.py      → depends: memory
  │     └── file_handler.py  → depends: pathlib
  └── src/utils/
        ├── config.py        → depends: dotenv
        └── logger.py        → depends: logging
```

### 5.2 Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| Web Framework | FastAPI | 0.110+ |
| Async Runtime | uvicorn | 0.29+ |
| Database | SQLite | 3.45+ |
| Video Processing | FFmpeg | 6.0+ |
| Media Player | VLC | 3.0+ |
| HTTP Client | httpx | 0.27+ |
| Data Validation | pydantic | 2.7+ |
| CLI | argparse | stdlib |
| TTS (local fallback) | edge-tts | 6.1+ |

---

## 6. Design Decisions

### DD-01: Choosing MiMo as the Primary AI Provider
- **Decision:** Use MiMo V2.5 series as the primary AI
- **Rationale:** 8 models in a single package, OpenAI-compatible API, cost-effective
- **Tradeoff:** Vendor lock-in -> Mitigated via Abstract Provider pattern

### DD-02: Multi-Agent vs Monolithic
- **Decision:** 10-agent architecture
- **Rationale:** Each pipeline has its own requirements and needs to be separated for maintainability
- **Tradeoff:** Increased complexity -> Mitigated via a common BaseAgent interface

### DD-03: SQLite vs PostgreSQL
- **Decision:** SQLite for Translation Memory
- **Rationale:** Zero-config, portable, sufficient for single-user
- **Tradeoff:** No concurrent write support -> Mitigated via WAL mode

### DD-04: Provider Pattern for AI
- **Decision:** Abstract Provider allows swapping the AI backend
- **Rationale:** Can fall back to OpenAI/DeepSeek if MiMo is down
- **Tradeoff:** Additional abstraction layer -> Simplified via a clear interface
