# Software Development Plan (SDP)
## Kế Hoạch Phát Triển Phần Mềm — Universal Translation Hub (UTH)

**Phiên bản:** 1.0
**Ngày:** 2026-05-22
**Tác giả:** Đoàn Minh Trí
**Chuẩn tham khảo:** IEEE 1058-1998

---

## 1. Tổng Quan Dự Án

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên dự án** | Universal Translation Hub (UTH) |
| **Mục tiêu** | Hệ thống AI đa tác nhân dịch game, manga, film sang tiếng Việt |
| **AI Platform** | Xiaomi MiMo V2.5 (8 models) |
| **Ngôn ngữ** | Python 3.12 |
| **Thời gian** | 8 tháng (T5/2026 — T12/2026) |
| **Người thực hiện** | Đoàn Minh Trí (DTHU University) |

---

## 2. Lộ Trình Tổng Thể (Roadmap)

```
2026
Tháng:  5    6    7    8    9    10   11   12
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

## 3. Chi Tiết Từng Phase

### Phase 1: Foundation (Tháng 5-6/2026) — 8 tuần

**Mục tiêu:** Thiết lập nền tảng, tích hợp MiMo API, tạo Director Agent.

| # | Task | Duration | Deliverable | Ưu tiên |
|---|------|----------|-------------|---------|
| 1.1 | Setup project structure | 1 tuần | Cấu trúc thư mục, README, .env | P0 |
| 1.2 | MiMo API Client | 1 tuần | mimo_client.py (chat, tts, voice_clone) | P0 |
| 1.3 | BaseAgent framework | 1 tuần | base.py, AgentTask, AgentResult | P0 |
| 1.4 | Director Agent | 1.5 tuần | director.py (routing, coordination) | P0 |
| 1.5 | Router Agent | 1 tuần | router.py (detect game/manga/film) | P0 |
| 1.6 | Translation Memory | 1 tuần | memory.py (SQLite, CRUD, fuzzy search) | P0 |
| 1.7 | Translator Agent | 1 tuần | translator.py (MiMo-V2.5 translation) | P0 |
| 1.8 | Unit tests cho Phase 1 | 0.5 tuần | tests/test_agents.py, test_memory.py | P1 |

**Milestone:** Director + Router + Translator hoạt động, có thể dịch text qua MiMo API.

---

### Phase 2: Pipeline Integration (Tháng 7-8/2026) — 8 tuần

**Mục tiêu:** Tích hợp 3 pipelines từ dự án hiện có.

| # | Task | Duration | Deliverable | Ưu tiên |
|---|------|----------|-------------|---------|
| 2.1 | Game Pipeline — Engine Detector | 1 tuần | game/detector.py (12 engines) | P0 |
| 2.2 | Game Pipeline — Text Extractor | 1.5 tuần | game/extractor.py | P0 |
| 2.3 | Game Pipeline — Text Injector | 1.5 tuần | game/injector.py | P0 |
| 2.4 | Manga Pipeline — Text Detector | 1 tuần | manga/detector.py | P0 |
| 2.5 | Manga Pipeline — OCR Agent | 1 tuần | manga/ocr.py | P0 |
| 2.6 | Manga Pipeline — Inpainting | 1 tuần | manga/inpaint.py | P0 |
| 2.7 | Manga Pipeline — Renderer | 0.5 tuần | manga/render.py | P0 |
| 2.8 | Film Pipeline — Subtitle OCR | 1 tuần | film/subtitle_ocr.py | P0 |
| 2.9 | Film Pipeline — STT Agent | 1 tuần | film/stt.py | P1 |
| 2.10 | Integration tests | 1 tuần | tests/test_pipelines.py | P1 |

**Milestone:** 3 pipelines hoạt động độc lập, Director điều phối được.

---

### Phase 3: Voice & Quality (Tháng 9-10/2026) — 8 tuần

**Mục tiêu:** Tích hợp MiMo TTS, QA Agent, Glossary.

| # | Task | Duration | Deliverable | Ưu tiên |
|---|------|----------|-------------|---------|
| 3.1 | Voice Agent — MiMo TTS | 1.5 tuần | voice_agent.py (basic TTS) | P0 |
| 3.2 | Voice Clone Agent | 1.5 tuần | voice_clone.py | P1 |
| 3.3 | Voice Design Agent | 1 tuần | voice_design.py | P2 |
| 3.4 | Audio Sync Agent | 1.5 tuần | audio_sync.py (FFmpeg mixing) | P0 |
| 3.5 | Volume Ducking | 0.5 tuần | volume_duck.py | P1 |
| 3.6 | QA Agent | 1.5 tuần | qa_agent.py (scoring, error detection) | P1 |
| 3.7 | Glossary Manager | 1 tuần | glossary.py (CRUD, import/export) | P1 |
| 3.8 | VLC Integration | 1 tuần | vlc_controller.py | P2 |

**Milestone:** Hoàn chỉnh tính năng voice + quality assurance.

---

### Phase 4: Polish & Release (Tháng 11/2026) — 4 tuần

**Mục tiêu:** Hoàn thiện, test, documentation, release.

| # | Task | Duration | Deliverable | Ưu tiên |
|---|------|----------|-------------|---------|
| 4.1 | Web Dashboard | 1.5 tuần | web/index.html, dashboard API | P1 |
| 4.2 | CLI polish | 0.5 tuần | main.py (help, progress bar) | P0 |
| 4.3 | Error handling | 0.5 tuần | Retry logic, graceful degradation | P0 |
| 4.4 | Documentation | 1 tuần | API docs, user guide, examples | P0 |
| 4.5 | Performance optimization | 0.5 tuần | Caching, batch processing | P1 |
| 4.6 | Release v1.0 | 0.5 tuần | GitHub release, demo video | P0 |

**Milestone:** Release v1.0 — sản phẩm hoàn chỉnh.

---

### Phase 5: Scale & Optimize (Tháng 12/2026) — 4 tuần

**Mục tiêu:** Mở rộng, tối ưu, community building.

| # | Task | Duration | Deliverable | Ưu tiên |
|---|------|----------|-------------|---------|
| 5.1 | Thêm ngôn ngữ mới | 1 tuần | Support thêm tiếng Anh, Hàn, Thái | P1 |
| 5.2 | Thêm game engine mới | 1 tuần | Godot, Unreal support | P2 |
| 5.3 | Performance benchmarking | 1 tuần | Benchmark report | P1 |
| 5.4 | Community & Feedback | 1 tuần | GitHub Issues, Discussions | P1 |

---

## 4. Phân Bổ MiMo Credits

| Phase | Thời gian | Credits ước tính | Ghi chú |
|-------|-----------|-----------------|---------|
| Phase 1 | T5-6/2026 | ~150M | Development + testing |
| Phase 2 | T7-8/2026 | ~300M | Pipeline integration heavy |
| Phase 3 | T9-10/2026 | ~250M | TTS + QA testing |
| Phase 4 | T11/2026 | ~100M | Polish + demo |
| Phase 5 | T12/2026 | ~100M | Scale testing |
| **Tổng** | **8 tháng** | **~900M** | **56% gói Max (1.6B)** |

---

## 5. Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| MiMo API downtime | Low | High | Fallback to OpenAI/DeepSeek |
| GPU不够 cho local processing | Medium | Medium | Cloud GPU (Google Colab Pro) |
| Game engine format thay đổi | Low | Medium | Modular extractor pattern |
| Translation quality thấp | Medium | High | QA Agent + human review |
| Scope creep | High | Medium | Strict phase gates |

---

## 6. Quality Assurance

### 6.1 Testing Strategy

| Loại test | Coverage mục tiêu | Tool |
|-----------|-------------------|------|
| Unit tests | 80% | pytest |
| Integration tests | 60% | pytest + httpx |
| E2E tests | 40% | Manual + scripts |
| Performance tests | Key paths | locust |

### 6.2 Code Review
- Tự review qua Claude Code / Gemini CLI
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
