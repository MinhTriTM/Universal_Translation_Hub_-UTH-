"""
OCRAgent - Agent OCR cho manga và phụ đề phim.
- Manga: dùng manga_ocr library (offline, nhanh) hoặc fallback sang MiMo API OCR
- Subtitle: dùng pysubs2 để load file ASS/SRT
"""

import os
from typing import Any, Dict, List, Optional

from .base import BaseAgent


class OCRAgent(BaseAgent):
    """
    Agent OCR trích xuất text từ ảnh manga hoặc file phụ đề.
    """

    # Cache kiểm tra manga_ocr availability
    _manga_ocr_available: Optional[bool] = None

    def __init__(
        self,
        provider: Any = None,
        memory: Any = None,
    ):
        super().__init__(name="OCRAgent", provider=provider, memory=memory)

    @classmethod
    def is_available(cls) -> bool:
        """
        Kiểm tra manga_ocr đã được cài đặt chưa.

        Returns:
            True nếu manga_ocr khả dụng, False nếu không
        """
        if cls._manga_ocr_available is not None:
            return cls._manga_ocr_available

        try:
            import manga_ocr  # noqa: F401
            cls._manga_ocr_available = True
        except ImportError:
            cls._manga_ocr_available = False

        return cls._manga_ocr_available

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực thi OCR dựa trên loại task.

        Args:
            task: Dict chứa:
                - type: "manga" | "subtitle"
                - images: List[str] — danh sách đường dẫn ảnh (khi type=manga)
                - subtitle_path: str — đường dẫn file phụ đề (klu type=subtitle)

        Returns:
            Dict chứa:
                - texts: List[Dict] — mỗi dict có "text", và tùy loại:
                    - manga: "image_path", "confidence"
                    - subtitle: "start", "end", "index"
        """
        task_type: str = task.get("type", "manga")

        if task_type == "manga":
            return await self._ocr_manga(task)
        elif task_type == "subtitle":
            return await self._load_subtitle(task)
        else:
            return {"texts": [], "error": f"Loại OCR không hỗ trợ: {task_type}"}

    async def _ocr_manga(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        OCR ảnh manga.
        Ưu tiên manga_ocr (offline), fallback sang MiMo API OCR.

        Args:
            task: Dict chứa "images": List[str]

        Returns:
            Dict với "texts": List[Dict] chứa text và vị trí
        """
        images: List[str] = task.get("images", [])
        if not images:
            return {"texts": [], "error": "Không có ảnh để OCR"}

        self.log(f"OCR {len(images)} ảnh manga")

        # Thử manga_ocr trước
        if self.is_available():
            return await self._ocr_manga_ocr(images)

        # Fallback: MiMo API OCR
        self.log("manga_ocr không khả dụng, dùng MiMo API OCR")
        return await self._ocr_mimo_api(images)

    async def _ocr_manga_ocr(self, images: List[str]) -> Dict[str, Any]:
        """
        Dùng manga_ocr library để OCR offline.
        Library này chuyên cho manga tiếng Nhật.

        Args:
            images: Danh sách đường dẫn ảnh

        Returns:
            Dict với "texts" chứa kết quả OCR
        """
        try:
            from manga_ocr import MangaOcr
            from PIL import Image

            self.log("Khởi tạo manga_ocr model...")
            mocr = MangaOcr()

            results: List[Dict[str, Any]] = []
            for img_path in images:
                if not os.path.exists(img_path):
                    self.log(f"Bỏ qua file không tồn tại: {img_path}")
                    continue

                try:
                    img = Image.open(img_path)
                    text = mocr(img)
                    results.append({
                        "text": text.strip(),
                        "image_path": img_path,
                        "confidence": 1.0,  # manga_ocr không trả confidence
                        "source": "manga_ocr",
                    })
                    self.log(f"OCR OK: {img_path} → {text[:50]}...")
                except Exception as e:
                    self.log(f"Lỗi OCR {img_path}: {e}")
                    results.append({
                        "text": "",
                        "image_path": img_path,
                        "confidence": 0.0,
                        "error": str(e),
                        "source": "manga_ocr",
                    })

            return {"texts": results}

        except Exception as e:
            self.log(f"Lỗi khởi tạo manga_ocr: {e}")
            return {"texts": [], "error": str(e)}

    async def _ocr_mimo_api(self, images: List[str]) -> Dict[str, Any]:
        """
        Fallback OCR qua MiMo API (khi manga_ocr không khả dụng).
        Gửi ảnh đến provider có hỗ trợ vision/OCR.

        Args:
            images: Danh sách đường dẫn ảnh

        Returns:
            Dict với "texts" chứa kết quả OCR
        """
        if not self.provider:
            return {
                "texts": [],
                "error": "Không có provider cho MiMo API OCR",
            }

        results: List[Dict[str, Any]] = []
        for img_path in images:
            if not os.path.exists(img_path):
                self.log(f"Bỏ qua file không tồn tại: {img_path}")
                continue

            try:
                # Giả sử provider có phương thức ocr_image(path)
                # hoặc vision_analyze(image_path, prompt)
                if hasattr(self.provider, "ocr_image"):
                    text = await self.provider.ocr_image(img_path)
                elif hasattr(self.provider, "vision_analyze"):
                    text = await self.provider.vision_analyze(
                        img_path, prompt="Extract all text from this manga image"
                    )
                else:
                    text = "[Provider không hỗ trợ OCR]"

                results.append({
                    "text": text.strip() if isinstance(text, str) else str(text),
                    "image_path": img_path,
                    "confidence": 0.8,  # API OCR ước lượng
                    "source": "mimo_api",
                })
                self.log(f"API OCR OK: {img_path}")

            except Exception as e:
                self.log(f"Lỗi API OCR {img_path}: {e}")
                results.append({
                    "text": "",
                    "image_path": img_path,
                    "confidence": 0.0,
                    "error": str(e),
                    "source": "mimo_api",
                })

        return {"texts": results}

    async def _load_subtitle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load file phụ đề ASS/SRT bằng pysubs2.

        Args:
            task: Dict chứa "subtitle_path": str

        Returns:
            Dict với "texts" chứa danh sách dòng phụ đề
        """
        subtitle_path: str = task.get("subtitle_path", "")
        if not subtitle_path:
            return {"texts": [], "error": "Không có đường dẫn file phụ đề"}

        if not os.path.exists(subtitle_path):
            return {"texts": [], "error": f"File không tồn tại: {subtitle_path}"}

        try:
            import pysubs2

            self.log(f"Load phụ đề: {subtitle_path}")
            subs = pysubs2.load(subtitle_path)

            results: List[Dict[str, Any]] = []
            for i, line in enumerate(subs.events):
                if line.is_comment:
                    continue
                results.append({
                    "text": line.text.replace("\\N", "\n").strip(),
                    "start": line.start,  # milliseconds
                    "end": line.end,
                    "index": i,
                    "source": "subtitle",
                })

            self.log(f"Load được {len(results)} dòng phụ đề")
            return {"texts": results}

        except ImportError:
            return {
                "texts": [],
                "error": "pysubs2 chưa cài đặt. Chạy: pip install pysubs2",
            }
        except Exception as e:
            return {"texts": [], "error": f"Lỗi load phụ đề: {e}"}
