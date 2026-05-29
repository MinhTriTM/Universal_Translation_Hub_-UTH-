# 📋 Logic Xử Lý — Universal Translation Hub (UTH)

## Mục lục

1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [Game Pipeline](#2-game-pipeline)
3. [Film Pipeline](#3-film-pipeline)
4. [Manga Pipeline](#4-manga-pipeline)
5. [Novel Pipeline](#5-novel-pipeline)
6. [Provider Pattern](#6-provider-pattern)
7. [Translation Memory](#7-translation-memory)

---

## 1. Tổng quan kiến trúc

```
┌─────────────────────────────────────────────────────────────────┐
│                    Universal Translation Hub                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │   Game   │    │   Film   │    │  Manga   │    │  Novel   │  │
│  │ Pipeline │    │ Pipeline │    │ Pipeline │    │ Pipeline │  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│       │               │               │               │          │
│       └───────────────┴───────────────┴───────────────┘          │
│                           │                                       │
│                    ┌──────┴──────┐                               │
│                    │  Providers  │                               │
│                    ├─────────────┤                               │
│                    │ MiMo API    │                               │
│                    │ Local (AI)  │                               │
│                    │ Auto        │                               │
│                    └──────┬──────┘                               │
│                           │                                       │
│                    ┌──────┴──────┐                               │
│                    │    TM       │                               │
│                    │ (SQLite)    │                               │
│                    └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### Chia sẻ chung

| Thành phần | Mô tả |
|------------|-------|
| **Provider** | Nguồn dịch thuật (MiMo API, Local AI) |
| **TM** | Translation Memory — cache kết quả dịch |
| **QA Agent** | Kiểm tra chất lượng bản dịch |
| **BasePipeline** | Lớp cơ sở cho tất cả pipelines |

---

## 2. Game Pipeline

### 2.1 Tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                      GAME PIPELINE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Input: Thư mục game (RPG Maker, Unity, Ren'Py, ...)           │
│                                                                   │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │ Detect  │──▶│  Scan   │──▶│ Extract │──▶│Translate│        │
│  │ Engine  │   │  Files  │   │  Text   │   │         │        │
│  └─────────┘   └─────────┘   └─────────┘   └────┬────┘        │
│                                                   │              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐        │              │
│  │Validate │◀──│ Rebuild │◀──│ Inject  │◀───────┘              │
│  │         │   │  Game   │   │  Text   │                        │
│  └─────────┘   └─────────┘   └─────────┘                        │
│                                                                   │
│  Output: Thư mục game đã dịch                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Chi tiết từng bước

#### Bước 1: Detect Engine

| | Chi tiết |
|---|----------|
| **Input** | Đường dẫn thư mục game |
| **Logic** | Quét file đặc trưng để xác định engine |
| **Output** | Tên engine (rpgmz, unity, renpy, ...) |

**Cách detect:**

| Engine | File đặc trưng |
|--------|----------------|
| RPG Maker MZ/MV | `data/Actors.json`, `www/data/` |
| RPG Maker XP | `Data/Actors.rxdata` |
| Unity | `*.assets`, `globalgamemanagers` |
| Ren'Py | `*.rpy`, `game/` |
| Kirikiri | `*.ks`, `*.xp3` |
| CatSystem2 | `*.int`, `*.pfs` |
| NScripter | `nscript.dat`, `*.txt` |
| TyranoBuilder | `data/tyrano`, `*.json` |

#### Bước 2: Scan Files

| | Chi tiết |
|---|----------|
| **Input** | Thư mục game + Engine |
| **Logic** | Tìm tất cả file chứa text cần dịch |
| **Output** | Danh sách file (paths) |

**File types theo engine:**

| Engine | File types |
|--------|-----------|
| RPG Maker MZ | `.json` (Actors, Items, Map, CommonEvents, ...) |
| Unity | `.txt`, `.json`, `.xml` trong `Assets/` |
| Ren'Py | `.rpy` (script files) |
| Kirikiri | `.ks` (script), `.csv` |
| CatSystem2 | `.int` (compiled scripts) |

#### Bước 3: Extract Text

| | Chi tiết |
|---|----------|
| **Input** | Danh sách file + Engine |
| **Logic** | Parse file, trích xuất text cần dịch |
| **Output** | `texts_dict` — Dict[key, text] |

**Format extracted data:**

```python
texts_dict = {
    "Actors.json:1:name": "勇者",
    "Actors.json:1:description": "世界を救う勇者",
    "Map001.json:5:text": "こんにちは",
    # ...
}
```

**Extract logic theo engine:**

| Engine | Logic |
|--------|-------|
| RPG Maker MZ | Parse JSON, lấy `name`, `description`, `note`, `text` từ các data files |
| Unity | Parse localization files, lấy source text |
| Ren'Py | Parse `.rpy`, lấy string literals trong `""` |
| Kirikiri | Parse `.ks`, lấy text sau `@` hoặc trong `[text]` |

#### Bước 4: Translate

| | Chi tiết |
|---|----------|
| **Input** | `texts_dict` + Source lang + Target lang |
| **Logic** | Dịch từng batch qua Provider, check TM cache |
| **Output** | `translations_dict` — Dict[key, translated_text] |

**Translate flow:**

```
texts_dict
    │
    ▼
┌─────────────────┐
│  Check TM Cache │◀──────────────────────┐
└────────┬────────┘                       │
         │                                │
    ┌────┴────┐                          │
    │ Cached? │                          │
    └────┬────┘                          │
    Yes  │  No                           │
    │    ▼                               │
    │  ┌─────────────────┐              │
    │  │  Batch Translate │              │
    │  │  (Provider API)  │              │
    │  └────────┬────────┘              │
    │           │                        │
    │           ▼                        │
    │  ┌─────────────────┐              │
    │  │  Save to TM     │──────────────┘
    │  └────────┬────────┘
    │           │
    └───────────┤
                ▼
        translations_dict
```

#### Bước 5: Inject Text

| | Chi tiết |
|---|----------|
| **Input** | `translations_dict` + Original files |
| **Logic** | Ghi bản dịch trở lại file game |
| **Output** | File game đã dịch |

**Inject logic theo engine:**

| Engine | Logic |
|--------|-------|
| RPG Maker MZ | Replace `name`, `description`, `text` trong JSON |
| Unity | Update localization files |
| Ren'Py | Replace string literals |
| Kirikiri | Replace text trong `.ks` |

#### Bước 6: Validate

| | Chi tiết |
|---|----------|
| **Input** | File game đã dịch |
| **Logic** | Kiểm tra format, encoding, completeness |
| **Output** | List lỗi (nếu có) |

**Validation checks:**

- [ ] JSON valid (RPG Maker)
- [ ] Encoding UTF-8
- [ ] Không sót text CJK
- [ ] Control codes preserved (`\n`, `{color}`, ...)
- [ ] File không bị corrupt

### 2.3 Biến thể theo Engine

#### RPG Maker MZ/MV

```
Input: Game directory
    │
    ▼
data/
    ├── Actors.json       ──▶ name, profile
    ├── Classes.json      ──▶ name, description
    ├── Items.json        ──▶ name, description
    ├── Weapons.json      ──▶ name, description
    ├── Armors.json       ──▶ name, description
    ├── Enemies.json      ──▶ name, battlerName
    ├── Skills.json       ──▶ name, description
    ├── States.json       ──▶ name, description
    ├── MapInfos.json     ──▶ name
    ├── Map001.json       ──▶ displayName, events[].list[].parameters
    ├── CommonEvents.json ──▶ name, list[].parameters
    ├── System.json       ──▶ gameTitle, terms
    ├── Tilesets.json     ──▶ name
    └── Troops.json       ──▶ name
```

#### Unity

```
Input: Game directory
    │
    ▼
Assets/
    ├── Localization/     ──▶ .json, .csv files
    ├── Resources/        ──▶ .txt, .asset files
    └── StreamingAssets/  ──▶ Custom format files
```

#### Ren'Py

```
Input: Game directory
    │
    ▼
game/
    ├── script.rpy        ──▶ Dialogue lines
    ├── options.rpy       ──▶ Menu options
    └── *.rpy             ──▶ Other scripts
```

### 2.4 Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│ GAME PIPELINE — DATA FLOW                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [Thư mục game]                                                  │
│       │                                                          │
│       ▼                                                          │
│  [Detect Engine] ──▶ "rpgmz" / "unity" / "renpy" / ...         │
│       │                                                          │
│       ▼                                                          │
│  [Scan Files] ──▶ ["Actors.json", "Map001.json", ...]           │
│       │                                                          │
│       ▼                                                          │
│  [Extract Text] ──▶ {"1": "勇者", "2": "世界を救う", ...}       │
│       │                                                          │
│       ▼                                                          │
│  [Check TM] ──▶ {"1": "Dũng sĩ"} (cached)                      │
│       │                                                          │
│       ▼                                                          │
│  [Translate] ──▶ {"2": "Cứu thế giới", ...}                    │
│       │                                                          │
│       ▼                                                          │
│  [Inject] ──▶ Actors.json (updated)                             │
│       │                                                          │
│       ▼                                                          │
│  [Validate] ──▶ OK / Errors[]                                   │
│       │                                                          │
│       ▼                                                          │
│  [Thư mục game đã dịch]                                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Film Pipeline

### 3.1 Tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                      FILM PIPELINE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Input: Video file + Subtitle file (optional)                   │
│                                                                   │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │Extract  │──▶│Translate│──▶│   TTS   │──▶│  Sync   │        │
│  │Subtitle │   │  Text   │   │  Audio  │   │  Audio  │        │
│  └─────────┘   └─────────┘   └─────────┘   └────┬────┘        │
│                                                   │              │
│  ┌─────────┐   ┌─────────┐                      │              │
│  │ Export  │◀──│  Merge  │◀──────────────────────┘              │
│  │  Files  │   │  Video  │                                       │
│  └─────────┘   └─────────┘                                       │
│                                                                   │
│  Output: Video + Subtitle đã dịch + TTS audio                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Chi tiết từng bước

#### Bước 1: Extract Subtitle

| | Chi tiết |
|---|----------|
| **Input** | Video file + Subtitle file (optional) |
| **Logic** | Load subtitle từ file, hoặc extract từ video |
| **Output** | `events` — List[{start_ms, end_ms, text}] |

**Subtitle sources:**

| Source | Logic |
|--------|-------|
| File .ass | `pysubs2.load()` |
| File .srt | `pysubs2.load()` |
| File .vtt | `pysubs2.load()` |
| Embedded | FFmpeg extract (`ffmpeg -i video.mkv -map 0:s:0 sub.srt`) |

**Event format:**

```python
events = [
    {
        "start_ms": 0,
        "end_ms": 2500,
        "text": "こんにちは",
        "original_text": "こんにちは"  # Giữ nguyên format ASS
    },
    {
        "start_ms": 2500,
        "end_ms": 5000,
        "text": "世界へようこそ",
        "original_text": "世界へようこそ"
    },
    # ...
]
```

#### Bước 2: Translate Subtitle

| | Chi tiết |
|---|----------|
| **Input** | `events` + Source lang + Target lang |
| **Logic** | Dịch từng câu qua Provider, check TM cache |
| **Output** | `events` với `translated` field |

**Translate flow:**

```
events[].text
    │
    ▼
┌─────────────────┐
│  Check TM Cache │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Cached? │
    └────┬────┘
    Yes  │  No
    │    ▼
    │  ┌─────────────────┐
    │  │  Batch Translate │
    │  │  (Provider API)  │
    │  └────────┬────────┘
    │           │
    │           ▼
    │  ┌─────────────────┐
    │  │  Save to TM     │
    │  └────────┬────────┘
    │           │
    └───────────┤
                ▼
        events[].translated
```

#### Bước 3: Generate TTS

| | Chi tiết |
|---|----------|
| **Input** | `events[].translated` + Voice |
| **Logic** | Tạo audio cho mỗi câu dịch |
| **Output** | List file `.mp3` |

**TTS flow:**

```
events[].translated
    │
    ▼
┌─────────────────┐
│  TTS Engine     │
│  (edge-tts /    │
│   MiMo TTS)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save .mp3      │
│  (per subtitle) │
└─────────────────┘
```

**TTS Engines:**

| Engine | Mô tả | Voice examples |
|--------|-------|----------------|
| edge-tts | Microsoft Edge free TTS | vi-VN-HoaiMyNeural (nữ), vi-VN-NamMinhNeural (nam) |
| MiMo TTS | Xiaomi MiMo TTS API | Custom voices |

#### Bước 4: Sync Audio

| | Chi tiết |
|---|----------|
| **Input** | TTS audio files + Original video |
| **Logic** | Merge audio vào video đúng thời điểm |
| **Output** | Video + Audio đã sync |

**Sync flow:**

```
┌─────────────────┐     ┌─────────────────┐
│ Original Video  │     │  TTS Audio      │
│ (with audio)    │     │  (per subtitle) │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
            ┌─────────────────┐
            │  FFmpeg Merge   │
            │  - Lower orig   │
            │  - Add TTS      │
            │  - Sync timing  │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Output Video   │
            │  (with TTS)     │
            └─────────────────┘
```

#### Bước 5: Export

| | Chi tiết |
|---|----------|
| **Input** | Video đã sync + Subtitle đã dịch |
| **Logic** | Lưu file output |
| **Output** | Video + Subtitle + TTS files |

**Output files:**

```
output/
├── video_translated.mkv      # Video + TTS audio
├── video_translated.ass      # Subtitle đã dịch
└── tts/
    ├── subtitle_0001.mp3     # TTS audio per line
    ├── subtitle_0002.mp3
    └── ...
```

### 3.3 Biến thể theo Subtitle Format

#### ASS/SSA Format

```
[Script Info]
Title: ...
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, ...

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.50,Default,,0,0,0,,こんにちは
Dialogue: 0,0:00:02.50,0:00:05.00,Default,,0,0,0,,世界へようこそ
```

**Extract logic:**
- Parse `[Events]` section
- Split by `,` (10+ fields)
- Text = field[9+] joined by `,`
- Clean ASS tags: `{\b1}`, `{\pos(x,y)}`, `\N`

#### SRT Format

```
1
00:00:00,000 --> 00:00:02,500
こんにちは

2
00:00:02,500 --> 00:00:05,000
世界へようこそ
```

**Extract logic:**
- Split by blank lines
- Line 1: index
- Line 2: timestamp (`HH:MM:SS,mmm --> HH:MM:SS,mmm`)
- Line 3+: text

#### VTT Format

```
WEBVTT

00:00:00.000 --> 00:00:02.500
こんにちは

00:00:02.500 --> 00:00:05.000
世界へようこそ
```

### 3.4 Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│ FILM PIPELINE — DATA FLOW                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [Video + Subtitle]                                              │
│       │                                                          │
│       ▼                                                          │
│  [Extract Subtitle] ──▶ events[{start, end, text}]              │
│       │                                                          │
│       ▼                                                          │
│  [Translate] ──▶ events[{..., translated}]                      │
│       │                                                          │
│       ├──▶ [Save Translated Subtitle] ──▶ .ass/.srt file        │
│       │                                                          │
│       ▼                                                          │
│  [Generate TTS] ──▶ .mp3 files (per subtitle)                   │
│       │                                                          │
│       ▼                                                          │
│  [Sync Audio] ──▶ Video + TTS merged                            │
│       │                                                          │
│       ▼                                                          │
│  [Export] ──▶ Video + Subtitle + TTS files                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Manga Pipeline

### 4.1 Tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                      MANGA PIPELINE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Input: Thư mục ảnh manga (JPG, PNG, PDF)                       │
│                                                                   │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │  Scan   │──▶│   OCR   │──▶│Translate│──▶│ Inpaint │        │
│  │ Images  │   │  Text   │   │         │   │         │        │
│  └─────────┘   └─────────┘   └─────────┘   └────┬────┘        │
│                                                   │              │
│  ┌─────────┐   ┌─────────┐                      │              │
│  │  Save   │◀──│ Render  │◀──────────────────────┘              │
│  │  Image  │   │  Text   │                                       │
│  └─────────┘   └─────────┘                                       │
│                                                                   │
│  Output: Ảnh đã dịch                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Chi tiết từng bước

#### Bước 1: Scan Images

| | Chi tiết |
|---|----------|
| **Input** | Đường dẫn thư mục |
| **Logic** | Tìm tất cả file ảnh |
| **Output** | List[Path] — danh sách ảnh |

**Supported formats:**

| Format | Extension |
|--------|-----------|
| JPEG | `.jpg`, `.jpeg` |
| PNG | `.png` |
| WebP | `.webp` |
| BMP | `.bmp` |
| TIFF | `.tiff` |
| PDF | `.pdf` (convert to images) |

#### Bước 2: OCR Text

| | Chi tiết |
|---|----------|
| **Input** | Ảnh manga |
| **Logic** | Detect text regions + OCR |
| **Output** | `regions` — List[{text, bbox, confidence}] |

**OCR Engines:**

| Engine | Mô tả | Ưu điểm |
|--------|-------|---------|
| manga-ocr | Python library cho manga | Chuyên dụng, chính xác |
| manga-image-translator | Full pipeline | Tự động detect + OCR |
| MiMo Vision API | Cloud API | Hỗ trợ nhiều ngôn ngữ |

**Region format:**

```python
regions = [
    {
        "text": "こんにちは",
        "bbox": [100, 50, 200, 80],  # [x, y, w, h]
        "confidence": 0.95
    },
    {
        "text": "世界へようこそ",
        "bbox": [300, 100, 250, 60],
        "confidence": 0.90
    },
    # ...
]
```

**Detection methods:**

| Method | Logic |
|--------|-------|
| Threshold + Contour | Binary threshold → findContours |
| MSER | Maximally Stable Extremal Regions |
| manga-image-translator | Deep learning detection |

#### Bước 3: Translate

| | Chi tiết |
|---|----------|
| **Input** | `regions[].text` + Source lang + Target lang |
| **Logic** | Dịch text qua Provider, check TM cache |
| **Output** | `regions[].translated` |

**Translate flow:**

```
regions[].text
    │
    ▼
┌─────────────────┐
│  Check TM Cache │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Cached? │
    └────┬────┘
    Yes  │  No
    │    ▼
    │  ┌─────────────────┐
    │  │  Batch Translate │
    │  │  (Provider API)  │
    │  └────────┬────────┘
    │           │
    │           ▼
    │  ┌─────────────────┐
    │  │  Save to TM     │
    │  └────────┬────────┘
    │           │
    └───────────┤
                ▼
        regions[].translated
```

#### Bước 4: Inpaint (Xóa text gốc)

| | Chi tiết |
|---|----------|
| **Input** | Ảnh gốc + `regions[].bbox` |
| **Logic** | Tạo mask → Inpaint xóa text |
| **Output** | Ảnh không có text |

**Inpaint methods:**

| Method | Logic |
|--------|-------|
| OpenCV inpaint | `cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)` |
| lama_mpe | Deep learning inpainting |
| manga-image-translator | Built-in inpainter |

**Inpaint flow:**

```
Original Image
    │
    ▼
┌─────────────────┐
│  Create Mask    │
│  (from bbox)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Inpaint        │
│  (remove text)  │
└────────┬────────┘
         │
         ▼
  Clean Image (no text)
```

#### Bước 5: Render Text

| | Chi tiết |
|---|----------|
| **Input** | Ảnh đã inpaint + `regions[].translated` + `regions[].bbox` |
| **Logic** | Vẽ text tiếng Việt lên ảnh |
| **Output** | Ảnh với text mới |

**Render flow:**

```
Clean Image + translated text
    │
    ▼
┌─────────────────┐
│  Find Font      │
│  (Vietnamese)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Auto Font Size │
│  (fit bbox)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Wrap Text      │
│  (fit width)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Draw Text      │
│  (on image)     │
└────────┬────────┘
         │
         ▼
  Final Image (translated)
```

**Font selection:**

| Priority | Font | Path |
|----------|------|------|
| 1 | Arial | `C:\Windows\Fonts\arial.ttf` |
| 2 | Times New Roman | `C:\Windows\Fonts\times.ttf` |
| 3 | Tahoma | `C:\Windows\Fonts\tahoma.ttf` |
| 4 | Verdana | `C:\Windows\Fonts\verdana.ttf` |

#### Bước 6: Save

| | Chi tiết |
|---|----------|
| **Input** | Ảnh đã render |
| **Logic** | Lưu file output |
| **Output** | File ảnh đã dịch |

### 4.3 Biến thể theo Engine

#### manga-image-translator (Khuyên dùng)

```
Input: Ảnh manga
    │
    ▼
┌─────────────────────────────────────────────┐
│  manga-image-translator pipeline            │
├─────────────────────────────────────────────┤
│  1. Text Detection (deep learning)          │
│  2. OCR (manga-ocr)                         │
│  3. Textline Merge                          │
│  4. Mask Refinement                         │
│  5. Inpainting (lama_mpe)                   │
│  6. Translation (configurable)              │
│  7. Rendering (auto font, auto size)        │
│  8. Colorization (optional)                 │
│  9. Upscaling (optional)                    │
└─────────────────────────────────────────────┘
    │
    ▼
Output: Ảnh đã dịch
```

**Config options:**

| Option | Default | Mô tả |
|--------|---------|-------|
| `detector` | `default` | Text detection model |
| `ocr` | `mocr` | OCR model |
| `translator` | `original` | Translation engine |
| `inpainter` | `lama_mpe` | Inpainting model |
| `colorizer` | `none` | Colorization model |
| `device` | `cuda` | Device (cuda/cpu) |

#### Manual (Fallback)

```
Input: Ảnh manga
    │
    ▼
┌─────────────────────────────────────────────┐
│  Manual pipeline                            │
├─────────────────────────────────────────────┤
│  1. Text Detection (OpenCV contour)         │
│  2. OCR (manga-ocr / MiMo API)             │
│  3. Translate (Provider)                    │
│  4. Inpaint (OpenCV inpaint)               │
│  5. Render (Pillow)                         │
└─────────────────────────────────────────────┘
    │
    ▼
Output: Ảnh đã dịch
```

### 4.4 Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│ MANGA PIPELINE — DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [Thư mục ảnh manga]                                             │
│       │                                                          │
│       ▼                                                          │
│  [Scan Images] ──▶ [img1.jpg, img2.jpg, ...]                    │
│       │                                                          │
│       ▼                                                          │
│  [OCR] ──▶ regions[{text, bbox}]                                │
│       │                                                          │
│       ▼                                                          │
│  [Translate] ──▶ regions[{..., translated}]                     │
│       │                                                          │
│       ▼                                                          │
│  [Inpaint] ──▶ Clean image (no text)                            │
│       │                                                          │
│       ▼                                                          │
│  [Render] ──▶ Image with Vietnamese text                        │
│       │                                                          │
│       ▼                                                          │
│  [Save] ──▶ translated/img1.jpg                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Novel Pipeline

### 5.1 Tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                      NOVEL PIPELINE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Input: File truyện chữ (TXT, EPUB, PDF)                        │
│                                                                   │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│  │  Parse  │──▶│ Segment │──▶│Translate│──▶│ Rebuild │        │
│  │  File   │   │  Text   │   │         │   │  File   │        │
│  └─────────┘   └─────────┘   └─────────┘   └────┬────┘        │
│                                                   │              │
│  ┌─────────┐                                     │              │
│  │  Save   │◀────────────────────────────────────┘              │
│  │  File   │                                                      │
│  └─────────┘                                                      │
│                                                                   │
│  Output: File truyện đã dịch                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Chi tiết từng bước

#### Bước 1: Parse File

| | Chi tiết |
|---|----------|
| **Input** | File truyện (TXT, EPUB, PDF) |
| **Logic** | Đọc file, extract text content |
| **Output** | Raw text content |

**Parse methods:**

| Format | Library | Logic |
|--------|---------|-------|
| TXT | Built-in | `open(file, encoding='utf-8').read()` |
| EPUB | ebooklib | `epub.read_epub()` → extract HTML → text |
| PDF | PyPDF2 / pdfplumber | `extract_text()` |

#### Bước 2: Segment Text

| | Chi tiết |
|---|----------|
| **Input** | Raw text content |
| **Logic** | Chia text thành các đoạn/câu nhỏ |
| **Output** | `segments` — List[{id, text, type}] |

**Segment types:**

| Type | Mô tả | Ví dụ |
|------|-------|-------|
| `title` | Tiêu đề chương | `第一章 はじめに` |
| `paragraph` | Đoạn văn | `こんにちは世界。今日は...` |
| `dialogue` | Hội thoại | `「こんにちは」` |
| `narration` | Narration | `彼女は言った。` |
| `note` | Chú thích | `（注：これは...）` |

**Segment logic:**

```
Raw Text
    │
    ▼
┌─────────────────┐
│  Split by       │
│  chapters       │
│  (regex: 第.*章) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Split by       │
│  paragraphs     │
│  (double newline)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classify       │
│  (title/dialog/ │
│   narration)    │
└────────┬────────┘
         │
         ▼
  segments[{id, text, type}]
```

#### Bước 3: Translate

| | Chi tiết |
|---|----------|
| **Input** | `segments[].text` + Source lang + Target lang |
| **Logic** | Dịch từng segment qua Provider, check TM cache |
| **Output** | `segments[].translated` |

**Translate considerations:**

| Issue | Solution |
|-------|----------|
| Context loss | Group segments into batches (10-20 per batch) |
| Dialogue consistency | Use glossary for character names |
| Formatting preservation | Keep `\n`, `「」`, `（）` |

**Translate flow:**

```
segments[].text
    │
    ▼
┌─────────────────┐
│  Group into     │
│  batches        │
│  (10-20 per)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Check TM Cache │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Cached? │
    └────┬────┘
    Yes  │  No
    │    ▼
    │  ┌─────────────────┐
    │  │  Batch Translate │
    │  │  (Provider API)  │
    │  └────────┬────────┘
    │           │
    │           ▼
    │  ┌─────────────────┐
    │  │  Save to TM     │
    │  └────────┬────────┘
    │           │
    └───────────┤
                ▼
        segments[].translated
```

#### Bước 4: Rebuild File

| | Chi tiết |
|---|----------|
| **Input** | `segments[].translated` + Original structure |
| **Logic** | Ghép lại thành file hoàn chỉnh |
| **Output** | File truyện đã dịch |

**Rebuild logic:**

```
segments[]
    │
    ▼
┌─────────────────┐
│  Preserve       │
│  structure      │
│  (chapters,     │
│   paragraphs)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Apply          │
│  formatting     │
│  (font, style)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate       │
│  output file    │
│  (TXT/EPUB/PDF) │
└─────────────────┘
```

#### Bước 5: Save

| | Chi tiết |
|---|----------|
| **Input** | Rebuilt content |
| **Logic** | Lưu file output |
| **Output** | File truyện đã dịch |

**Output formats:**

| Input | Output | Logic |
|-------|--------|-------|
| TXT | TXT | Direct write |
| EPUB | EPUB | Rebuild epub structure |
| PDF | PDF / TXT | Extract text → translate → write |

### 5.3 Biến thể theo Format

#### TXT Format

```
Input: novel.txt
    │
    ▼
┌─────────────────┐
│  Read file      │
│  (UTF-8)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Split by       │
│  paragraphs     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Translate      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Write file     │
└─────────────────┘
    │
    ▼
Output: novel_vi.txt
```

#### EPUB Format

```
Input: novel.epub
    │
    ▼
┌─────────────────┐
│  Read EPUB      │
│  (ebooklib)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extract HTML   │
│  chapters       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse HTML     │
│  → text blocks  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Translate      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Rebuild HTML   │
│  with translated│
│  text           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create EPUB    │
│  (preserve      │
│   structure)    │
└─────────────────┘
    │
    ▼
Output: novel_vi.epub
```

#### PDF Format

```
Input: novel.pdf
    │
    ▼
┌─────────────────┐
│  Extract text   │
│  (PyPDF2 /      │
│   pdfplumber)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Translate      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Output:        │
│  - TXT file     │
│  - OR new PDF   │
│    (with FPDF2) │
└─────────────────┘
    │
    ▼
Output: novel_vi.txt / novel_vi.pdf
```

### 5.4 Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│ NOVEL PIPELINE — DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [File truyện (TXT/EPUB/PDF)]                                   │
│       │                                                          │
│       ▼                                                          │
│  [Parse File] ──▶ Raw text content                              │
│       │                                                          │
│       ▼                                                          │
│  [Segment] ──▶ segments[{id, text, type}]                       │
│       │                                                          │
│       ▼                                                          │
│  [Translate] ──▶ segments[{..., translated}]                    │
│       │                                                          │
│       ▼                                                          │
│  [Rebuild] ──▶ Translated content                               │
│       │                                                          │
│       ▼                                                          │
│  [Save] ──▶ novel_vi.txt / .epub / .pdf                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Provider Pattern

### 6.1 Tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                      PROVIDER PATTERN                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              TranslationProvider (ABC)                    │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  + translate(text, src, tgt) → str                       │   │
│  │  + translate_batch(texts, src, tgt) → List[str]          │   │
│  │  + get_name() → str                                      │   │
│  │  + is_available() → bool                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                  │
│         │                 │                 │                  │
│         ▼                 ▼                 ▼                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ MiMoProvider│  │LocalProvider│  │  AutoProvider│           │
│  │             │  │             │  │  (fallback)  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 MiMoProvider

| Field | Value |
|-------|-------|
| **Name** | `mimo` |
| **Endpoint** | `https://token-plan-sgp.xiaomimimo.com/anthropic` |
| **Auth** | `x-api-key` header |
| **Format** | Anthropic Messages API |

**Models:**

| Model | Mô tả |
|-------|-------|
| `mimo-v2.5-pro` | Reasoning mạnh nhất |
| `mimo-v2.5` | Nhanh, đa năng |
| `mimo-v2-pro` | Thế hệ trước |
| `mimo-v2.5-omni` | Đa modal |

**Translate flow:**

```
text
    │
    ▼
┌─────────────────┐
│  Build prompt   │
│  (system + user)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Call API       │
│  POST /v1/      │
│  messages       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse response │
│  (text blocks)  │
└─────────────────┘
    │
    ▼
translated_text
```

### 6.3 LocalProvider

| Field | Value |
|-------|-------|
| **Name** | `local` |
| **Endpoint** | `http://localhost:5000` |
| **Backend** | AG-Translator |

**Endpoints:**

| Endpoint | Mô tả |
|----------|-------|
| `POST /api/translate/dolphin` | Dịch bằng Dolphin GGUF |
| `POST /api/translate/hymt` | Dịch bằng Tencent HY-MT |

### 6.4 AutoProvider

| Field | Value |
|-------|-------|
| **Name** | `auto` |
| **Logic** | Thử MiMo trước, fallback Local |

**Fallback flow:**

```
request
    │
    ▼
┌─────────────────┐
│  MiMo available?│
└────────┬────────┘
    Yes  │  No
    │    ▼
    │  ┌─────────────────┐
    │  │ Local available? │
    │  └────────┬────────┘
    │      Yes  │  No
    │      │    ▼
    │      │  Error
    │      ▼
    │  Use Local
    ▼
Use MiMo
```

---

## 7. Translation Memory

### 7.1 Tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                   TRANSLATION MEMORY                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    SQLite Database                        │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  Table: translations                                     │   │
│  │  - source_text (TEXT)                                    │   │
│  │  - translated_text (TEXT)                                │   │
│  │  - source_lang (TEXT)                                    │   │
│  │  - target_lang (TEXT)                                    │   │
│  │  - provider (TEXT)                                       │   │
│  │  - timestamp (DATETIME)                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Methods:                                                         │
│  + get(source_text, src_lang, tgt_lang) → str | None            │
│  + put(source_text, translated, src, tgt, provider)             │
│  + stats() → {total, by_language, by_provider}                  │
│  + clear()                                                      │
│  + export_json() → str                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Cache Flow

```
Translate request
    │
    ▼
┌─────────────────┐
│  Generate key   │
│  (src_lang +    │
│   source_text)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query SQLite   │
│  WHERE key = ?  │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Found?  │
    └────┬────┘
    Yes  │  No
    │    ▼
    │  ┌─────────────────┐
    │  │  Call Provider   │
    │  │  (translate)     │
    │  └────────┬────────┘
    │           │
    │           ▼
    │  ┌─────────────────┐
    │  │  Save to SQLite │
    │  └────────┬────────┘
    │           │
    └───────────┤
                ▼
        Return translated text
```

### 7.3 Benefits

| Benefit | Mô tả |
|---------|-------|
| **Tốc độ** | Cache hit = instant response |
| **Chi tiết** | Giảm API calls = tiết kiệm chi phí |
| **Consistency** | Cùng text luôn cùng dịch |
| **Offline** | Có thể dùng khi mất kết nối |

---

## Appendix: Summary Tables

### Pipeline Comparison

| Feature | Game | Film | Manga | Novel |
|---------|------|------|-------|-------|
| **Input** | Game directory | Video + Subtitle | Image directory | Text file |
| **Output** | Translated game | Video + Subtitle + TTS | Translated images | Translated text |
| **OCR** | ❌ | ❌ | ✅ | ❌ |
| **TTS** | ❌ | ✅ | ❌ | ❌ |
| **Inpaint** | ❌ | ❌ | ✅ | ❌ |
| **Complexity** | High | Medium | Medium | Low |

### Provider Comparison

| Feature | MiMo | Local | Auto |
|---------|------|-------|------|
| **Speed** | Fast | Medium | Variable |
| **Quality** | High | High | Best available |
| **Cost** | API cost | Free | Optimized |
| **Offline** | ❌ | ✅ | Partial |

### Data Types

| Type | Format | Example |
|------|--------|---------|
| `texts_dict` | Dict[str, str] | `{"1": "勇者", "2": "世界"}` |
| `events` | List[Dict] | `[{"start": 0, "end": 2500, "text": "こんにちは"}]` |
| `regions` | List[Dict] | `[{"text": "こんにちは", "bbox": [100, 50, 200, 80]}]` |
| `segments` | List[Dict] | `[{"id": 1, "text": "第一章", "type": "title"}]` |