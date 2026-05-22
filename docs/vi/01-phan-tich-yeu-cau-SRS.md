# Software Requirements Specification (SRS)
## Đặc Tả Yêu Cầu Phần Mềm — Universal Translation Hub (UTH)

**Phiên bản:** 1.0
**Ngày:** 2026-05-22
**Tác giả:** Đoàn Minh Trí
**Chuẩn tham khảo:** IEEE 830-1998

---

## 1. Giới Thiệu

### 1.1 Mục đích
Tài liệu này đặc tả yêu cầu phần mềm cho dự án **Universal Translation Hub (UTH)** — hệ thống AI đa tác nhân dịch thuật phổ quát cho game, manga, và film.

### 1.2 Phạm vi
UTH hỗ trợ dịch thuật tự động cho 3 loại nội dung:
- **Game**: 12 game engines (RPG Maker, Unity, Ren'Py, Kirikiri, CatSystem2, NScripter, TyranoBuilder, Web/HTML5, NW.js, Wolf RPG, Binary)
- **Manga/Comic**: OCR → Dịch → Inpainting → Render
- **Film/Video**: STT → Dịch → TTS → Sync audio

### 1.3 Định nghĩa & Thuật ngữ

| Thuật ngữ | Định nghĩa |
|-----------|-----------|
| Agent | Tác nhân AI tự động, có mục tiêu cụ thể |
| Pipeline | Chuỗi xử lý tuần tự hoặc song song |
| TTS | Text-to-Speech (Tổng hợp giọng nói) |
| STT | Speech-to-Text (Nhận diện giọng nói) |
| OCR | Optical Character Recognition (Nhận dạng ký tự) |
| Inpainting | Xóa text gốc và khôi phục nền hình ảnh |
| Translation Memory | Cơ sở dữ liệu lưu trữ bản dịch đã có |
| Glossary | Bảng thuật ngữ thống nhất |

### 1.4 Tham khảo
- IEEE 830-1998: Software Requirements Specification
- IEEE 1471-2000: Software Architecture Documentation
- Xiaomi MiMo V2.5 API Documentation
- DichGame Project Documentation
- manga-image-translator Documentation
- MIMO-AXON Project Documentation

---

## 2. Mô Tả Tổng Quan

### 2.1 Triển vọng hệ thống
UTH là hệ thống client-server, chạy trên máy người dùng, kết nối Xiaomi MiMo API cho AI processing. Hệ thống có 3 pipelines song song, được điều phối bởi Director Agent.

### 2.2 Các chức năng chính
1. **FR-01**: Tự động nhận diện loại nội dung đầu vào (game/manga/film)
2. **FR-02**: Trích xuất text từ game files (12 engines)
3. **FR-03**: OCR text từ ảnh manga/comic
4. **FR-04**: STT từ audio/video
5. **FR-05**: Dịch text đa ngôn ngữ → tiếng Việt
6. **FR-06**: Inpainting (xóa text gốc khỏi ảnh)
7. **FR-07**: Render text dịch vào ảnh
8. **FR-08**: TTS — tạo giọng đọc tiếng Việt
9. **FR-09**: Voice clone — clone giọng nhân vật
10. **FR-10**: Đồng bộ audio với video
11. **FR-11**: Translation Memory — cache bản dịch
12. **FR-12**: Glossary Manager — quản lý thuật ngữ
13. **FR-13**: QA tự động — đánh giá chất lượng bản dịch
14. **FR-14**: Unified Dashboard — giám sát tất cả pipelines

### 2.3 Đặc điểm người dùng

| Loại người dùng | Mô tả |
|-----------------|-------|
| Gamer | Muốn Việt hóa game Trung/Nhật/Không cần biết code |
| Đọc giả manga | Muốn đọc manga tiếng Việt, chất lượng cao |
| Người xem phim | Muốn xem phim Trung/Nhật với thuyết minh tiếng Việt |
| Developer | Muốn tích hợp UTH vào workflow của họ |

### 2.4 Ràng buộc
- Chạy trên Windows 10/11 (primary), Linux (secondary)
- Cần GPU NVIDIA (CUDA) cho local processing
- Cần internet cho MiMo API calls
- Python 3.10+

### 2.5 Giả định và phụ thuộc
- Xiaomi MiMo API luôn sẵn sàng (99.9% uptime)
- Người dùng có GPU NVIDIA với CUDA support
- File game/manga/video không bị DRM/bảo vệ bản quyền

---

## 3. Yêu Cầu Chức Năng (Functional Requirements)

### 3.1 Director Agent (FR-01)

**Mô tả:** Agent chính, sử dụng MiMo-V2.5-Pro, điều phối toàn bộ hệ thống.

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-01.1 | Nhận input từ người dùng (đường dẫn file/thư mục) | P0 |
| FR-01.2 | Phân loại loại nội dung (game/manga/film) | P0 |
| FR-01.3 | Chọn pipeline phù hợp | P0 |
| FR-01.4 | Điều phối các sub-agents theo đúng thứ tự | P0 |
| FR-01.5 | Xử lý lỗi và retry khi sub-agent thất bại | P1 |
| FR-01.6 | Báo cáo tiến độ realtime | P1 |

### 3.2 Game Pipeline (FR-02)

**Mô tả:** Dịch game từ 12 engines khác nhau.

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-02.1 | Tự động nhận diện game engine (magic bytes, file signature) | P0 |
| FR-02.2 | Trích xuất text từ game files | P0 |
| FR-02.3 | Dịch text qua MiMo-V2.5 | P0 |
| FR-02.4 | Inject bản dịch ngược lại file game | P0 |
| FR-02.5 | Xử lý font tiếng Việt (detect, subset, embed) | P0 |
| FR-02.6 | Đóng gói lại game hoàn chỉnh | P1 |
| FR-02.7 | Hỗ trợ batch processing (nhiều game cùng lúc) | P2 |

### 3.3 Manga Pipeline (FR-03, FR-06, FR-07)

**Mô tả:** Dịch ảnh manga/comic từ ảnh scan.

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-03.1 | Phát hiện text bubbles trong ảnh | P0 |
| FR-03.2 | OCR text từ ảnh | P0 |
| FR-03.3 | Dịch text qua MiMo-V2.5 | P0 |
| FR-03.4 | Xóa text gốc (inpainting) | P0 |
| FR-03.5 | Render text dịch vào ảnh | P0 |
| FR-03.6 | Hỗ trợ 26 ngôn ngữ nguồn | P1 |
| FR-03.7 | Batch processing (cả chapter/volume) | P1 |

### 3.4 Film Pipeline (FR-04, FR-08, FR-09, FR-10)

**Mô tả:** Dịch và thuyết minh phim/video tự động.

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-04.1 | OCR phụ đề cứng từ video | P0 |
| FR-04.2 | STT — chuyển giọng nói thành text | P0 |
| FR-04.3 | Dịch text qua MiMo-V2.5 | P0 |
| FR-04.4 | TTS — tạo giọng đọc tiếng Việt | P0 |
| FR-04.5 | Đồng bộ audio TTS với video gốc | P0 |
| FR-04.6 | Volume ducking (giảm volume phim khi TTS nói) | P1 |
| FR-04.7 | Voice clone — clone giọng nhân vật | P1 |
| FR-04.8 | VLC integration — realtime dubbing | P2 |

### 3.5 Shared Services (FR-11, FR-12, FR-13)

| ID | Yêu cầu | Ưu tiên |
|----|---------|---------|
| FR-11.1 | Lưu bản dịch vào SQLite database | P0 |
| FR-11.2 | Tìm kiếm bản dịch đã có (fuzzy match) | P0 |
| FR-11.3 | Tự động dùng lại bản dịch cũ | P0 |
| FR-12.1 | Quản lý thuật ngữ (CRUD) | P1 |
| FR-12.2 | Áp dụng glossary trước khi dịch | P1 |
| FR-12.3 | Export/Import glossary (JSON, CSV) | P2 |
| FR-13.1 | Đánh giá bản dịch tự động (1-10 score) | P1 |
| FR-13.2 | Phát hiện lỗi dịch (sai nghĩa, thiếu câu) | P1 |
| FR-13.3 | Gợi ý cải thiện bản dịch | P2 |

---

## 4. Yêu Cầu Phi Chức Năng (Non-Functional Requirements)

### 4.1 Hiệu năng (Performance)

| ID | Yêu cầu | Giá trị mục tiêu |
|----|---------|-----------------|
| NFR-01 | Thời gian dịch 1 câu game text | < 2 giây |
| NFR-02 | Thời gian xử lý 1 trang manga | < 30 giây |
| NFR-03 | Thời gian dịch 1 tập phim (45min) | < 30 phút |
| NFR-04 | MiMo API response time | < 5 giây (P95) |
| NFR-05 | Concurrent pipelines | Tối thiểu 3 (song song) |

### 4.2 Độ tin cậy (Reliability)

| ID | Yêu cầu | Giá trị mục tiêu |
|----|---------|-----------------|
| NFR-06 | Uptime (khi có internet) | 99.5% |
| NFR-07 | Retry on API failure | 3 lần, exponential backoff |
| NFR-08 | Data integrity | Không mất file gốc khi lỗi |
| NFR-09 | Translation Memory durability | SQLite WAL mode |

### 4.3 Khả năng mở rộng (Scalability)

| ID | Yêu cầu |
|----|---------|
| NFR-10 | Thêm game engine mới mà không sửa code core |
| NFR-11 | Thêm ngôn ngữ mới mà không sửa translator |
| NFR-12 | Thêm AI provider mới (OpenAI, DeepSeek...) mà không sửa pipeline |

### 4.4 Bảo mật (Security)

| ID | Yêu cầu |
|----|---------|
| NFR-13 | API keys lưu trong .env, không commit vào git |
| NFR-14 | Không upload file game/manga/video lên cloud |
| NFR-15 | MiMo API calls qua HTTPS |

### 4.5 Khả năng sử dụng (Usability)

| ID | Yêu cầu |
|----|---------|
| NFR-16 | CLI interface cho developer |
| NFR-17 | Web Dashboard cho người dùng phổ thông |
| NFR-18 | Progress bar cho batch processing |
| NFR-19 | Error messages tiếng Việt, dễ hiểu |

---

## 5. Giao Diện Hệ Thống (System Interfaces)

### 5.1 Xiaomi MiMo API
- Endpoint: `https://api.mimo.xiaomi.com/v1/`
- Models: MiMo-V2.5-Pro, MiMo-V2.5, MiMo-V2.5-TTS, MiMo-TTS-VoiceClone, MiMo-TTS-VoiceDesign
- Auth: API Key (Bearer token)
- Format: OpenAI-compatible API

### 5.2 External Tools
- **FFmpeg**: Xử lý video/audio
- **VLC**: Media playback + HTTP API
- **SQLite**: Local database
- **espeak-ng**: Phonemization cho TTS

---

## 6. Yêu Cầu Dữ Liệu

### 6.1 Translation Memory Database
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

### 6.2 Glossary Database
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

## 7. Tài Liệu Phụ Trợ
- [SAD.md](../SAD.md) — Kiến trúc hệ thống
- [SDP.md](../SDP.md) — Kế hoạch phát triển
- [FEASIBILITY.md](../FEASIBILITY.md) — Khảo sát khả thi
- [RESOURCES.md](../RESOURCES.md) — Tài nguyên & Tham khảo
