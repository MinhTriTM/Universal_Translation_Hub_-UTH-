# Software Development Plan (SDP)
## 소프트웨어 개발 계획 — Universal Translation Hub (UTH)

**버전:** 1.0
**날짜:** 2026-05-22
**저자:** Đoàn Minh Trí
**참고 표준:** IEEE 1058-1998

---

## 1. 프로젝트 개요

| 정보 | 상세 |
|------|------|
| **프로젝트명** | Universal Translation Hub (UTH) |
| **목표** | 게임, 만화, 영화를 베트남어로 번역하는 AI 다중 에이전트 시스템 |
| **AI 플랫폼** | Xiaomi MiMo V2.5 (8개 모델) |
| **언어** | Python 3.12 |
| **기간** | 8개월 (2026년 5월 — 2026년 12월) |
| **수행자** | Đoàn Minh Trí (DTHU University) |

---

## 2. 전체 로드맵 (Roadmap)

```
2026
월:   5    6    7    8    9    10   11   12
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

## 3. 단계별 상세 계획

### Phase 1: Foundation (2026년 5-6월) — 8주

**목표:** 기반 구축, MiMo API 통합, Director Agent 생성.

| # | 태스크 | 기간 | 산출물 | 우선순위 |
|---|--------|------|--------|----------|
| 1.1 | 프로젝트 구조 설정 | 1주 | 디렉토리 구조, README, .env | P0 |
| 1.2 | MiMo API 클라이언트 | 1주 | mimo_client.py (chat, tts, voice_clone) | P0 |
| 1.3 | BaseAgent 프레임워크 | 1주 | base.py, AgentTask, AgentResult | P0 |
| 1.4 | Director Agent | 1.5주 | director.py (라우팅, 조율) | P0 |
| 1.5 | Router Agent | 1주 | router.py (게임/만화/영화 감지) | P0 |
| 1.6 | Translation Memory | 1주 | memory.py (SQLite, CRUD, 퍼지 검색) | P0 |
| 1.7 | Translator Agent | 1주 | translator.py (MiMo-V2.5 번역) | P0 |
| 1.8 | Phase 1 단위 테스트 | 0.5주 | tests/test_agents.py, test_memory.py | P1 |

**마일스톤:** Director + Router + Translator가 작동하고, MiMo API를 통해 텍스트 번역 가능.

---

### Phase 2: Pipeline Integration (2026년 7-8월) — 8주

**목표:** 기존 프로젝트에서 3개 파이프라인 통합.

| # | 태스크 | 기간 | 산출물 | 우선순위 |
|---|--------|------|--------|----------|
| 2.1 | Game Pipeline — 엔진 감지기 | 1주 | game/detector.py (12개 엔진) | P0 |
| 2.2 | Game Pipeline — 텍스트 추출기 | 1.5주 | game/extractor.py | P0 |
| 2.3 | Game Pipeline — 텍스트 주입기 | 1.5주 | game/injector.py | P0 |
| 2.4 | Manga Pipeline — 텍스트 감지기 | 1주 | manga/detector.py | P0 |
| 2.5 | Manga Pipeline — OCR 에이전트 | 1주 | manga/ocr.py | P0 |
| 2.6 | Manga Pipeline — 인페인팅 | 1주 | manga/inpaint.py | P0 |
| 2.7 | Manga Pipeline — 렌더러 | 0.5주 | manga/render.py | P0 |
| 2.8 | Film Pipeline — 자막 OCR | 1주 | film/subtitle_ocr.py | P0 |
| 2.9 | Film Pipeline — STT 에이전트 | 1주 | film/stt.py | P1 |
| 2.10 | 통합 테스트 | 1주 | tests/test_pipelines.py | P1 |

**마일스톤:** 3개 파이프라인이 독립적으로 작동하고, Director가 조율 가능.

---

### Phase 3: Voice & Quality (2026년 9-10월) — 8주

**목표:** MiMo TTS 통합, QA Agent, Glossary 구현.

| # | 태스크 | 기간 | 산출물 | 우선순위 |
|---|--------|------|--------|----------|
| 3.1 | Voice Agent — MiMo TTS | 1.5주 | voice_agent.py (기본 TTS) | P0 |
| 3.2 | Voice Clone Agent | 1.5주 | voice_clone.py | P1 |
| 3.3 | Voice Design Agent | 1주 | voice_design.py | P2 |
| 3.4 | Audio Sync Agent | 1.5주 | audio_sync.py (FFmpeg 믹싱) | P0 |
| 3.5 | Volume Ducking | 0.5주 | volume_duck.py | P1 |
| 3.6 | QA Agent | 1.5주 | qa_agent.py (점수화, 오류 감지) | P1 |
| 3.7 | Glossary Manager | 1주 | glossary.py (CRUD, 가져오기/내보내기) | P1 |
| 3.8 | VLC 통합 | 1주 | vlc_controller.py | P2 |

**마일스톤:** 음성 + 품질 보증 기능 완성.

---

### Phase 4: Polish & Release (2026년 11월) — 4주

**목표:** 완성, 테스트, 문서화, 릴리스.

| # | 태스크 | 기간 | 산출물 | 우선순위 |
|---|--------|------|--------|----------|
| 4.1 | 웹 대시보드 | 1.5주 | web/index.html, dashboard API | P1 |
| 4.2 | CLI 개선 | 0.5주 | main.py (도움말, 진행 표시줄) | P0 |
| 4.3 | 오류 처리 | 0.5주 | 재시도 로직, 우아한 성능 저하 | P0 |
| 4.4 | 문서화 | 1주 | API 문서, 사용자 가이드, 예제 | P0 |
| 4.5 | 성능 최적화 | 0.5주 | 캐싱, 배치 처리 | P1 |
| 4.6 | v1.0 릴리스 | 0.5주 | GitHub 릴리스, 데모 비디오 | P0 |

**마일스톤:** v1.0 릴리스 — 완성된 제품.

---

### Phase 5: Scale & Optimize (2026년 12월) — 4주

**목표:** 확장, 최적화, 커뮤니티 구축.

| # | 태스크 | 기간 | 산출물 | 우선순위 |
|---|--------|------|--------|----------|
| 5.1 | 새 언어 추가 | 1주 | 영어, 한국어, 태국어 추가 지원 | P1 |
| 5.2 | 새 게임 엔진 추가 | 1주 | Godot, Unreal 지원 | P2 |
| 5.3 | 성능 벤치마킹 | 1주 | 벤치마크 보고서 | P1 |
| 5.4 | 커뮤니티 및 피드백 | 1주 | GitHub Issues, Discussions | P1 |

---

## 4. MiMo 크레딧 할당

| 단계 | 기간 | 예상 크레딧 | 비고 |
|------|------|-------------|------|
| Phase 1 | 5-6월/2026 | ~150M | 개발 + 테스트 |
| Phase 2 | 7-8월/2026 | ~300M | 파이프라인 통합 집중 |
| Phase 3 | 9-10월/2026 | ~250M | TTS + QA 테스트 |
| Phase 4 | 11월/2026 | ~100M | 개선 + 데모 |
| Phase 5 | 12월/2026 | ~100M | 확장 테스트 |
| **합계** | **8개월** | **~900M** | **Max 패키지의 56% (1.6B)** |

---

## 5. 위험 관리

| 위험 | 확률 | 영향 | 완화 방안 |
|------|------|------|-----------|
| MiMo API 다운타임 | 낮음 | 높음 | OpenAI/DeepSeek로 폴백 |
| 로컬 처리를 위한 GPU 부족 | 중간 | 중간 | 클라우드 GPU (Google Colab Pro) |
| 게임 엔진 포맷 변경 | 낮음 | 중간 | 모듈형 추출기 패턴 |
| 번역 품질 저하 | 중간 | 높음 | QA Agent + 수동 검토 |
| 범위 확대 | 높음 | 중간 | 엄격한 단계 게이트 |

---

## 6. 품질 보증

### 6.1 테스트 전략

| 테스트 유형 | 목표 커버리지 | 도구 |
|-------------|---------------|------|
| 단위 테스트 | 80% | pytest |
| 통합 테스트 | 60% | pytest + httpx |
| E2E 테스트 | 40% | 수동 + 스크립트 |
| 성능 테스트 | 주요 경로 | locust |

### 6.2 코드 리뷰
- Claude Code / Gemini CLI를 통한 셀프 리뷰
- 프리-commit 훅 (ruff, mypy)

---

## 7. 형상 관리

| 도구 | 용도 |
|------|------|
| Git | 소스 코드 버전 관리 |
| GitHub | 저장소 호스팅, Issues, Actions |
| .env | API 키, 시크릿 |
| pyproject.toml | Python 프로젝트 설정 |
| requirements.txt | 의존성 |
