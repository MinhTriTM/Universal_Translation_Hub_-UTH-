# -*- coding: utf-8 -*-
"""
FileDetector - Nhận diện loại file để định tuyến pipeline.
Hỗ trợ 3 loại pipeline: game, manga, film.
"""

import os
from pathlib import Path
from typing import Dict, List

# ============================================================================
# Các phần mở rộng / đặc điểm nhận diện cho từng loại pipeline
# ============================================================================

# Game indicators: extension hoặc tên file/thư mục
_GAME_EXTENSIONS = {
    ".rpgproject",   # RPG Maker MV/MZ project
    ".rxdata",       # RPG Maker XP
    ".rvdata",       # RPG Maker VX
    ".rvdata2",      # RPG Maker VX Ace
    ".xp3",          # Kirikiri engine
    ".int",          # NScripter / ONScripter
    ".rpa",          # Ren'Py archive
    ".ks",           # Kirikiri script
    ".nsa",          # NScripter archive
    ".pak",          # Generic game archive
    ".rpgmvp",       # RPG Maker MZ encrypted image
    ".rpgmvm",       # RPG Maker MZ encrypted audio
    ".rpgmvo",       # RPG Maker MZ encrypted other
}

_GAME_FILENAMES = {
    "game.ini",      # CatSystem2, NScripter, ONScripter
    "game.exe",      # Executable game
    "rgss*.dll",     # RPG Maker runtime
}

_GAME_DIRNAMES = {
    "www",           # RPG Maker MV/MZ web export
    "data",          # RPG Maker data folder
    "renpy",         # Ren'Py engine folder
}

# Manga indicators: thư mục chứa nhiều ảnh
_MANGA_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}
_MANGA_EXTENSIONS = {".pdf"} | _MANGA_IMAGE_EXTENSIONS

# Film indicators
_FILM_VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".ts", ".m4v"}
_FILM_SUBTITLE_EXTENSIONS = {".ass", ".srt", ".vtt", ".sub", ".ssa", ".idx"}
_FILM_EXTENSIONS = _FILM_VIDEO_EXTENSIONS | _FILM_SUBTITLE_EXTENSIONS


def detect_pipeline(input_path: str) -> str:
    """
    Nhận diện loại pipeline dựa trên đường dẫn đầu vào.

    Args:
        input_path: Đường dẫn đến file hoặc thư mục.

    Returns:
        "game", "manga", hoặc "film".

    Raises:
        FileNotFoundError: Nếu đường dẫn không tồn tại.
    """
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Đường dẫn không tồn tại: {input_path}")

    # Nếu là file đơn lẻ
    if path.is_file():
        return _detect_single_file(path)

    # Nếu là thư mục — kiểm tra nội dung bên trong
    if path.is_dir():
        return _detect_directory(path)

    # Fallback
    return "game"


def _detect_single_file(path: Path) -> str:
    """Nhận diện loại pipeline từ một file đơn lẻ."""
    suffix = path.suffix.lower()
    name_lower = path.name.lower()

    # Kiểm tra game extension
    if suffix in _GAME_EXTENSIONS:
        return "game"

    # Kiểm tra game filename
    if name_lower in _GAME_FILENAMES:
        return "game"

    # Kiểm tra film extension
    if suffix in _FILM_EXTENSIONS:
        return "film"

    # Kiểm tra manga (PDF chứa ảnh, hoặc file ảnh)
    if suffix in _MANGA_EXTENSIONS:
        return "manga"

    # Fallback: dựa vào nội dung file
    if suffix in {".json", ".xml", ".txt", ".csv"}:
        # Có thể là data game
        return "game"

    return "game"


def _detect_directory(path: Path) -> str:
    """Nhận diện loại pipeline từ thư mục."""
    # Liệt kê tất cả file và thư mục con
    try:
        entries = list(path.iterdir())
    except PermissionError:
        return "game"

    file_names = set()
    dir_names = set()
    extensions = set()
    image_count = 0
    video_count = 0
    subtitle_count = 0

    for entry in entries:
        if entry.is_file():
            file_names.add(entry.name.lower())
            ext = entry.suffix.lower()
            extensions.add(ext)

            if ext in _MANGA_IMAGE_EXTENSIONS:
                image_count += 1
            if ext in _FILM_VIDEO_EXTENSIONS:
                video_count += 1
            if ext in _FILM_SUBTITLE_EXTENSIONS:
                subtitle_count += 1

        elif entry.is_dir():
            dir_names.add(entry.name.lower())

    # Kiểm tra game indicators
    game_score = 0

    # Game extensions
    if extensions & _GAME_EXTENSIONS:
        game_score += 3

    # Game filenames
    if file_names & _GAME_FILENAMES:
        game_score += 3

    # Game directories
    if dir_names & _GAME_DIRNAMES:
        game_score += 3

    # Kiểm tra manga indicators
    manga_score = 0

    # Thư mục chứa >3 file ảnh
    if image_count > 3:
        manga_score += 3

    # PDF files
    if ".pdf" in extensions:
        manga_score += 2

    # Kiểm tra film indicators
    film_score = 0

    # Video files
    if video_count > 0:
        film_score += 3

    # Subtitle files
    if subtitle_count > 0:
        film_score += 2

    # Chọn loại có điểm cao nhất
    scores = {"game": game_score, "manga": manga_score, "film": film_score}
    best = max(scores, key=lambda k: scores[k])

    # Nếu không có indicator rõ ràng, mặc định là game
    if scores[best] == 0:
        return "game"

    return best


def get_file_info(path: str) -> Dict:
    """
    Lấy thông tin chi tiết về file hoặc thư mục.

    Args:
        path: Đường dẫn đến file hoặc thư mục.

    Returns:
        Dict chứa: name, path, type (file/dir), extension, size_bytes, size_human,
                   pipeline_type, exists.
    """
    p = Path(path)
    result = {
        "name": p.name,
        "path": str(p.resolve()),
        "exists": p.exists(),
    }

    if not p.exists():
        result.update({
            "type": "unknown",
            "extension": "",
            "size_bytes": 0,
            "size_human": "0 B",
            "pipeline_type": "unknown",
        })
        return result

    if p.is_file():
        size = p.stat().st_size
        result.update({
            "type": "file",
            "extension": p.suffix.lower(),
            "size_bytes": size,
            "size_human": _format_size(size),
        })
    elif p.is_dir():
        # Đếm tổng kích thước thư mục
        total_size = 0
        file_count = 0
        for f in p.rglob("*"):
            if f.is_file():
                try:
                    total_size += f.stat().st_size
                    file_count += 1
                except (OSError, PermissionError):
                    pass
        result.update({
            "type": "dir",
            "extension": "",
            "size_bytes": total_size,
            "size_human": _format_size(total_size),
            "file_count": file_count,
        })
    else:
        result.update({
            "type": "other",
            "extension": "",
            "size_bytes": 0,
            "size_human": "0 B",
        })

    # Nhận diện pipeline
    try:
        result["pipeline_type"] = detect_pipeline(path)
    except FileNotFoundError:
        result["pipeline_type"] = "unknown"

    return result


def _format_size(size_bytes: int) -> str:
    """Chuyển đổi kích thước bytes sang dạng human-readable."""
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} B"
    return f"{size:.2f} {units[unit_index]}"
