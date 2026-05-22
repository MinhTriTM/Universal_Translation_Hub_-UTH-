<div align="center">

# Universal Translation Hub (UTH)

### 汎用多媒体翻訳システム

**Xiaomi MiMo V2.5 搭載 — マルチエージェントアーキテクチャ**

![MiMo](https://img.shields.io/badge/Xiaomi_MiMo-V2.5_Pro-orange)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![Agents](https://img.shields.io/badge/AIエージェント-10-purple)
![Languages](https://img.shields.io/badge/対応言語-6-red)

[Tiếng Việt](README.vn.md) | [English](README.en.md) | [中文](README.cn.md) | [Русский](README.ru.md) | [한국어](README.kr.md)

</div>

---

## 概要

**Universal Translation Hub (UTH)** は、**3種類のマルチメディアコンテンツ**を自動翻訳するマルチエージェントAIシステムです：

| パイプライン | 入力 | 出力 |
|-------------|------|------|
| **ゲーム翻訳** | ゲームファイル（12エンジン：RPG Maker、Unity、Ren'Py、Kirikiri等） | 完全にベトナム語化されたゲーム |
| **漫画翻訳** | 漫画画像（JPG、PNG、PDF） | テキストをレンダリングした翻訳済み画像 |
| **映画吹き替え** | 動画＋字幕（MKV、MP4、ASS、SRT） | AIベトナム語吹き替え付き動画 |

### なぜこのプロジェクトが必要なのか？

> **課題：** 日本、中国、韓国から数百万のゲーム、漫画、映画がベトナム語翻訳を持っていません。手動翻訳は数ヶ月かかり、高コストで、スケールしません。

> **解決策：** UTHは**10個のAIサブエージェント**が自動的に協力し、**Xiaomi MiMo V2.5**を搭載して、あらゆるマルチメディアコンテンツを数分でベトナム語に翻訳します。

---

## システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                    ディレクターエージェント                        │
│              (MiMo-V2.5-Pro — フラッグシップ推論)                 │
│   リクエスト分析 → パイプライン選択 → 9サブエージェント調整       │
└──────────┬──────────────┬──────────────┬────────────────────────┘
           │              │              │
  ┌────────▼────────┐ ┌──▼──────────┐ ┌▼──────────────┐
  │  ゲーム         │ │  漫画       │ │  映画          │
  │  パイプライン   │ │ パイプライン│ │  パイプライン  │
  │  (12エンジン)   │ │(OCR+描画)   │ │  (STT+TTS)    │
  └─────────────────┘ └─────────────┘ └───────────────┘
```

### 10個のAIサブエージェント

| # | エージェント | MiMoモデル | 役割 |
|---|-------------|-----------|------|
| 1 | **ディレクター** | MiMo-V2.5-Pro | オーケストレーション、推論 |
| 2 | **ルーター** | MiMo-V2.5 | 入力分類 → ゲーム/漫画/映画 |
| 3 | **翻訳者** | MiMo-V2.5 | 多言語翻訳（中/日/韓/英 → ベトナム語） |
| 4 | **OCRエージェント** | MiMo-V2.5 | 画像テキスト認識 |
| 5 | **インペインティング** | MiMo-V2.5 | 原文削除、背景復元 |
| 6 | **レンダラー** | MiMo-V2.5 | 翻訳テキストの描画 |
| 7 | **STTエージェント** | MiMo-V2.5 | 音声認識 |
| 8 | **ボイスエージェント** | MiMo-V2.5-TTS | 基本TTS |
| 9 | **ボイスクローン** | MiMo-TTS-VoiceClone | キャラクター声のクローン |
| 10 | **QAエージェント** | MiMo-V2.5 | 翻訳品質評価 |

---

## Xiaomi MiMo統合

### 使用モデル（8/8）

| モデル | 用途 | 月間Credits見込み |
|--------|------|-----------------|
| **MiMo-V2.5-Pro** | ディレクター — 複雑な推論 | ~5000万 |
| **MiMo-V2.5** | 翻訳、OCR、QA、ルーティング | ~2億 |
| **MiMo-V2.5-TTS** | ボイスエージェント | ~3000万 |
| **MiMo-TTS-VoiceClone** | 声のクローン | ~1000万 |
| **MiMo-TTS-VoiceDesign** | 新しい声の作成 | ~500万 |
| **合計** | | **~2.95億/月** |

---

## クイックスタート

```bash
git clone https://github.com/YOUR_USERNAME/universal-translation-hub.git
cd universal-translation-hub
pip install -r requirements.txt
cp .env.example .env
# .envを編集: MIMO_API_KEY=your_key_here
python main.py
```

---

## ロードマップ

| フェーズ | 期間 | フォーカス |
|---------|------|-----------|
| Phase 1 | 月1-2 | 基盤構築、MiMo API統合 |
| Phase 2 | 月3-4 | パイプライン統合 |
| Phase 3 | 月5-6 | ボイス＆品質（TTS、QA） |
| Phase 4 | 月7-8 | 仕上げ＆リリースv1.0 |

---

## 著者

**Đoàn Minh Trí** — DTHU大学

---

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) をご覧ください。

---

<div align="center">

**Xiaomi MiMo V2.5 搭載 | ベトナムのゲーム＆アニメコミュニティのために ❤️ で構築**

</div>
