"""
Universal Translation Hub (UTH) — Entry Point
Hệ thống dịch thuật phổ quát đa phương tiện
Powered by Xiaomi MiMo V2.5 + Local AI Models

Tác giả: Đoàn Minh Trí — DTHU University
License: MIT (2026)
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Thêm src vào Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.providers import get_provider
from src.memory import TranslationMemory
from src.pipelines import GamePipeline, MangaPipeline, FilmPipeline
from src.utils.file_detector import detect_pipeline

__version__ = "0.2.0"


# ===== BANNER =====
BANNER = """
╔══════════════════════════════════════════════════════════╗
║         Universal Translation Hub (UTH) v{:<14s}║
║         Powered by MiMo V2.5 + Local AI                 ║
║         Multi-Agent AI Translation System                ║
╚══════════════════════════════════════════════════════════╝
"""


async def run_pipeline(args):
    """Chạy pipeline chính."""
    provider_name = args.provider
    provider = get_provider(provider_name)
    memory = TranslationMemory()

    print(f"  Provider: {provider.get_name()}")
    print(f"  Available: {provider.is_available()}")

    if not provider.is_available():
        print(f"\n  ⚠️  Provider '{provider_name}' không sẵn sàng!")
        if provider_name == "mimo":
            print("  → Set MIMO_API_KEY trong env hoặc .env file")
            print("  → Thử: python main.py --provider local")
        elif provider_name == "local":
            print("  → Chạy AG-Translator backend: cd E:\\DichGame\\Backend && python server.py")
            print("  → Thử: python main.py --provider mimo")
        return None

    mode = args.mode
    if mode == "auto":
        mode = detect_pipeline(args.input)
        print(f"  Auto-detected pipeline: {mode}")

    # Chọn pipeline
    pipeline_map = {
        "game": lambda: GamePipeline(provider, memory, backend_url=args.backend),
        "manga": lambda: MangaPipeline(provider, memory),
        "film": lambda: FilmPipeline(provider, memory),
    }

    if mode not in pipeline_map:
        print(f"  ❌ Pipeline không hỗ trợ: {mode}")
        return None

    pipeline = pipeline_map[mode]()

    print(f"\n{'='*60}")
    print(f"  PIPELINE: {mode.upper()}")
    print(f"  Input: {args.input}")
    print(f"  Provider: {provider.get_name()}")
    print(f"{'='*60}\n")

    # Build options
    options = {
        "source_lang": args.source_lang,
        "target_lang": args.target_lang,
    }
    if args.subtitle:
        options["subtitle"] = args.subtitle
    if args.output:
        options["output_dir"] = args.output
    if args.voice:
        options["voice"] = args.voice
    if args.engine:
        options["engine"] = args.engine

    result = await pipeline.execute(args.input, options)

    # Report
    print(f"\n{'='*60}")
    print(f"  KẾT QUẢ")
    print(f"{'='*60}")
    print(result.summary())

    # TM stats
    stats = memory.stats()
    if stats.get("total_entries", 0) > 0:
        print(f"\n  Translation Memory: {stats['total_entries']} entries")

    return result


async def run_demo():
    """Chạy demo showcase tất cả 3 pipelines."""
    print("  🎮 DEMO MODE — Không cần API key hay backend\n")

    provider = get_provider("local")
    memory = TranslationMemory()

    # Demo 1: Game
    print("━" * 60)
    print("  DEMO 1: Dịch Game (RPG Maker)")
    print("━" * 60)
    game = GamePipeline(provider, memory)
    print(f"  Pipeline: {game.name}")
    print(f"  Steps: Detect → Scan → Extract → Translate → Inject → Validate")
    print(f"  Backend: {game.backend_url}")
    print(f"  ✅ Game Pipeline sẵn sàng (cần AG-Translator backend để chạy)\n")

    # Demo 2: Manga
    print("━" * 60)
    print("  DEMO 2: Dịch Manga/Comic")
    print("━" * 60)
    manga = MangaPipeline(provider, memory)
    print(f"  Pipeline: {manga.name}")
    print(f"  Steps: Scan → OCR → Translate → Inpaint → Render")
    print(f"  OCR: manga-ocr (Japanese) + MiMo API fallback")
    print(f"  ✅ Manga Pipeline sẵn sàng\n")

    # Demo 3: Film
    print("━" * 60)
    print("  DEMO 3: Dịch Film + Thuyết Minh")
    print("━" * 60)
    film = FilmPipeline(provider, memory)
    print(f"  Pipeline: {film.name}")
    print(f"  Steps: Subtitle → Translate → TTS → Sync")
    print(f"  TTS: edge-tts (vi-VN-HoaiMyNeural)")
    print(f"  ✅ Film Pipeline sẵn sàng\n")

    # Summary
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                    DEMO HOÀN TẤT                        ║
╠══════════════════════════════════════════════════════════╣
║  ✅ Game Pipeline:  12 engines, Smart Auto-Pilot        ║
║  ✅ Manga Pipeline: OCR + Inpainting + Render           ║
║  ✅ Film Pipeline:  Subtitle + TTS + Voice              ║
║  ✅ Provider:       MiMo API + Local Models             ║
║  ✅ Translation Memory: SQLite cache                    ║
╠══════════════════════════════════════════════════════════╣
║  📖 Docs:  docs/vi/SRS.md, SAD.md, SDP.md              ║
║  🌐 README: README.md                                   ║
║  🔑 API:   MIMO_API_KEY hoặc AG-Translator backend      ║
╚══════════════════════════════════════════════════════════╝
    """)


async def main():
    parser = argparse.ArgumentParser(
        description="Universal Translation Hub (UTH) — Dịch thuật AI đa phương tiện",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python main.py --mode game --input "E:\\Games\\MyGame" --provider local
  python main.py --mode manga --input "./manga_chapter_01/"
  python main.py --mode film --input "./movie.mkv" --subtitle "./movie.ass"
  python main.py --demo
  python main.py --mode auto --input "./any_content/"
        """
    )
    parser.add_argument("--mode", choices=["game", "manga", "film", "auto"], default="auto",
                        help="Chọn pipeline: game/manga/film/auto (default: auto)")
    parser.add_argument("--input", type=str, default="",
                        help="Đường dẫn file/thư mục đầu vào")
    parser.add_argument("--output", type=str, default="",
                        help="Thư mục đầu ra (optional)")
    parser.add_argument("--subtitle", type=str, default="",
                        help="Đường dẫn file phụ đề (chỉ cho film mode)")
    parser.add_argument("--provider", choices=["auto", "mimo", "local"], default="auto",
                        help="Translation provider: auto/mimo/local (default: auto)")
    parser.add_argument("--engine", type=str, default="",
                        help="Game engine (auto-detect nếu bỏ qua)")
    parser.add_argument("--source-lang", type=str, default="auto",
                        help="Ngôn ngữ nguồn (default: auto)")
    parser.add_argument("--target-lang", type=str, default="vi",
                        help="Ngôn ngữ đích (default: vi)")
    parser.add_argument("--voice", type=str, default="vi-VN-HoaiMyNeural",
                        help="TTS voice cho film pipeline")
    parser.add_argument("--backend", type=str, default="http://localhost:5000",
                        help="AG-Translator backend URL")
    parser.add_argument("--demo", action="store_true",
                        help="Chạy demo mode")
    parser.add_argument("--version", action="version", version=f"UTH v{__version__}")

    args = parser.parse_args()

    print(BANNER.format(__version__))

    if args.demo:
        await run_demo()
        return

    if not args.input:
        parser.print_help()
        print("\n  ⚠️  Cần --input để chạy pipeline!")
        print("  → Hoặc dùng --demo để xem demo")
        return

    if not os.path.exists(args.input):
        print(f"  ❌ Không tìm thấy: {args.input}")
        return

    await run_pipeline(args)


if __name__ == "__main__":
    asyncio.run(main())
