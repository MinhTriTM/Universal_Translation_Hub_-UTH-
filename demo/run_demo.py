#!/usr/bin/env python3
"""
MIMO-AXON Demo — Chạy demo tổng hợp 3 dự án.

Hệ sinh thái AI đa tác nhân:
  1. XiaoMi100T  — OCR + Dubbing (Gemini API)
  2. DichGame    — Game Translation Engine (LLM)
  3. manga-image-translator — Manga/Comic Translation (OCR + Inpainting)

Usage:
  python run_demo.py                    # Demo interactive
  python run_demo.py --check            # Kiểm tra hệ thống
  python run_demo.py --show-modules     # Hiển thị modules
"""

import os
import sys
import importlib.util
from pathlib import Path
from datetime import datetime

# === Constants ===
DEMO_DIR = Path(__file__).parent
PROJECT_ROOT = DEMO_DIR.parent


# ============================================================
#  UTILS
# ============================================================

def banner(title: str, width: int = 60):
    """In banner đẹp."""
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def section(title: str):
    """In section header."""
    print(f"\n--- [{title}] ---")


def check_module(name: str, path: Path) -> bool:
    """Kiểm tra module có tồn tại không."""
    exists = path.exists()
    icon = "✅" if exists else "❌"
    print(f"  {icon} {name}: {path}")
    return exists


def load_module_from_path(name: str, path: Path):
    """Load module Python từ đường dẫn."""
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"  ⚠️  Lỗi load {name}: {e}")
    return None


# ============================================================
#  CHECK SYSTEM
# ============================================================

def check_system():
    """Kiểm tra toàn bộ hệ thống."""
    banner("MIMO-AXON — Kiểm Tra Hệ Thống")

    results = {"total": 0, "ok": 0, "fail": 0}

    # 1. Python version
    section("Python")
    v = sys.version_info
    print(f"  {'✅' if v.major >= 3 and v.minor >= 10 else '⚠️'} Python {v.major}.{v.minor}.{v.micro}")
    results["total"] += 1
    if v.major >= 3 and v.minor >= 10:
        results["ok"] += 1

    # 2. Demo files
    section("Demo Files")
    demo_files = [
        ("setup.py", DEMO_DIR / "setup.py"),
        ("run_demo.py", DEMO_DIR / "run_demo.py"),
    ]
    for name, path in demo_files:
        results["total"] += 1
        if check_module(name, path):
            results["ok"] += 1
        else:
            results["fail"] += 1

    # 3. Source projects
    section("Dự án nguồn")
    sources = [
        ("XiaoMi100T", Path(r"D:\Du_An_Mini\XiaoMi100T")),
        ("DichGame", Path(r"E:\DichGame")),
        ("manga-image-translator", Path(r"E:\DichGame\Tool\manga-image-translator")),
    ]
    for name, path in sources:
        results["total"] += 1
        if check_module(name, path):
            results["ok"] += 1
        else:
            results["fail"] += 1

    # 4. Copied modules
    section("Modules đã copy")
    modules = [
        ("XiaoMi OCR", DEMO_DIR / "xiaomi_mimo" / "ocr_engine.py"),
        ("XiaoMi Dubbing", DEMO_DIR / "xiaomi_mimo" / "dubbing_tmf.py"),
        ("DichGame Server", DEMO_DIR / "dichgame" / "server.py"),
        ("DichGame Engines", DEMO_DIR / "dichgame" / "engines_logic.py"),
        ("Manga Translator", DEMO_DIR / "manga_translator" / "__init__.py"),
    ]
    for name, path in modules:
        results["total"] += 1
        if check_module(name, path):
            results["ok"] += 1
        else:
            results["fail"] += 1

    # 5. Dependencies
    section("Dependencies (kiểm tra import)")
    deps = [
        ("dotenv", "python_dotenv"),
        ("tqdm", "tqdm"),
        ("pysubs2", "pysubs2"),
    ]
    for display_name, module_name in deps:
        results["total"] += 1
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {display_name}")
            results["ok"] += 1
        except ImportError:
            print(f"  ❌ {display_name} (chưa cài)")
            results["fail"] += 1

    # Summary
    banner("Kết quả kiểm tra")
    print(f"  Tổng: {results['total']} | ✅ {results['ok']} | ❌ {results['fail']}")
    if results["fail"] == 0:
        print("  🎉 Hệ thống sẵn sàng!")
    else:
        print(f"  ⚠️  Cần khắc phục {results['fail']} mục.")
    return results["fail"] == 0


# ============================================================
#  SHOW MODULES
# ============================================================

def show_modules():
    """Hiển thị kiến trúc modules của 3 dự án."""
    banner("MIMO-AXON — Kiến Trúc Modules")

    modules = {
        "🔹 XiaoMi100T (OCR + Dubbing)": {
            "ocr_engine.py": "Trích xuất sub từ video bằng FFmpeg + Gemini 2.5 Flash Lite",
            "dubbing_tmf.py": "Text-to-Speech dubbing engine (TMF format)",
            "dubbing_google_tts.py": "Google Cloud TTS integration",
        },
        "🔹 DichGame (Game Translation)": {
            "server.py": "FastAPI backend — serve translation API",
            "engines_logic.py": "Core translation engines (50KB+ logic)",
            "modules_core/": "Game-specific parsers (RPGM, Unity, Kirikiri, NScripter...)",
        },
        "🔹 manga-image-translator": {
            "__init__.py": "Manga/comic OCR + translation + inpainting",
            "server/": "REST API server",
            "requirements.txt": "Dependencies (torch, transformers, manga-ocr...)",
        },
    }

    for project, files in modules.items():
        section(project)
        for filename, desc in files.items():
            print(f"  📄 {filename:30s} — {desc}")

    # Architecture diagram
    section("Luồng dữ liệu")
    print("""
  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │   XiaoMi100T    │     │    DichGame     │     │  Manga-Translator│
  │  (Video/Sub)    │     │  (Game Files)   │     │  (Comic Images)  │
  └────────┬────────┘     └────────┬────────┘     └────────┬─────────┘
           │                       │                       │
           ▼                       ▼                       ▼
  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │  Gemini 2.5     │     │  LLM Engine     │     │  OCR + Inpaint  │
  │  Flash Lite     │     │  (llama-cpp)    │     │  (manga-ocr)    │
  └────────┬────────┘     └────────┬────────┘     └────────┬─────────┘
           │                       │                       │
           ▼                       ▼                       ▼
  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │  Edge TTS /     │     │  Translated     │     │  Translated     │
  │  Google Cloud   │     │  Game Scripts   │     │  Comic Pages    │
  └─────────────────┘     └─────────────────┘     └─────────────────┘
    """)


# ============================================================
#  DEMO INTERACTIVE
# ============================================================

def demo_interactive():
    """Demo interactive chính."""
    banner("MIMO-AXON — Demo Tương Tác")

    print("""
  Chọn demo:

  1. 🔍 OCR Demo      — Trích xuất sub từ video (XiaoMi100T)
  2. 🎮 Game Demo      — Dịch game engine (DichGame)
  3. 📖 Manga Demo     — Dịch manga/comic (manga-image-translator)
  4. 🔧 Check System   — Kiểm tra hệ thống
  5. 📦 Show Modules   — Xem kiến trúc modules
  0. ❌ Thoát
    """)

    while True:
        choice = input("  👉 Chọn (0-5): ").strip()

        if choice == "1":
            demo_ocr()
        elif choice == "2":
            demo_game()
        elif choice == "3":
            demo_manga()
        elif choice == "4":
            check_system()
        elif choice == "5":
            show_modules()
        elif choice == "0":
            print("\n  👋 Tạm biệt!\n")
            break
        else:
            print("  ⚠️  Lựa chọn không hợp lệ.")


def demo_ocr():
    """Demo OCR từ XiaoMi100T."""
    section("OCR Demo — XiaoMi100T")
    ocr_path = DEMO_DIR / "xiaomi_mimo" / "ocr_engine.py"
    ocr_module = load_module_from_path("ocr_engine", ocr_path)

    if ocr_module:
        print("  📄 Module OCR đã load thành công.")
        print("  🔧 Chức năng: extract_subtitles_ocr(video_path, output_dir)")
        print("  📝 Sử dụng FFmpeg + Gemini 2.5 Flash Lite")
        # Demo với dummy path
        print("\n  💡 Demo call (dry run):")
        print("     extract_subtitles_ocr('video.mp4', 'output/ocr_frames')")
    else:
        print("  ❌ Không load được module OCR.")
        print("  💡 Chạy: python setup.py để copy files.")


def demo_game():
    """Demo Game Translation từ DichGame."""
    section("Game Demo — DichGame")
    engine_path = DEMO_DIR / "dichgame" / "engines_logic.py"

    if engine_path.exists():
        print("  📄 Engines logic đã có sẵn.")
        print("  🔧 Kích thước:", engine_path.stat().st_size, "bytes")
        print("  📝 Hỗ trợ: RPGM, Unity, Kirikiri, NScripter, Ren'Py, Wolf, Tyrano...")
    else:
        print("  ❌ Không tìm thấy engines_logic.py.")
        print("  💡 Chạy: python setup.py để copy files.")


def demo_manga():
    """Demo Manga Translation."""
    section("Manga Demo — manga-image-translator")
    manga_path = DEMO_DIR / "manga_translator" / "__init__.py"

    if manga_path.exists():
        print("  📄 Manga translator module đã có sẵn.")
        print("  🔧 OCR: manga-ocr (Japanese)")
        print("  📝 Inpainting: PyTorch + custom models")
    else:
        print("  ❌ Không tìm thấy manga_translator module.")
        print("  💡 Chạy: python setup.py để copy files.")


# ============================================================
#  MAIN
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="MIMO-AXON Demo")
    parser.add_argument("--check", action="store_true", help="Kiểm tra hệ thống")
    parser.add_argument("--show-modules", action="store_true", help="Hiển thị modules")
    parser.add_argument("--interactive", action="store_true", help="Demo tương tác")
    args = parser.parse_args()

    if args.check:
        check_system()
    elif args.show_modules:
        show_modules()
    elif args.interactive:
        demo_interactive()
    else:
        # Mặc định: chạy interactive
        demo_interactive()


if __name__ == "__main__":
    main()
