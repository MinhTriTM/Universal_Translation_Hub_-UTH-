# Software Requirements Specification (SRS)
## 소프트웨어 요구사항 명세서 — Universal Translation Hub (UTH)

**버전:** 1.0
**날짜:** 2026-05-22
**저자:** Đoàn Minh Trí
**참고 표준:** IEEE 830-1998

---

## 1. 소개

### 1.1 목적
이 문서는 **Universal Translation Hub (UTH)** 프로젝트의 소프트웨어 요구사항을 명세합니다. UTH는 게임, 만화, 영화를 위한 범용 AI 다중 에이전트 번역 시스템입니다.

### 1.2 범위
UTH는 3가지 유형의 콘텐츠에 대한 자동 번역을 지원합니다:
- **게임**: 12개 게임 엔진 (RPG Maker, Unity, Ren'Py, Kirikiri, CatSystem2, NScripter, TyranoBuilder, Web/HTML5, NW.js, Wolf RPG, Binary)
- **만화/코믹**: OCR → 번역 → 인페인팅 → 렌더링
- **영화/비디오**: STT → 번역 → TTS → 오디오 동기화

### 1.3 정의 및 용어

| 용어 | 정의 |
|------|------|
| Agent | 특정 목표를 가진 자동 AI 에이전트 |
| Pipeline | 순차적이거나 병렬적인 처리 체인 |
| TTS | Text-to-Speech (음성 합성) |
| STT | Speech-to-Text (음성 인식) |
| OCR | Optical Character Recognition (광학 문자 인식) |
| Inpainting | 원본 텍스트를 제거하고 이미지 배경을 복원 |
| Translation Memory | 기존 번역을 저장하는 데이터베이스 |
| Glossary | 통일된 용어표 |

### 1.4 참고 문헌
- IEEE 830-1998: Software Requirements Specification
- IEEE 1471-2000: Software Architecture Documentation
- Xiaomi MiMo V2.5 API Documentation
- DichGame Project Documentation
- manga-image-translator Documentation
- MIMO-AXON Project Documentation

---

## 2. 개요

### 2.1 시스템 전망
UTH는 클라이언트-서버 시스템으로, 사용자 PC에서 실행되며 AI 처리를 위해 Xiaomi MiMo API에 연결합니다. 시스템은 Director Agent에 의해 조율되는 3개의 병렬 파이프라인을 갖습니다.

### 2.2 주요 기능
1. **FR-01**: 입력 콘텐츠 유형 자동 인식 (게임/만화/영화)
2. **FR-02**: 게임 파일에서 텍스트 추출 (12개 엔진)
3. **FR-03**: 만화/코믹 이미지에서 OCR 텍스트 추출
4. **FR-04**: 오디오/비디오에서 STT
5. **FR-05**: 다국어 텍스트 → 베트남어 번역
6. **FR-06**: 인페인팅 (이미지에서 원본 텍스트 제거)
7. **FR-07**: 번역 텍스트를 이미지에 렌더링
8. **FR-08**: TTS — 베트남어 음성 생성
9. **FR-09**: 음성 클론 — 캐릭터 음성 복제
10. **FR-10**: 오디오와 비디오 동기화
11. **FR-11**: Translation Memory — 번역 캐싱
12. **FR-12**: Glossary Manager — 용어 관리
13. **FR-13**: 자동 QA — 번역 품질 평가
14. **FR-14**: Unified Dashboard — 모든 파이프라인 모니터링

### 2.3 사용자 특성

| 사용자 유형 | 설명 |
|-------------|------|
| 게이머 | 중국/일본 게임을 베트남어로 현지화하고 싶어함, 코딩 불필요 |
| 만화 독자 | 고품질 베트남어 만화를 읽고 싶어함 |
| 영화 시청자 | 중국/일본 영화를 베트남어 더빙으로 시청하고 싶어함 |
| 개발자 | UTH를 자신의 워크플로우에 통합하고 싶어함 |

### 2.4 제약 조건
- Windows 10/11 (기본), Linux (보조)에서 실행
- 로컬 처리를 위해 NVIDIA GPU (CUDA) 필요
- MiMo API 호출을 위해 인터넷 필요
- Python 3.10+

### 2.5 가정 및 의존성
- Xiaomi MiMo API가 항상 사용 가능 (99.9% 가동률)
- 사용자가 CUDA를 지원하는 NVIDIA GPU를 보유
- 게임/만화/비디오 파일이 DRM/저작권 보호가 되어 있지 않음

---

## 3. 기능 요구사항 (Functional Requirements)

### 3.1 Director Agent (FR-01)

**설명:** MiMo-V2.5-Pro를 사용하는 주요 에이전트로, 전체 시스템을 조율합니다.

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| FR-01.1 | 사용자로부터 입력 수신 (파일/폴더 경로) | P0 |
| FR-01.2 | 콘텐츠 유형 분류 (게임/만화/영화) | P0 |
| FR-01.3 | 적합한 파이프라인 선택 | P0 |
| FR-01.4 | 서브 에이전트를 올바른 순서로 조율 | P0 |
| FR-01.5 | 서브 에이전트 실패 시 오류 처리 및 재시도 | P1 |
| FR-01.6 | 실시간 진행 상황 보고 | P1 |

### 3.2 Game Pipeline (FR-02)

**설명:** 12개의 서로 다른 엔진에서 게임을 번역합니다.

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| FR-02.1 | 게임 엔진 자동 인식 (magic bytes, 파일 시그니처) | P0 |
| FR-02.2 | 게임 파일에서 텍스트 추출 | P0 |
| FR-02.3 | MiMo-V2.5를 통한 텍스트 번역 | P0 |
| FR-02.4 | 번역본을 게임 파일에 주입 | P0 |
| FR-02.5 | 베트남어 폰트 처리 (감지, 서브셋, 임베드) | P0 |
| FR-02.6 | 완성된 게임 재패키징 | P1 |
| FR-02.7 | 배치 처리 지원 (여러 게임 동시 처리) | P2 |

### 3.3 Manga Pipeline (FR-03, FR-06, FR-07)

**설명:** 스캔된 이미지에서 만화/코믹을 번역합니다.

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| FR-03.1 | 이미지 내 텍스트 버블 감지 | P0 |
| FR-03.2 | 이미지에서 OCR 텍스트 추출 | P0 |
| FR-03.3 | MiMo-V2.5를 통한 텍스트 번역 | P0 |
| FR-03.4 | 원본 텍스트 제거 (인페인팅) | P0 |
| FR-03.5 | 번역 텍스트를 이미지에 렌더링 | P0 |
| FR-03.6 | 26개 소스 언어 지원 | P1 |
| FR-03.7 | 배치 처리 (전체 챕터/볼륨) | P1 |

### 3.4 Film Pipeline (FR-04, FR-08, FR-09, FR-10)

**설명:** 영화/비디오를 자동으로 번역하고 더빙합니다.

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| FR-04.1 | 비디오에서 하드 자막 OCR | P0 |
| FR-04.2 | STT — 음성을 텍스트로 변환 | P0 |
| FR-04.3 | MiMo-V2.5를 통한 텍스트 번역 | P0 |
| FR-04.4 | TTS — 베트남어 음성 생성 | P0 |
| FR-04.5 | TTS 오디오를 원본 비디오와 동기화 | P0 |
| FR-04.6 | 볼륨 덕킹 (TTS 발화 시 영화 볼륨 감소) | P1 |
| FR-04.7 | 음성 클론 — 캐릭터 음성 복제 | P1 |
| FR-04.8 | VLC 통합 — 실시간 더빙 | P2 |

### 3.5 Shared Services (FR-11, FR-12, FR-13)

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| FR-11.1 | SQLite 데이터베이스에 번역 저장 | P0 |
| FR-11.2 | 기존 번역 검색 (퍼지 매칭) | P0 |
| FR-11.3 | 이전 번역 자동 재사용 | P0 |
| FR-12.1 | 용어 관리 (CRUD) | P1 |
| FR-12.2 | 번역 전 용어집 적용 | P1 |
| FR-12.3 | 용어집 내보내기/가져오기 (JSON, CSV) | P2 |
| FR-13.1 | 자동 번역 평가 (1-10점) | P1 |
| FR-13.2 | 번역 오류 감지 (잘못된 의미, 누락된 문장) | P1 |
| FR-13.3 | 번역 개선 제안 | P2 |

---

## 4. 비기능 요구사항 (Non-Functional Requirements)

### 4.1 성능 (Performance)

| ID | 요구사항 | 목표 값 |
|----|----------|---------|
| NFR-01 | 게임 텍스트 1문장 번역 시간 | < 2초 |
| NFR-02 | 만화 1페이지 처리 시간 | < 30초 |
| NFR-03 | 영화 1화(45분) 번역 시간 | < 30분 |
| NFR-04 | MiMo API 응답 시간 | < 5초 (P95) |
| NFR-05 | 동시 파이프라인 수 | 최소 3개 (병렬) |

### 4.2 신뢰성 (Reliability)

| ID | 요구사항 | 목표 값 |
|----|----------|---------|
| NFR-06 | 가동률 (인터넷 연결 시) | 99.5% |
| NFR-07 | API 실패 시 재시도 | 3회, 지수 백오프 |
| NFR-08 | 데이터 무결성 | 오류 시 원본 파일 손실 없음 |
| NFR-09 | Translation Memory 내구성 | SQLite WAL 모드 |

### 4.3 확장성 (Scalability)

| ID | 요구사항 |
|----|----------|
| NFR-10 | 코어 코드 수정 없이 새 게임 엔진 추가 가능 |
| NFR-11 | 번역기 수정 없이 새 언어 추가 가능 |
| NFR-12 | 파이프라인 수정 없이 새 AI 프로바이더 추가 가능 (OpenAI, DeepSeek...) |

### 4.4 보안 (Security)

| ID | 요구사항 |
|----|----------|
| NFR-13 | API 키는 .env에 저장, git에 커밋하지 않음 |
| NFR-14 | 게임/만화/비디오 파일을 클라우드에 업로드하지 않음 |
| NFR-15 | MiMo API 호출은 HTTPS 사용 |

### 4.5 사용성 (Usability)

| ID | 요구사항 |
|----|----------|
| NFR-16 | 개발자를 위한 CLI 인터페이스 |
| NFR-17 | 일반 사용자를 위한 웹 대시보드 |
| NFR-18 | 배치 처리를 위한 진행 표시줄 |
| NFR-19 | 베트남어로 된 이해하기 쉬운 오류 메시지 |

---

## 5. 시스템 인터페이스

### 5.1 Xiaomi MiMo API
- Endpoint: `https://api.mimo.xiaomi.com/v1/`
- Models: MiMo-V2.5-Pro, MiMo-V2.5, MiMo-V2.5-TTS, MiMo-TTS-VoiceClone, MiMo-TTS-VoiceDesign
- Auth: API Key (Bearer token)
- Format: OpenAI-compatible API

### 5.2 외부 도구
- **FFmpeg**: 비디오/오디오 처리
- **VLC**: 미디어 재생 + HTTP API
- **SQLite**: 로컬 데이터베이스
- **espeak-ng**: TTS용 음소화

---

## 6. 데이터 요구사항

### 6.1 Translation Memory 데이터베이스
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

### 6.2 Glossary 데이터베이스
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

## 7. 보조 문서
- [SAD.md](../SAD.md) — 시스템 아키텍처
- [SDP.md](../SDP.md) — 개발 계획
- [FEASIBILITY.md](../FEASIBILITY.md) — 타당성 조사
- [RESOURCES.md](../RESOURCES.md) — 자료 및 참고 문헌
