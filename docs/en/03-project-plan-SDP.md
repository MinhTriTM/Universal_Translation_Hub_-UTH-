# Software Development Plan (SDP)
## Software Development Plan — Universal Translation Hub (UTH)

**Version:** 1.0
**Date:** 2026-05-22
**Author:** Doan Minh Tri
**Reference Standard:** IEEE 1058-1998

---

## 1. Project Overview

| Information | Details |
|-------------|---------|
| **Project Name** | Universal Translation Hub (UTH) |
| **Objective** | Multi-agent AI system for translating games, manga, and films into Vietnamese |
| **AI Platform** | Xiaomi MiMo V2.5 (8 models) |
| **Language** | Python 3.12 |
| **Duration** | 8 months (May 2026 — Dec 2026) |
| **Author** | Doan Minh Tri (DTHU University) |

---

## 2. Overall Roadmap

```
2026
Month:  5    6    7    8    9    10   11   12
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

## 3. Phase Details

### Phase 1: Foundation (May-Jun 2026) — 8 weeks

**Objective:** Establish the foundation, integrate MiMo API, create the Director Agent.

| # | Task | Duration | Deliverable | Priority |
|---|------|----------|-------------|----------|
| 1.1 | Setup project structure | 1 week | Directory structure, README, .env | P0 |
| 1.2 | MiMo API Client | 1 week | mimo_client.py (chat, tts, voice_clone) | P0 |
| 1.3 | BaseAgent framework | 1 week | base.py, AgentTask, AgentResult | P0 |
| 1.4 | Director Agent | 1.5 weeks | director.py (routing, coordination) | P0 |
| 1.5 | Router Agent | 1 week | router.py (detect game/manga/film) | P0 |
| 1.6 | Translation Memory | 1 week | memory.py (SQLite, CRUD, fuzzy search) | P0 |
| 1.7 | Translator Agent | 1 week | translator.py (MiMo-V2.5 translation) | P0 |
| 1.8 | Unit tests for Phase 1 | 0.5 weeks | tests/test_agents.py, test_memory.py | P1 |

**Milestone:** Director + Router + Translator operational, capable of translating text via MiMo API.

---

### Phase 2: Pipeline Integration (Jul-Aug 2026) — 8 weeks

**Objective:** Integrate 3 pipelines from existing projects.

| # | Task | Duration | Deliverable | Priority |
|---|------|----------|-------------|----------|
| 2.1 | Game Pipeline — Engine Detector | 1 week | game/detector.py (12 engines) | P0 |
| 2.2 | Game Pipeline — Text Extractor | 1.5 weeks | game/extractor.py | P0 |
| 2.3 | Game Pipeline — Text Injector | 1.5 weeks | game/injector.py | P0 |
| 2.4 | Manga Pipeline — Text Detector | 1 week | manga/detector.py | P0 |
| 2.5 | Manga Pipeline — OCR Agent | 1 week | manga/ocr.py | P0 |
| 2.6 | Manga Pipeline — Inpainting | 1 week | manga/inpaint.py | P0 |
| 2.7 | Manga Pipeline — Renderer | 0.5 weeks | manga/render.py | P0 |
| 2.8 | Film Pipeline — Subtitle OCR | 1 week | film/subtitle_ocr.py | P0 |
| 2.9 | Film Pipeline — STT Agent | 1 week | film/stt.py | P1 |
| 2.10 | Integration tests | 1 week | tests/test_pipelines.py | P1 |

**Milestone:** 3 pipelines operating independently, Director coordinating them.

---

### Phase 3: Voice & Quality (Sep-Oct 2026) — 8 weeks

**Objective:** Integrate MiMo TTS, QA Agent, Glossary.

| # | Task | Duration | Deliverable | Priority |
|---|------|----------|-------------|----------|
| 3.1 | Voice Agent — MiMo TTS | 1.5 weeks | voice_agent.py (basic TTS) | P0 |
| 3.2 | Voice Clone Agent | 1.5 weeks | voice_clone.py | P1 |
| 3.3 | Voice Design Agent | 1 week | voice_design.py | P2 |
| 3.4 | Audio Sync Agent | 1.5 weeks | audio_sync.py (FFmpeg mixing) | P0 |
| 3.5 | Volume Ducking | 0.5 weeks | volume_duck.py | P1 |
| 3.6 | QA Agent | 1.5 weeks | qa_agent.py (scoring, error detection) | P1 |
| 3.7 | Glossary Manager | 1 week | glossary.py (CRUD, import/export) | P1 |
| 3.8 | VLC Integration | 1 week | vlc_controller.py | P2 |

**Milestone:** Voice and quality assurance features complete.

---

### Phase 4: Polish & Release (Nov 2026) — 4 weeks

**Objective:** Finalize, test, document, and release.

| # | Task | Duration | Deliverable | Priority |
|---|------|----------|-------------|----------|
| 4.1 | Web Dashboard | 1.5 weeks | web/index.html, dashboard API | P1 |
| 4.2 | CLI polish | 0.5 weeks | main.py (help, progress bar) | P0 |
| 4.3 | Error handling | 0.5 weeks | Retry logic, graceful degradation | P0 |
| 4.4 | Documentation | 1 week | API docs, user guide, examples | P0 |
| 4.5 | Performance optimization | 0.5 weeks | Caching, batch processing | P1 |
| 4.6 | Release v1.0 | 0.5 weeks | GitHub release, demo video | P0 |

**Milestone:** Release v1.0 — complete product.

---

### Phase 5: Scale & Optimize (Dec 2026) — 4 weeks

**Objective:** Expand, optimize, and build the community.

| # | Task | Duration | Deliverable | Priority |
|---|------|----------|-------------|----------|
| 5.1 | Add new languages | 1 week | Support for English, Korean, Thai | P1 |
| 5.2 | Add new game engines | 1 week | Godot, Unreal support | P2 |
| 5.3 | Performance benchmarking | 1 week | Benchmark report | P1 |
| 5.4 | Community & Feedback | 1 week | GitHub Issues, Discussions | P1 |

---

## 4. MiMo Credits Allocation

| Phase | Period | Estimated Credits | Notes |
|-------|--------|-------------------|-------|
| Phase 1 | May-Jun 2026 | ~150M | Development + testing |
| Phase 2 | Jul-Aug 2026 | ~300M | Pipeline integration heavy |
| Phase 3 | Sep-Oct 2026 | ~250M | TTS + QA testing |
| Phase 4 | Nov 2026 | ~100M | Polish + demo |
| Phase 5 | Dec 2026 | ~100M | Scale testing |
| **Total** | **8 months** | **~900M** | **56% of Max plan (1.6B)** |

---

## 5. Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MiMo API downtime | Low | High | Fallback to OpenAI/DeepSeek |
| Insufficient GPU for local processing | Medium | Medium | Cloud GPU (Google Colab Pro) |
| Game engine format changes | Low | Medium | Modular extractor pattern |
| Low translation quality | Medium | High | QA Agent + human review |
| Scope creep | High | Medium | Strict phase gates |

---

## 6. Quality Assurance

### 6.1 Testing Strategy

| Test Type | Target Coverage | Tool |
|-----------|----------------|------|
| Unit tests | 80% | pytest |
| Integration tests | 60% | pytest + httpx |
| E2E tests | 40% | Manual + scripts |
| Performance tests | Key paths | locust |

### 6.2 Code Review
- Self-review via Claude Code / Gemini CLI
- Pre-commit hooks (ruff, mypy)

---

## 7. Configuration Management

| Tool | Purpose |
|------|---------|
| Git | Source code version control |
| GitHub | Repository hosting, Issues, Actions |
| .env | API keys, secrets |
| pyproject.toml | Python project config |
| requirements.txt | Dependencies |
