# -*- coding: utf-8 -*-
"""
Subtitle - Tiện ích xử lý phụ đề (subtitle).
Hỗ trợ đọc/ghi ASS, SRT, VTT. Sử dụng thư viện pysubs2.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    import pysubs2
except ImportError:
    pysubs2 = None  # Sẽ báo lỗi khi sử dụng nếu chưa cài

# ============================================================================
# Regex để làm sạch tag ASS
# ============================================================================
_ASS_TAG_PATTERN = re.compile(r"\{\\[^}]*\}")  # {\b1}, {\i0}, {\pos(x,y)}, ...
_NEWLINE_TAG = re.compile(r"\\[Nn]")            # \N hoặc \n trong ASS


def load_subtitle(path: str) -> List[Dict]:
    """
    Đọc file phụ đề và trả về danh sách events.

    Args:
        path: Đường dẫn đến file phụ đề (.ass, .srt, .vtt, .sub, .ssa).

    Returns:
        Danh sách dict, mỗi dict có key: start_ms, end_ms, text.

    Raises:
        ImportError: Nếu chưa cài thư viện pysubs2.
        FileNotFoundError: Nếu file không tồn tại.
        ValueError: Nếu định dạng không được hỗ trợ.
    """
    _check_pysubs2()
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"File phụ đề không tồn tại: {path}")

    subs = pysubs2.load(str(p), encoding="utf-8")
    events = []

    for event in subs.events:
        # Bỏ qua comment và dòng trống
        if event.is_comment:
            continue
        text = event.text.strip()
        if not text:
            continue

        events.append({
            "start_ms": event.start,
            "end_ms": event.end,
            "text": text,
        })

    return events


def save_subtitle(
    events: List[Dict],
    path: str,
    format: str = "ass",
) -> None:
    """
    Lưu danh sách events ra file phụ đề.

    Args:
        events: Danh sách dict với key: start_ms, end_ms, text.
        path: Đường dẫn file đầu ra.
        format: Định dạng đầu ra — "ass", "srt", hoặc "vtt". Mặc định "ass".
    """
    _check_pysubs2()

    subs = pysubs2.SSAFile()

    for ev in events:
        event = pysubs2.SSAEvent(
            start=ev["start_ms"],
            end=ev["end_ms"],
            text=ev["text"],
        )
        subs.events.append(event)

    # Tự tạo thư mục cha nếu chưa có
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    subs.save(path, encoding="utf-8", format_=format)


def clean_subtitle_text(text: str) -> str:
    """Làm sạch văn bản phụ đề: loại bỏ tag ASS và ký tự đặc biệt."""
    # Loại bỏ tag ASS {...}
    cleaned = _ASS_TAG_PATTERN.sub("", text)

    # Thay thế \N, \n bằng khoảng trắng
    cleaned = _NEWLINE_TAG.sub(" ", cleaned)

    # Loại bỏ khoảng trắng thừa
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def merge_subtitle_tracks(tracks: List[List[Dict]]) -> List[Dict]:
    """
    Gộp nhiều track phụ đề thành một track duy nhất, sắp xếp theo thời gian.

    Args:
        tracks: Danh sách các track, mỗi track là List[Dict] với key: start_ms, end_ms, text.

    Returns:
        Danh sách events đã gộp và sắp xếp theo start_ms.
    """
    merged = []

    for track in tracks:
        merged.extend(track)

    # Sắp xếp theo thời gian bắt đầu
    merged.sort(key=lambda ev: ev["start_ms"])

    return merged


def _check_pysubs2() -> None:
    """Kiểm tra thư viện pysubs2 đã được cài chưa."""
    if pysubs2 is None:
        raise ImportError(
            "Thư viện pysubs2 chưa được cài đặt. "
            "Cài đặt bằng lệnh: pip install pysubs2"
        )
