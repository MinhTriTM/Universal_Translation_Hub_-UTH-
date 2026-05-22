# Software Development Plan (SDP)
## ソフトウェア開発計画 — Universal Translation Hub (UTH)

**バージョン:** 1.0
**日付:** 2026-05-22
**著者:** Doan Minh Tri
**参照規格:** IEEE 1058-1998

---

## 1. プロジェクト概要

| 項目 | 詳細 |
|------|------|
| **プロジェクト名** | Universal Translation Hub (UTH) |
| **目標** | ゲーム、漫画、映画をベトナム語に翻訳するマルチエージェントAIシステム |
| **AIプラットフォーム** | Xiaomi MiMo V2.5（8モデル） |
| **言語** | Python 3.12 |
| **期間** | 8ヶ月（2026年5月〜2026年12月） |
| **担当者** | Doan Minh Tri（DTHU大学） |

---

## 2. ロードマップ

```
2026
月:   5    6    7    8    9    10   11   12
        ├────┤    │    │    │    │    │    │
        Phase 1   │    │    │    │    │    │
        Foundation│    │    │    │    │    │
        │    │    │    │    │    │    │    │
        │    ├────┤    │    │    │    │    │
        │    Phase 2   │    │    │    │    │
        │    Pipeline  │    │    │    │    │
        │    Integration    │    │    │    │
        │    │    │    │    │    │    │    │
        │    │    ├────┤    │    │    │    │
        │    │    Phase 3   │    │    │    │
        │    │    Voice &   │    │    │    │
        │    │    Quality   │    │    │    │
        │    │    │    │    │    │    │    │
        │    │    │    ├────┤    │    │    │
        │    │    │    Phase 4   │    │    │
        │    │    │    Polish &  │    │    │
        │    │    │    Release   │    │    │
        │    │    │    │    ├────┤    │    │
        │    │    │    │    Phase 5   │    │
        │    │    │    │    Scale &   │    │
        │    │    │    │    Optimize  │    │
```

---

## 3. 各フェーズ詳細

### Phase 1: Foundation（2026年5-6月）— 8週間

**目標:** 基盤構築、MiMo API統合、Director Agentの作成。

| # | タスク | 期間 | 成果物 | 優先度 |
|---|--------|------|--------|--------|
| 1.1 | プロジェクト構造のセットアップ | 1週間 | ディレクトリ構造、README、.env | P0 |
| 1.2 | MiMo API Client | 1週間 | mimo_client.py（chat、tts、voice_clone） | P0 |
| 1.3 | BaseAgentフレームワーク | 1週間 | base.py、AgentTask、AgentResult | P0 |
| 1.4 | Director Agent | 1.5週間 | director.py（ルーティング、調整） | P0 |
| 1.5 | Router Agent | 1週間 | router.py（ゲーム/漫画/映画の検出） | P0 |
| 1.6 | Translation Memory | 1週間 | memory.py（SQLite、CRUD、ファジー検索） | P0 |
| 1.7 | Translator Agent | 1週間 | translator.py（MiMo-V2.5翻訳） | P0 |
| 1.8 | Phase 1の単体テスト | 0.5週間 | tests/test_agents.py、test_memory.py | P1 |

**マイルストーン:** Director + Router + Translatorが動作し、MiMo API経由でテキスト翻訳が可能になる。

---

### Phase 2: Pipeline Integration（2026年7-8月）— 8週間

**目標:** 既存プロジェクトから3つのパイプラインを統合する。

| # | タスク | 期間 | 成果物 | 優先度 |
|---|--------|------|--------|--------|
| 2.1 | Game Pipeline — Engine Detector | 1週間 | game/detector.py（12エンジン） | P0 |
| 2.2 | Game Pipeline — Text Extractor | 1.5週間 | game/extractor.py | P0 |
| 2.3 | Game Pipeline — Text Injector | 1.5週間 | game/injector.py | P0 |
| 2.4 | Manga Pipeline — Text Detector | 1週間 | manga/detector.py | P0 |
| 2.5 | Manga Pipeline — OCR Agent | 1週間 | manga/ocr.py | P0 |
| 2.6 | Manga Pipeline — Inpainting | 1週間 | manga/inpaint.py | P0 |
| 2.7 | Manga Pipeline — Renderer | 0.5週間 | manga/render.py | P0 |
| 2.8 | Film Pipeline — Subtitle OCR | 1週間 | film/subtitle_ocr.py | P0 |
| 2.9 | Film Pipeline — STT Agent | 1週間 | film/stt.py | P1 |
| 2.10 | 結合テスト | 1週間 | tests/test_pipelines.py | P1 |

**マイルストーン:** 3つのパイプラインが独立して動作し、Directorが統括できる。

---

### Phase 3: Voice & Quality（2026年9-10月）— 8週間

**目標:** MiMo TTS、QA Agent、Glossaryの統合。

| # | タスク | 期間 | 成果物 | 優先度 |
|---|--------|------|--------|--------|
| 3.1 | Voice Agent — MiMo TTS | 1.5週間 | voice_agent.py（基本TTS） | P0 |
| 3.2 | Voice Clone Agent | 1.5週間 | voice_clone.py | P1 |
| 3.3 | Voice Design Agent | 1週間 | voice_design.py | P2 |
| 3.4 | Audio Sync Agent | 1.5週間 | audio_sync.py（FFmpegミキシング） | P0 |
| 3.5 | Volume Ducking | 0.5週間 | volume_duck.py | P1 |
| 3.6 | QA Agent | 1.5週間 | qa_agent.py（スコアリング、エラー検出） | P1 |
| 3.7 | Glossary Manager | 1週間 | glossary.py（CRUD、インポート/エクスポート） | P1 |
| 3.8 | VLC連携 | 1週間 | vlc_controller.py | P2 |

**マイルストーン:** 音声機能と品質保証が完成する。

---

### Phase 4: Polish & Release（2026年11月）— 4週間

**目標:** 仕上げ、テスト、ドキュメント作成、リリース。

| # | タスク | 期間 | 成果物 | 優先度 |
|---|--------|------|--------|--------|
| 4.1 | Webダッシュボード | 1.5週間 | web/index.html、dashboard API | P1 |
| 4.2 | CLI仕上げ | 0.5週間 | main.py（ヘルプ、プログレスバー） | P0 |
| 4.3 | エラー処理 | 0.5週間 | リトライロジック、グレースフルデグラデーション | P0 |
| 4.4 | ドキュメント作成 | 1週間 | APIドキュメント、ユーザーガイド、サンプル | P0 |
| 4.5 | パフォーマンス最適化 | 0.5週間 | キャッシュ、バッチ処理 | P1 |
| 4.6 | v1.0リリース | 0.5週間 | GitHubリリース、デモ動画 | P0 |

**マイルストーン:** v1.0リリース — 完成した製品。

---

### Phase 5: Scale & Optimize（2026年12月）— 4週間

**目標:** 拡張、最適化、コミュニティ構築。

| # | タスク | 期間 | 成果物 | 優先度 |
|---|--------|------|--------|--------|
| 5.1 | 新言語の追加 | 1週間 | 英語、韓国語、タイ語のサポート追加 | P1 |
| 5.2 | 新ゲームエンジンの追加 | 1週間 | Godot、Unreal対応 | P2 |
| 5.3 | パフォーマンスベンチマーク | 1週間 | ベンチマークレポート | P1 |
| 5.4 | コミュニティとフィードバック | 1週間 | GitHub Issues、Discussions | P1 |

---

## 4. MiMo Credits配分

| フェーズ | 期間 | 見積Credits | 備考 |
|---------|------|------------|------|
| Phase 1 | 5-6月/2026 | ~150M | 開発 + テスト |
| Phase 2 | 7-8月/2026 | ~300M | パイプライン統合が中心 |
| Phase 3 | 9-10月/2026 | ~250M | TTS + QAテスト |
| Phase 4 | 11月/2026 | ~100M | 仕上げ + デモ |
| Phase 5 | 12月/2026 | ~100M | スケールテスト |
| **合計** | **8ヶ月** | **~900M** | **Maxパッケージ（1.6B）の56%** |

---

## 5. リスク管理

| リスク | 確率 | 影響 | 対策 |
|--------|------|------|------|
| MiMo APIダウンタイム | 低 | 高 | OpenAI/DeepSeekへフォールバック |
| GPU不足（ローカル処理向け） | 中 | 中 | クラウドGPU（Google Colab Pro） |
| ゲームエンジンフォーマット変更 | 低 | 中 | モジュラー型抽出パターン |
| 翻訳品質の低さ | 中 | 高 | QA Agent + 人的レビュー |
| スコープクリープ | 高 | 中 | 厳格なフェーズゲート |

---

## 6. 品質保証

### 6.1 テスト戦略

| テスト種別 | 目標カバレッジ | ツール |
|-----------|---------------|--------|
| 単体テスト | 80% | pytest |
| 結合テスト | 60% | pytest + httpx |
| E2Eテスト | 40% | 手動 + スクリプト |
| パフォーマンステスト | 主要パス | locust |

### 6.2 コードレビュー
- Claude Code / Gemini CLIによるセルフレビュー
- プリコミットフック（ruff、mypy）

---

## 7. 構成管理

| ツール | 用途 |
|--------|------|
| Git | ソースコードのバージョン管理 |
| GitHub | リポジトリホスティング、Issues、Actions |
| .env | APIキー、シークレット |
| pyproject.toml | Pythonプロジェクト設定 |
| requirements.txt | 依存関係 |
