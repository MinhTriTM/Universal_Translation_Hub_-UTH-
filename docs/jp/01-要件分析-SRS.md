# Software Requirements Specification (SRS)
## ソフトウェア要件仕様 — Universal Translation Hub (UTH)

**バージョン:** 1.0
**日付:** 2026-05-22
**著者:** Doan Minh Tri
**参照規格:** IEEE 830-1998

---

## 1. はじめに

### 1.1 目的
本書は、**Universal Translation Hub (UTH)** プロジェクトのソフトウェア要件を規定する。UTHは、ゲーム、漫画、映画向けの汎用AIマルチエージェント翻訳システムである。

### 1.2 範囲
UTHは3種類のコンテンツの自動翻訳をサポートする：
- **ゲーム**: 12種類のゲームエンジン（RPG Maker、Unity、Ren'Py、Kirikiri、CatSystem2、NScripter、TyranoBuilder、Web/HTML5、NW.js、Wolf RPG、Binary）
- **漫画/コミック**: OCR → 翻訳 → インペインティング → レンダリング
- **映画/動画**: STT → 翻訳 → TTS → 音声同期

### 1.3 定義および用語

| 用語 | 定義 |
|------|------|
| Agent | 特定の目標を持つ自動AIエージェント |
| Pipeline | 逐次または並列の処理チェーン |
| TTS | Text-to-Speech（音声合成） |
| STT | Speech-to-Text（音声認識） |
| OCR | Optical Character Recognition（光学文字認識） |
| Inpainting | 元のテキストを削除し、画像の背景を復元する処理 |
| Translation Memory | 既存の翻訳を保存するデータベース |
| Glossary | 統一された用語集 |

### 1.4 参考文献
- IEEE 830-1998: Software Requirements Specification
- IEEE 1471-2000: Software Architecture Documentation
- Xiaomi MiMo V2.5 API Documentation
- DichGame Project Documentation
- manga-image-translator Documentation
- MIMO-AXON Project Documentation

---

## 2. 概要

### 2.1 システムの展望
UTHはクライアントサーバーシステムであり、ユーザーのマシン上で稼働し、AI処理のためにXiaomi MiMo APIに接続する。システムは3つの並列パイプラインを持ち、Director Agentによって統括される。

### 2.2 主要機能
1. **FR-01**: 入力コンテンツの種類を自動識別（ゲーム/漫画/映画）
2. **FR-02**: ゲームファイルからのテキスト抽出（12エンジン）
3. **FR-03**: 漫画/コミック画像からのOCRテキスト抽出
4. **FR-04**: 音声/動画からのSTT
5. **FR-05**: 多言語テキストのベトナム語への翻訳
6. **FR-06**: インペインティング（画像から元のテキストを除去）
7. **FR-07**: 翻訳テキストの画像へのレンダリング
8. **FR-08**: TTS — ベトナム語音声の生成
9. **FR-09**: ボイスクローン — キャラクター声のクローン
10. **FR-10**: 音声と動画の同期
11. **FR-11**: Translation Memory — 翻訳のキャッシュ
12. **FR-12**: Glossary Manager — 用語管理
13. **FR-13**: 自動QA — 翻訳品質の評価
14. **FR-14**: Unified Dashboard — 全パイプラインの監視

### 2.3 ユーザー特性

| ユーザー種別 | 説明 |
|-------------|------|
| ゲーマー | 中国/日本のゲームをベトナム語化したい（コーディング不要） |
| 漫画読者 | 高品質なベトナム語漫画を読みたい |
| 映画視聴者 | 中国/日本映画をベトナム語吹き替えで観たい |
| 開発者 | UTHを自身のワークフローに統合したい |

### 2.4 制約条件
- Windows 10/11（プライマリ）、Linux（セカンダリ）で動作
- ローカル処理にはNVIDIA GPU（CUDA）が必要
- MiMo API呼び出しにはインターネットが必要
- Python 3.10+

### 2.5 前提条件と依存関係
- Xiaomi MiMo APIが常に利用可能（99.9% uptime）
- ユーザーがCUDA対応のNVIDIA GPUを保有
- ゲーム/漫画/動画ファイルがDRM/著作権保護されていない

---

## 3. 機能要件（Functional Requirements）

### 3.1 Director Agent（FR-01）

**説明:** メインエージェント。MiMo-V2.5-Proを使用し、システム全体を統括する。

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-01.1 | ユーザーからの入力を受け取る（ファイル/フォルダパス） | P0 |
| FR-01.2 | コンテンツの種類を分類（ゲーム/漫画/映画） | P0 |
| FR-01.3 | 適切なパイプラインを選択 | P0 |
| FR-01.4 | サブエージェントを正しい順序で調整 | P0 |
| FR-01.5 | サブエージェント失敗時のエラー処理とリトライ | P1 |
| FR-01.6 | リアルタイム進捗報告 | P1 |

### 3.2 Game Pipeline（FR-02）

**説明:** 12種類の異なるエンジンからのゲーム翻訳。

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-02.1 | ゲームエンジンの自動識別（magic bytes、ファイル署名） | P0 |
| FR-02.2 | ゲームファイルからのテキスト抽出 | P0 |
| FR-02.3 | MiMo-V2.5によるテキスト翻訳 | P0 |
| FR-02.4 | 翻訳結果をゲームファイルに注入 | P0 |
| FR-02.5 | ベトナム語フォント処理（検出、サブセット、埋め込み） | P0 |
| FR-02.6 | 完成したゲームの再パッケージ化 | P1 |
| FR-02.7 | バッチ処理対応（複数ゲーム同時処理） | P2 |

### 3.3 Manga Pipeline（FR-03、FR-06、FR-07）

**説明:** スキャン画像からの漫画/コミック翻訳。

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-03.1 | 画像内のテキスト吹き出しを検出 | P0 |
| FR-03.2 | 画像からのOCRテキスト抽出 | P0 |
| FR-03.3 | MiMo-V2.5によるテキスト翻訳 | P0 |
| FR-03.4 | 元のテキストの削除（インペインティング） | P0 |
| FR-03.5 | 翻訳テキストの画像へのレンダリング | P0 |
| FR-03.6 | 26言語のソース言語対応 | P1 |
| FR-03.7 | バッチ処理（章/巻単位） | P1 |

### 3.4 Film Pipeline（FR-04、FR-08、FR-09、FR-10）

**説明:** 映画/動画の自動翻訳および吹き替え。

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-04.1 | 動画からハードサブタイトルのOCR | P0 |
| FR-04.2 | STT — 音声をテキストに変換 | P0 |
| FR-04.3 | MiMo-V2.5によるテキスト翻訳 | P0 |
| FR-04.4 | TTS — ベトナム語音声の生成 | P0 |
| FR-04.5 | TTS音声とオリジナル動画の同期 | P0 |
| FR-04.6 | ボリュームダッキング（TTS発話中の映画音量低下） | P1 |
| FR-04.7 | ボイスクローン — キャラクター声のクローン | P1 |
| FR-04.8 | VLC連携 — リアルタイム吹き替え | P2 |

### 3.5 Shared Services（FR-11、FR-12、FR-13）

| ID | 要件 | 優先度 |
|----|------|--------|
| FR-11.1 | 翻訳をSQLiteデータベースに保存 | P0 |
| FR-11.2 | 既存翻訳の検索（ファジーマッチ） | P0 |
| FR-11.3 | 既存翻訳の自動再利用 | P0 |
| FR-12.1 | 用語管理（CRUD） | P1 |
| FR-12.2 | 翻訳前のグロス適用 | P1 |
| FR-12.3 | グロスのエクスポート/インポート（JSON、CSV） | P2 |
| FR-13.1 | 翻訳の自動評価（1-10スコア） | P1 |
| FR-13.2 | 翻訳エラーの検出（誤訳、文欠落） | P1 |
| FR-13.3 | 翻訳改善の提案 | P2 |

---

## 4. 非機能要件（Non-Functional Requirements）

### 4.1 性能（Performance）

| ID | 要件 | 目標値 |
|----|------|--------|
| NFR-01 | ゲームテキスト1文の翻訳時間 | < 2秒 |
| NFR-02 | 漫画1ページの処理時間 | < 30秒 |
| NFR-03 | 映画1話（45分）の翻訳時間 | < 30分 |
| NFR-04 | MiMo APIレスポンスタイム | < 5秒（P95） |
| NFR-05 | 同時パイプライン数 | 最低3（並列） |

### 4.2 信頼性（Reliability）

| ID | 要件 | 目標値 |
|----|------|--------|
| NFR-06 | アップタイム（インターネット接続時） | 99.5% |
| NFR-07 | API障害時のリトライ | 3回、指数バックオフ |
| NFR-08 | データ整合性 | エラー時に元ファイルを失わない |
| NFR-09 | Translation Memoryの耐久性 | SQLite WALモード |

### 4.3 拡張性（Scalability）

| ID | 要件 |
|----|------|
| NFR-10 | コアコードの修正なしにゲームエンジンを追加可能 |
| NFR-11 | トランスレーターの修正なしに新しい言語を追加可能 |
| NFR-12 | パイプラインの修正なしに新しいAIプロバイダー（OpenAI、DeepSeek等）を追加可能 |

### 4.4 セキュリティ（Security）

| ID | 要件 |
|----|------|
| NFR-13 | APIキーは.envに保存し、gitにコミットしない |
| NFR-14 | ゲーム/漫画/動画ファイルをクラウドにアップロードしない |
| NFR-15 | MiMo API呼び出しはHTTPS経由 |

### 4.5 使用性（Usability）

| ID | 要件 |
|----|------|
| NFR-16 | 開発者向けCLIインターフェース |
| NFR-17 | 一般ユーザー向けWebダッシュボード |
| NFR-18 | バッチ処理用プログレスバー |
| NFR-19 | ベトナム語で分かりやすいエラーメッセージ |

---

## 5. システムインターフェース

### 5.1 Xiaomi MiMo API
- エンドポイント: `https://api.mimo.xiaomi.com/v1/`
- モデル: MiMo-V2.5-Pro、MiMo-V2.5、MiMo-V2.5-TTS、MiMo-TTS-VoiceClone、MiMo-TTS-VoiceDesign
- 認証: API Key（Bearer token）
- フォーマット: OpenAI互換API

### 5.2 外部ツール
- **FFmpeg**: 動画/音声処理
- **VLC**: メディア再生 + HTTP API
- **SQLite**: ローカルデータベース
- **espeak-ng**: TTS向けの音素化

---

## 6. データ要件

### 6.1 Translation Memoryデータベース
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

### 6.2 Glossaryデータベース
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

## 7. 関連資料
- [SAD.md](../SAD.md) — システムアーキテクチャ
- [SDP.md](../SDP.md) — 開発計画
- [FEASIBILITY.md](../FEASIBILITY.md) — 実現可能性調査
- [RESOURCES.md](../RESOURCES.md) — リソースおよび参考文献
