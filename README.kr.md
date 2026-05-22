<div align="center">

# Universal Translation Hub (UTH)

### 범용 멀티미디어 번역 시스템

**Xiaomi MiMo V2.5 기반 — 멀티 에이전트 아키텍처**

![MiMo](https://img.shields.io/badge/Xiaomi_MiMo-V2.5_Pro-orange)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)
![Agents](https://img.shields.io/badge/AI에이전트-10-purple)
![Languages](https://img.shields.io/badge/지원언어-6-red)

[Tiếng Việt](README.vn.md) | [English](README.en.md) | [中文](README.cn.md) | [Русский](README.ru.md) | [日本語](README.jp.md)

</div>

---

## 개요

**Universal Translation Hub (UTH)**는 **3가지 유형의 멀티미디어 콘텐츠**를 자동 번역하는 멀티 에이전트 AI 시스템입니다:

| 파이프라인 | 입력 | 출력 |
|-----------|------|------|
| **게임 번역** | 게임 파일 (12개 엔진: RPG Maker, Unity, Ren'Py, Kirikiri 등) | 완전 베트남어 현지화된 게임 |
| **만화 번역** | 만화 이미지 (JPG, PNG, PDF) | 텍스트가 렌더링된 번역 이미지 |
| **영화 더빙** | 영상 + 자막 (MKV, MP4, ASS, SRT) | AI 베트남어 더빙이 포함된 영상 |

### 이 프로젝트가 필요한 이유

> **문제:** 일본, 중국, 한국의 수백만 게임, 만화, 영화가 베트남어 번역이 없습니다. 수동 번역은 몇 달이 걸리고 비용이 많이 들며 확장할 수 없습니다.

> **해결:** UTH는 **10개의 AI 서브 에이전트**가 자동으로 협력하며, **Xiaomi MiMo V2.5**를 기반으로 모든 멀티미디어 콘텐츠를 몇 분 안에 베트남어로 번역합니다.

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    디렉터 에이전트                                │
│              (MiMo-V2.5-Pro — 플래그십 추론 모델)                │
│   요청 분석 → 파이프라인 선택 → 9개 서브 에이전트 조율          │
└──────────┬──────────────┬──────────────┬────────────────────────┘
           │              │              │
  ┌────────▼────────┐ ┌──▼──────────┐ ┌▼──────────────┐
  │  게임           │ │  만화       │ │  영화          │
  │  파이프라인     │ │ 파이프라인  │ │  파이프라인    │
  │  (12개 엔진)    │ │(OCR+렌더링) │ │  (STT+TTS)    │
  └─────────────────┘ └─────────────┘ └───────────────┘
```

### 10개의 AI 서브 에이전트

| # | 에이전트 | MiMo 모델 | 역할 |
|---|---------|----------|------|
| 1 | **디렉터** | MiMo-V2.5-Pro | 오케스트레이션, 추론 |
| 2 | **라우터** | MiMo-V2.5 | 입력 분류 → 게임/만화/영화 |
| 3 | **번역기** | MiMo-V2.5 | 다국어 번역 (중/일/한/영 → 베트남어) |
| 4 | **OCR 에이전트** | MiMo-V2.5 | 이미지 텍스트 인식 |
| 5 | **인페인팅** | MiMo-V2.5 | 원본 텍스트 제거, 배경 복원 |
| 6 | **렌더러** | MiMo-V2.5 | 번역 텍스트 렌더링 |
| 7 | **STT 에이전트** | MiMo-V2.5 | 음성 인식 |
| 8 | **보이스 에이전트** | MiMo-V2.5-TTS | 기본 TTS |
| 9 | **보이스 클론** | MiMo-TTS-VoiceClone | 캐릭터 음성 클론 |
| 10 | **QA 에이전트** | MiMo-V2.5 | 번역 품질 평가 |

---

## Xiaomi MiMo 통합

### 사용 모델 (8/8)

| 모델 | 사용 용도 | 월간 Credits 추정 |
|------|---------|-----------------|
| **MiMo-V2.5-Pro** | 디렉터 — 복잡한 추론 | ~5천만 |
| **MiMo-V2.5** | 번역, OCR, QA, 라우팅 | ~2억 |
| **MiMo-V2.5-TTS** | 보이스 에이전트 | ~3천만 |
| **MiMo-TTS-VoiceClone** | 음성 클론 | ~1천만 |
| **MiMo-TTS-VoiceDesign** | 새 음성 생성 | ~5백만 |
| **합계** | | **~2.95억/월** |

---

## 빠른 시작

```bash
git clone https://github.com/YOUR_USERNAME/universal-translation-hub.git
cd universal-translation-hub
pip install -r requirements.txt
cp .env.example .env
# .env 편집: MIMO_API_KEY=your_key_here
python main.py
```

---

## 로드맵

| 단계 | 기간 | 초점 |
|------|------|------|
| Phase 1 | 1-2개월 | 기반 구축, MiMo API 통합 |
| Phase 2 | 3-4개월 | 파이프라인 통합 |
| Phase 3 | 5-6개월 | 음성 & 품질 (TTS, QA) |
| Phase 4 | 7-8개월 | 다듬기 & 릴리스 v1.0 |

---

## 저자

**Đoàn Minh Trí** — DTHU 대학교

---

## 라이선스

MIT License — 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

---

<div align="center">

**Xiaomi MiMo V2.5 기반 | 베트남 게임 & 애니메이션 커뮤니티를 위해 ❤️ 로 제작**

</div>
