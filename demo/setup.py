#!/usr/bin/env python3
"""MIMO-AXON Demo Setup - Copy files tu 3 du an nguon."""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def _resolve_source(name: str, env_var: str, fallbacks: list[str]) -> Path:
    """Resolve đường dẫn nguồn từ env var → fallbacks."""
    # 1. Ưu tiên env var
    env_val = os.environ.get(env_var)
    if env_val:
        p = Path(env_val)
        if p.exists():
            return p

    # 2. Thử các fallback
    for fb in fallbacks:
        p = Path(fb)
        if p.exists():
            return p

    # 3. Trả về fallback đầu tiên (dù không tồn tại)
    return Path(fallbacks[0])


def _detect_sources() -> dict[str, Path]:
    """Tự động detect đường dẫn 3 dự án nguồn."""
    base = Path(__file__).resolve().parent.parent.parent  # Du_An_Mini
    return {
        "xiaomi_mimo": _resolve_source(
            "xiaomi_mimo", "MIMO_SOURCE_XIAOMI",
            [
                str(base / "XiaoMi100T"),
                r"D:\Du_An_Mini\XiaoMi100T",
                str(Path.home() / "Du_An_Mini" / "XiaoMi100T"),
            ],
        ),
        "dichgame": _resolve_source(
            "dichgame", "MIMO_SOURCE_DICHGAME",
            [
                r"E:\DichGame",
                str(base.parent / "DichGame"),
                str(Path.home() / "DichGame"),
            ],
        ),
        "manga_translator": _resolve_source(
            "manga_translator", "MIMO_SOURCE_MANGA",
            [
                r"E:\DichGame\Tool\manga-image-translator",
                str(base.parent / "DichGame" / "Tool" / "manga-image-translator"),
            ],
        ),
    }


# === Đường dẫn nguồn (dynamic) ===
SOURCES = _detect_sources()

# === Danh sách file cần copy (nguồn → đích) ===
COPY_MAP = {
    # --- XiaoMi100T: OCR + Dubbing core ---
    "xiaomi_mimo": [
        ("src/core/ocr_engine.py", "xiaomi_mimo/ocr_engine.py"),
        ("src/modules/dubbing/TMF.py", "xiaomi_mimo/dubbing_tmf.py"),
        ("src/modules/dubbing/TMF_GoogleTTS.py", "xiaomi_mimo/dubbing_google_tts.py"),
        (".env.example", "xiaomi_mimo/.env.example"),
        ("requirements.txt", "xiaomi_mimo/requirements.txt"),
    ],
    # --- DichGame: Backend server + engines ---
    "dichgame": [
        ("Backend/server.py", "dichgame/server.py"),
        ("Backend/engines_logic.py", "dichgame/engines_logic.py"),
        ("Backend/requirements.txt", "dichgame/requirements.txt"),
        ("Tool/modules/core/__init__.py", "dichgame/modules_core/__init__.py"),
    ],
    # --- manga-image-translator: Core translator ---
    "manga_translator": [
        ("manga_translator/__init__.py", "manga_translator/__init__.py"),
        ("requirements.txt", "manga_translator/requirements.txt"),
        (".env", "manga_translator/.env.example"),
    ],
}


def check_sources() -> dict[str, bool]:
    """Kiểm tra tồn tại của các thư mục nguồn."""
    status = {}
    for name, path in SOURCES.items():
        exists = path.exists()
        status[name] = exists
        icon = "✅" if exists else "❌"
        print(f"  {icon} {name}: {path}")
    return status


def copy_files(demo_dir: Path, dry_run: bool = False) -> list[str]:
    """Copy files từ nguồn về demo directory."""
    copied = []
    skipped = []

    for source_name, file_list in COPY_MAP.items():
        source_root = SOURCES[source_name]
        print(f"\n📦 [{source_name}]")

        for src_rel, dst_rel in file_list:
            src_path = source_root / src_rel
            dst_path = demo_dir / dst_rel

            if not src_path.exists():
                skipped.append(f"  ⚠️  Bỏ qua (không tìm thấy): {src_rel}")
                continue

            if dry_run:
                copied.append(f"  📋 Sẽ copy: {src_rel} → {dst_rel}")
                continue

            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            size = dst_path.stat().st_size
            copied.append(f"  ✅ {src_rel} → {dst_rel} ({size:,} bytes)")

    # In kết quả
    for msg in copied:
        print(msg)
    for msg in skipped:
        print(msg)

    return copied


def create_manifest(demo_dir: Path, copied: list[str]):
    """Tạo file manifest ghi lại các file đã copy."""
    manifest_path = demo_dir / "MANIFEST.md"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("# MIMO-AXON Demo — File Manifest\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Nguồn\n\n")
        for name, path in SOURCES.items():
            f.write(f"- **{name}**: `{path}`\n")
        f.write("\n## Files đã copy\n\n")
        for line in copied:
            if line.startswith("  ✅"):
                f.write(f"- {line.strip()}\n")
        f.write("\n")
    print(f"\n📄 Manifest: {manifest_path}")


def main():
    global SOURCES

    parser = argparse.ArgumentParser(description="MIMO-AXON Demo Setup")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ hiển thị, không copy")
    parser.add_argument(
        "--demo-dir", type=Path, default=None,
        help="Thư mục demo (mặc định: cùng cấp script)"
    )
    parser.add_argument("--xiaomi", type=Path, default=None, help="Đường dẫn XiaoMi100T")
    parser.add_argument("--dichgame", type=Path, default=None, help="Đường dẫn DichGame")
    parser.add_argument("--manga", type=Path, default=None, help="Đường dẫn manga-translator")
    args = parser.parse_args()

    # CLI overrides
    if args.xiaomi:
        SOURCES["xiaomi_mimo"] = args.xiaomi
    if args.dichgame:
        SOURCES["dichgame"] = args.dichgame
    if args.manga:
        SOURCES["manga_translator"] = args.manga

    demo_dir = args.demo_dir or Path(__file__).parent
    demo_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  MIMO-AXON Demo Setup")
    print("  Copy files từ 3 dự án nguồn")
    print("=" * 60)

    # 1. Kiểm tra nguồn
    print("\n🔍 Kiểm tra thư mục nguồn:")
    status = check_sources()
    available = sum(1 for v in status.values() if v)
    print(f"\n  → {available}/{len(status)} thư mục khả dụng")

    if available == 0:
        print("\n❌ Không tìm thấy thư mục nào. Kiểm tra lại đường dẫn.")
        sys.exit(1)

    # 2. Copy files
    mode = "DRY RUN" if args.dry_run else "COPY"
    print(f"\n{'=' * 60}")
    print(f"  [{mode}] Copy files:")
    print(f"{'=' * 60}")
    copied = copy_files(demo_dir, dry_run=args.dry_run)

    # 3. Tạo manifest
    if not args.dry_run:
        create_manifest(demo_dir, copied)

    # 4. Tóm tắt
    print(f"\n{'=' * 60}")
    total = len([c for c in copied if c.startswith("  ✅")])
    print(f"  Hoàn tất! Đã copy {total} files.")
    print(f"  Thư mục demo: {demo_dir}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
