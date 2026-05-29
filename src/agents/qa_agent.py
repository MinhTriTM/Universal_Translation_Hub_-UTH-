"""
QAAgent - Agent kiểm tra chất lượng bản dịch.
Kiểm tra: ký tự CJK残留, bản dịch rỗng, format code preservation, tỷ lệ độ dài.
"""

import re
from typing import Any, Dict, List

from .base import BaseAgent


class QAAgent(BaseAgent):
    """
    Agent QA kiểm tra chất lượng bản dịch game/manga.
    Trả về điểm số 0-1 và danh sách vấn đề phát hiện.
    """

    # Regex phát hiện ký tự CJK残留 trong bản dịch
    CJK_PATTERN = re.compile(r"[一-鿿぀-ゟ゠-ヿ가-힯]")

    # Các format code phổ biến trong game
    FORMAT_CODES = [
        r"\\[CNV]\[\d+\]",      # \C[n], \N[n], \V[n] — RPG Maker
        r"<br>",                 # HTML line break
        r"</?[^>]+>",            # HTML/XML tags
        r"\{[^}]+\}",           # Template variables {name}
        r"\\[nNrRtT]",          # Escape sequences
        r"%[sd%]",              # Printf-style placeholders
    ]

    # Compile tất cả format code patterns
    FORMAT_PATTERN = re.compile("|".join(FORMAT_CODES))

    # Ngưỡng tỷ lệ độ dài
    MAX_LENGTH_RATIO: float = 3.0
    MIN_LENGTH_RATIO: float = 0.3

    def __init__(
        self,
        provider: Any = None,
        memory: Any = None,
    ):
        super().__init__(name="QAAgent", provider=provider, memory=memory)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kiểm tra chất lượng một cặp original-translated.

        Args:
            task: Dict chứa:
                - original: str — văn bản gốc
                - translated: str — bản dịch
                - source_lang: str — ngôn ngữ nguồn (tùy chọn)

        Returns:
            Dict chứa:
                - passed: bool — True nếu đạt chất lượng
                - issues: List[str] — danh sách vấn đề phát hiện
                - score: float — điểm chất lượng 0.0-1.0 (1.0 = hoàn hảo)
        """
        original: str = task.get("original", "")
        translated: str = task.get("translated", "")
        source_lang: str = task.get("source_lang", "")

        issues: List[str] = []
        score: float = 1.0

        # Kiểm tra 1: Bản dịch rỗng
        if not translated or not translated.strip():
            issues.append("Bản dịch rỗng")
            return {"passed": False, "issues": issues, "score": 0.0}

        # Kiểm tra 2: Ký tự CJK残留
        # Chỉ kiểm tra nếu đích là tiếng Việt (không phải CJK)
        if not self._is_cjk_lang(source_lang):
            cjk_matches = self.CJK_PATTERN.findall(translated)
            if cjk_matches:
                unique_chars = set(cjk_matches)
                issues.append(
                    f"Phát hiện ký tự CJK残留: {''.join(unique_chars)} "
                    f"({len(cjk_matches)} ký tự)"
                )
                score -= 0.3

        # Kiểm tra 3: Format code preservation
        original_formats = set(self.FORMAT_PATTERN.findall(original))
        translated_formats = set(self.FORMAT_PATTERN.findall(translated))
        if original_formats:
            missing_formats = original_formats - translated_formats
            extra_formats = translated_formats - original_formats
            if missing_formats:
                issues.append(
                    f"Mất format code: {', '.join(missing_formats)}"
                )
                score -= 0.2
            if extra_formats:
                issues.append(
                    f"Thừa format code: {', '.join(extra_formats)}"
                )
                score -= 0.1

        # Kiểm tra 4: Tỷ lệ độ dài
        if original:
            ratio = len(translated) / len(original)
            if ratio > self.MAX_LENGTH_RATIO:
                issues.append(
                    f"Bản dịch quá dài: {ratio:.1f}x bản gốc "
                    f"(tối đa {self.MAX_LENGTH_RATIO}x)"
                )
                score -= 0.2
            elif ratio < self.MIN_LENGTH_RATIO:
                issues.append(
                    f"Bản dịch quá ngắn: {ratio:.2f}x bản gốc "
                    f"(tối thiểu {self.MIN_LENGTH_RATIO}x)"
                )
                score -= 0.2

        # Kiểm tra 5: Bản dịch giống hệt bản gốc (có thể chưa dịch)
        if original.strip() == translated.strip() and len(original.strip()) > 3:
            issues.append("Bản dịch giống hệt bản gốc (có thể chưa dịch)")
            score -= 0.3

        # Giới hạn score trong khoảng 0-1
        score = max(0.0, min(1.0, score))

        # passed nếu score >= 0.5 và không có issue nghiêm trọng
        passed = score >= 0.5 and "Bản dịch rỗng" not in issues

        return {
            "passed": passed,
            "issues": issues,
            "score": round(score, 2),
        }

    @staticmethod
    def _is_cjk_lang(lang: str) -> bool:
        """
        Kiểm tra ngôn ngữ có phải CJK (Trung/Nhật/Hàn) không.

        Args:
            lang: Mã ngôn ngữ (vi dụ: "ja", "zh", "ko", "en")

        Returns:
            True nếu là ngôn ngữ CJK
        """
        cjk_langs = {"ja", "zh", "ko", "zh-cn", "zh-tw", "ja-jp", "ko-kr"}
        return lang.lower() in cjk_langs
