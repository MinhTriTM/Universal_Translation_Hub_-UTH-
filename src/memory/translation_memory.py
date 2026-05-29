# -*- coding: utf-8 -*-
"""
TranslationMemory - Bộ nhớ đệm dịch thuật backed by SQLite.
Cache kết quả dịch thuật để tránh gọi lại API/provider cho cùng một câu.
"""

import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TranslationMemory:
    """
    Bộ nhớ đệm dịch thuật sử dụng SQLite.
    Thread-safe, hỗ trợ get/put/batch/export/import.
    """

    def __init__(self, db_path: str = "translation_memory.db") -> None:
        """
        Khởi tạo TranslationMemory.

        Args:
            db_path: Đường dẫn file SQLite database. Mặc định "translation_memory.db".
        """
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Lấy connection SQLite cho thread hiện tại (lazy init)."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self) -> None:
        """Tạo bảng translations nếu chưa tồn tại."""
        conn = self._get_conn()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_text TEXT NOT NULL,
                source_lang TEXT NOT NULL DEFAULT 'auto',
                target_lang TEXT NOT NULL DEFAULT 'vi',
                translated_text TEXT NOT NULL,
                provider TEXT NOT NULL DEFAULT 'unknown',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_text, source_lang, target_lang)
            )
            """
        )
        conn.commit()

    def get(
        self,
        source_text: str,
        source_lang: str = "auto",
        target_lang: str = "vi",
    ) -> Optional[str]:
        """
        Tra cứu bản dịch đã cache.

        Args:
            source_text: Văn bản gốc cần tra cứu.
            source_lang: Ngôn ngữ nguồn. Mặc định "auto".
            target_lang: Ngôn ngữ đích. Mặc định "vi".

        Returns:
            Bản dịch đã cache, hoặc None nếu chưa có.
        """
        conn = self._get_conn()
        row = conn.execute(
            """
            SELECT translated_text FROM translations
            WHERE source_text = ? AND source_lang = ? AND target_lang = ?
            """,
            (source_text, source_lang, target_lang),
        ).fetchone()
        return row["translated_text"] if row else None

    def put(
        self,
        source_text: str,
        translated_text: str,
        source_lang: str = "auto",
        target_lang: str = "vi",
        provider: str = "unknown",
    ) -> None:
        """
        Lưu bản dịch vào cache. Nếu đã tồn tại thì cập nhật (UPSERT).

        Args:
            source_text: Văn bản gốc.
            translated_text: Văn bản đã dịch.
            source_lang: Ngôn ngữ nguồn. Mặc định "auto".
            target_lang: Ngôn ngữ đích. Mặc định "vi".
            provider: Nhà cung cấp dịch (google, deepl, ai, ...). Mặc định "unknown".
        """
        conn = self._get_conn()
        conn.execute(
            """
            INSERT INTO translations (source_text, source_lang, target_lang, translated_text, provider, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_text, source_lang, target_lang)
            DO UPDATE SET
                translated_text = excluded.translated_text,
                provider = excluded.provider,
                created_at = excluded.created_at
            """,
            (
                source_text,
                source_lang,
                target_lang,
                translated_text,
                provider,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()

    def put_batch(self, items: List[Dict]) -> None:
        """
        Chèn hàng loạt bản dịch vào cache.

        Args:
            items: Danh sách dict, mỗi dict chứa các key:
                   source_text, translated_text, source_lang (opt), target_lang (opt), provider (opt)
        """
        if not items:
            return
        conn = self._get_conn()
        now = datetime.utcnow().isoformat()
        rows = []
        for item in items:
            rows.append(
                (
                    item["source_text"],
                    item.get("source_lang", "auto"),
                    item.get("target_lang", "vi"),
                    item["translated_text"],
                    item.get("provider", "unknown"),
                    now,
                )
            )
        conn.executemany(
            """
            INSERT INTO translations (source_text, source_lang, target_lang, translated_text, provider, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_text, source_lang, target_lang)
            DO UPDATE SET
                translated_text = excluded.translated_text,
                provider = excluded.provider,
                created_at = excluded.created_at
            """,
            rows,
        )
        conn.commit()

    def stats(self) -> Dict:
        """
        Thống kê bộ nhớ đệm.

        Returns:
            Dict chứa: total, by_language (dict), by_provider (dict).
        """
        conn = self._get_conn()

        # Tổng số entry
        total = conn.execute("SELECT COUNT(*) AS cnt FROM translations").fetchone()["cnt"]

        # Thống kê theo ngôn ngữ đích
        lang_rows = conn.execute(
            """
            SELECT target_lang, COUNT(*) AS cnt
            FROM translations
            GROUP BY target_lang
            ORDER BY cnt DESC
            """
        ).fetchall()
        by_language = {row["target_lang"]: row["cnt"] for row in lang_rows}

        # Thống kê theo provider
        provider_rows = conn.execute(
            """
            SELECT provider, COUNT(*) AS cnt
            FROM translations
            GROUP BY provider
            ORDER BY cnt DESC
            """
        ).fetchall()
        by_provider = {row["provider"]: row["cnt"] for row in provider_rows}

        return {
            "total": total,
            "by_language": by_language,
            "by_provider": by_provider,
        }

    def export_json(self, output_path: str) -> int:
        """
        Xuất toàn bộ cache ra file JSON.

        Args:
            output_path: Đường dẫn file JSON đầu ra.

        Returns:
            Số lượng entry đã xuất.
        """
        conn = self._get_conn()
        rows = conn.execute(
            """
            SELECT source_text, source_lang, target_lang, translated_text, provider, created_at
            FROM translations
            ORDER BY id
            """
        ).fetchall()

        data = [dict(row) for row in rows]

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return len(data)

    def import_json(self, input_path: str) -> int:
        """
        Nhập cache từ file JSON.

        Args:
            input_path: Đường dẫn file JSON đầu vào.

        Returns:
            Số lượng entry đã nhập.
        """
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("File JSON phải chứa một mảng các object.")

        self.put_batch(data)
        return len(data)

    def clear(self) -> int:
        """
        Xóa toàn bộ cache.

        Returns:
            Số lượng entry đã xóa.
        """
        conn = self._get_conn()
        count = conn.execute("SELECT COUNT(*) AS cnt FROM translations").fetchone()["cnt"]
        conn.execute("DELETE FROM translations")
        conn.commit()
        return count
