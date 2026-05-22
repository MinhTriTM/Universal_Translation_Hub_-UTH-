# Software Architecture Document (SAD)
## システムアーキテクチャ文書 — Universal Translation Hub (UTH)

**バージョン:** 1.0
**日付:** 2026-05-22
**著者:** Doan Minh Tri
**参照規格:** IEEE 1471-2000 (ISO/IEC 42010)

---

## 1. アーキテクチャ概要

### 1.1 ステークホルダーと関心事

| ステークホルダー | 関心事 |
|-----------------|--------|
| エンドユーザー | 操作性の良さ、高速性、翻訳品質の高さ |
| 開発者 | モジュール性、拡張容易性、保守容易性 |
| Xiaomi MiMo | MiMoエコシステムの効率的利用、トークン消費 |
| コミュニティ | オープンソース、貢献の容易さ |

### 1.2 ビューポイント

本書は4つのビューポイントからアーキテクチャを記述する：
1. **Logical View** — モジュール構造、エージェントの責務
2. **Process View** — ランタイム動作、データフロー
3. **Physical View** — デプロイメント、ハードウェア
4. **Development View** — コード構造、ビルド、テスト

---

## 2. Logical View — 論理アーキテクチャ

### 2.1 レイヤードアーキテクチャ

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

### 2.2 エージェント設計パターン

各エージェントは共通インターフェースを実装する：

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
        """タスクを実行し、結果を返す"""
        pass

    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """このエージェントが指定されたタスクタイプを処理できるか確認する"""
        pass
```

### 2.3 MiMo API Client

```python
class MiMoClient:
    """Xiaomi MiMo API用クライアントラッパー — OpenAI互換フォーマット"""

    def __init__(self, api_key: str, base_url: str = "https://api.mimo.xiaomi.com/v1"):
        self.api_key = api_key
        self.base_url = base_url

    async def chat_completion(self, model: str, messages: list, **kwargs) -> str:
        """MiMo chat completion APIを呼び出す"""
        pass

    async def tts(self, text: str, voice: str = "vi-VN-Standard") -> bytes:
        """MiMo TTS APIを呼び出し、音声バイトデータを返す"""
        pass

    async def voice_clone(self, audio_sample: bytes, text: str) -> bytes:
        """サンプル音声から声をクローンする"""
        pass
```

---

## 3. Process View — 処理フロー

### 3.1 ゲーム翻訳フロー

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

### 3.2 漫画翻訳フロー

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

### 3.3 映画吹き替えフロー

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

## 4. Physical View — デプロイメント

### 4.1 デプロイメント図

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

### 4.2 ハードウェア要件

| コンポーネント | 最小構成 | 推奨構成 |
|---------------|---------|---------|
| CPU | Intel i5 / AMD Ryzen 5 | Intel i7 / AMD Ryzen 7 |
| GPU | NVIDIA GTX 1060 6GB | NVIDIA RTX 4060 8GB+ |
| RAM | 8GB | 16GB+ |
| ストレージ | 10GB空き容量 | 50GB空き容量（モデル用） |
| ネットワーク | 10 Mbps | 50 Mbps+ |

---

## 5. Development View — コード構造

### 5.1 モジュール依存グラフ

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

### 5.2 技術スタック

| レイヤー | 技術 | バージョン |
|---------|------|-----------|
| 言語 | Python | 3.12+ |
| Webフレームワーク | FastAPI | 0.110+ |
| 非同期ランタイム | uvicorn | 0.29+ |
| データベース | SQLite | 3.45+ |
| 動画処理 | FFmpeg | 6.0+ |
| メディアプレーヤー | VLC | 3.0+ |
| HTTPクライアント | httpx | 0.27+ |
| データバリデーション | pydantic | 2.7+ |
| CLI | argparse | stdlib |
| TTS（ローカルフォールバック） | edge-tts | 6.1+ |

---

## 6. 設計決定事項

### DD-01: MiMoをプライマリAIプロバイダーとして選定
- **決定:** MiMo V2.5シリーズをメインAIとして使用
- **理由:** 1パッケージで8モデル、OpenAI互換API、コスト効率が高い
- **トレードオフ:** ベンダーロックイン → Abstract Providerパターンで緩和

### DD-02: マルチエージェント vs モノリシック
- **決定:** 10エージェントのアーキテクチャ
- **理由:** 各パイプラインに固有の要件があり、保守のために分離が必要
- **トレードオフ:** 複雑性の増加 → 共通BaseAgentインターフェースで緩和

### DD-03: SQLite vs PostgreSQL
- **決定:** Translation MemoryにSQLiteを使用
- **理由:** ゼロコンフィグ、ポータブル、シングルユーザーに十分
- **トレードオフ:** 同時書き込み非対応 → WALモードで緩和

### DD-04: AI向けProviderパターン
- **決定:** Abstract ProviderによりAIバックエンドの切り替えを可能にする
- **理由:** MiMo障害時にOpenAI/DeepSeekへフォールバック可能
- **トレードオフ:** 抽象化レイヤーの追加 → 明確なインターフェースで簡素化
