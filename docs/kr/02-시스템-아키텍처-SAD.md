# Software Architecture Document (SAD)
## 시스템 아키텍처 문서 — Universal Translation Hub (UTH)

**버전:** 1.0
**날짜:** 2026-05-22
**저자:** Đoàn Minh Trí
**참고 표준:** IEEE 1471-2000 (ISO/IEC 42010)

---

## 1. 아키텍처 개요

### 1.1 이해관계자 및 관심사

| 이해관계자 | 관심사 |
|-----------|--------|
| 최종 사용자 | 사용 용이성, 속도, 높은 번역 품질 |
| 개발자 | 모듈화, 확장 용이성, 유지보수 용이성 |
| Xiaomi MiMo | MiMo 에코시스템의 효율적 활용, 토큰 소비 |
| 커뮤니티 | 오픈 소스, 기여 용이성 |

### 1.2 뷰포인트

이 문서는 4개의 뷰포인트에 따라 아키텍처를 기술합니다:
1. **Logical View** — 모듈 구조, 에이전트 책임
2. **Process View** — 런타임 동작, 데이터 흐름
3. **Physical View** — 배포, 하드웨어
4. **Development View** — 코드 구조, 빌드, 테스트

---

## 2. Logical View — 논리적 아키텍처

### 2.1 계층형 아키텍처 (Layered Architecture)

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

### 2.2 에이전트 설계 패턴

모든 에이전트는 공통 인터페이스를 구현합니다:

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
        """태스크를 실행하고 결과를 반환"""
        pass

    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """에이전트가 해당 태스크 유형을 처리할 수 있는지 확인"""
        pass
```

### 2.3 MiMo API 클라이언트

```python
class MiMoClient:
    """Xiaomi MiMo API 클라이언트 래퍼 — OpenAI-compatible format"""

    def __init__(self, api_key: str, base_url: str = "https://api.mimo.xiaomi.com/v1"):
        self.api_key = api_key
        self.base_url = base_url

    async def chat_completion(self, model: str, messages: list, **kwargs) -> str:
        """MiMo chat completion API 호출"""
        pass

    async def tts(self, text: str, voice: str = "vi-VN-Standard") -> bytes:
        """MiMo TTS API 호출, 오디오 바이트 반환"""
        pass

    async def voice_clone(self, audio_sample: bytes, text: str) -> bytes:
        """샘플 오디오에서 음성 클론"""
        pass
```

---

## 3. Process View — 처리 프로세스

### 3.1 게임 번역 흐름

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

### 3.2 만화 번역 흐름

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

### 3.3 영화 더빙 흐름

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

## 4. Physical View — 배포

### 4.1 배포 다이어그램

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

### 4.2 하드웨어 요구사항

| 구성요소 | 최소 사양 | 권장 사양 |
|----------|-----------|-----------|
| CPU | Intel i5 / AMD Ryzen 5 | Intel i7 / AMD Ryzen 7 |
| GPU | NVIDIA GTX 1060 6GB | NVIDIA RTX 4060 8GB+ |
| RAM | 8GB | 16GB+ |
| 저장 공간 | 10GB 여유 | 50GB 여유 (모델용) |
| 네트워크 | 10 Mbps | 50 Mbps+ |

---

## 5. Development View — 코드 구조

### 5.1 모듈 의존성 그래프

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

### 5.2 기술 스택

| 계층 | 기술 | 버전 |
|------|------|------|
| 언어 | Python | 3.12+ |
| 웹 프레임워크 | FastAPI | 0.110+ |
| 비동기 런타임 | uvicorn | 0.29+ |
| 데이터베이스 | SQLite | 3.45+ |
| 비디오 처리 | FFmpeg | 6.0+ |
| 미디어 플레이어 | VLC | 3.0+ |
| HTTP 클라이언트 | httpx | 0.27+ |
| 데이터 검증 | pydantic | 2.7+ |
| CLI | argparse | stdlib |
| TTS (로컬 폴백) | edge-tts | 6.1+ |

---

## 6. 설계 결정

### DD-01: MiMo를 주요 AI 프로바이더로 선택
- **결정:** MiMo V2.5 시리즈를 주요 AI로 사용
- **이유:** 1개 패키지에 8개 모델, OpenAI 호환 API, 비용 효율적
- **트레이드오프:** 벤더 종속 → 추상 프로바이더 패턴으로 완화

### DD-02: 멀티 에이전트 vs 모놀리식
- **결정:** 10개 에이전트 아키텍처
- **이유:** 각 파이프라인이 고유한 요구사항을 가지며, 유지보수를 위해 분리 필요
- **트레이드오프:** 복잡성 증가 → 공통 BaseAgent 인터페이스로 완화

### DD-03: SQLite vs PostgreSQL
- **결정:** Translation Memory에 SQLite 사용
- **이유:** 설정 불필요, 이식성, 단일 사용자에 충분
- **트레이드오프:** 동시 쓰기 미지원 → WAL 모드로 완화

### DD-04: AI를 위한 프로바이더 패턴
- **결정:** 추상 프로바이더로 AI 백엔드 교체 가능
- **이유:** MiMo 다운 시 OpenAI/DeepSeek로 폴백 가능
- **트레이드오프:** 추상화 계층 추가 → 명확한 인터페이스로 단순화
