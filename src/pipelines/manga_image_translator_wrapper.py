"""
Manga Image Translator Wrapper — Tích hợp manga-image-translator vào XiaoMimo.
Gọi trực tiếp manga_translator module để dịch manga/comic.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Thêm manga-image-translator vào Python path
MANGA_TRANSLATOR_PATH = Path(r"E:\DichGame\Tool\manga-image-translator")
if str(MANGA_TRANSLATOR_PATH) not in sys.path:
    sys.path.insert(0, str(MANGA_TRANSLATOR_PATH))

logger = logging.getLogger(__name__)


class MangaImageTranslatorWrapper:
    """
    Wrapper gọi manga-image-translator để dịch manga.
    Sử dụng MangaTranslatorLocal class để xử lý toàn bộ pipeline.
    """

    def __init__(
        self,
        target_lang: str = "vi",
        source_lang: str = "ja",
        detector: str = "default",
        ocr: str = "mocr",
        translator: str = "original",
        inpainter: str = "lama_mpe",
        colorizer: str = "none",
        device: str = "cuda",
    ):
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.detector = detector
        self.ocr = ocr
        self.translator = translator
        self.inpainter = inpainter
        self.colorizer = colorizer
        self.device = device
        self._translator = None

    def _init_translator(self):
        """Khởi tạo MangaTranslatorLocal."""
        if self._translator is not None:
            return

        try:
            from manga_translator.mode.local import MangaTranslatorLocal

            params = {
                "target_lang": self.target_lang,
                "source_lang": self.source_lang,
                "detector": self.detector,
                "ocr": self.ocr,
                "translator": self.translator,
                "inpainter": self.inpainter,
                "colorizer": self.colorizer,
                "device": self.device,
                "verbose": False,
                "ignore_errors": True,
                "skip_no_text": False,
                "use_mtpe": False,
                "save_text": False,
                "save_text_file": "",
                "pre_dict": "",
                "post_dict": "",
                "kernel_size": -1,
                "text_threshold": 0.5,
                "det_threshold": 0.3,
                "det_batch_size": 1,
                "ocr_batch_size": 1,
                "inpainting_size": 1024,
                "font_size_offset": 0,
                "font_size_minimum": 0,
                "manga2eng": False,
                "eng_font": "fonts/comic.ttf",
                "no_hybrid": False,
                "mask_dilation_offset": 0,
                "overwrite": True,
            }

            self._translator = MangaTranslatorLocal(params)
            logger.info("MangaTranslatorLocal initialized successfully")
        except ImportError as e:
            logger.error(f"Cannot import manga_translator: {e}")
            raise RuntimeError(
                f"manga-image-translator chưa được cài đặt. "
                f"Đảm bảo thư mục tồn tại: {MANGA_TRANSLATOR_PATH}"
            )

    async def translate_image(
        self,
        image_path: str,
        output_path: str = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Dịch một ảnh manga.

        Args:
            image_path: Đường dẫn ảnh nguồn
            output_path: Đường dẫn ảnh đích (nếu None, tự tạo)
            **kwargs: Các tham số override

        Returns:
            Dict chứa kết quả dịch
        """
        self._init_translator()

        image_path = Path(image_path)
        if not image_path.exists():
            return {"success": False, "error": f"Không tìm thấy ảnh: {image_path}"}

        if output_path is None:
            output_dir = image_path.parent / "translated"
            output_dir.mkdir(exist_ok=True)
            output_path = str(output_dir / f"translated_{image_path.name}")

        try:
            # Chuẩn bị params
            params = {
                "target_lang": kwargs.get("target_lang", self.target_lang),
                "source_lang": kwargs.get("source_lang", self.source_lang),
                "detector": kwargs.get("detector", self.detector),
                "ocr": kwargs.get("ocr", self.ocr),
                "translator": kwargs.get("translator", self.translator),
                "inpainter": kwargs.get("inpainter", self.inpainter),
                "colorizer": kwargs.get("colorizer", self.colorizer),
                "device": kwargs.get("device", self.device),
                "overwrite": True,
            }

            # Chạy translation
            await self._translator.translate_path(
                str(image_path),
                str(Path(output_path).parent),
                params,
            )

            # Tìm file output
            result_dir = Path(output_path).parent
            translated_files = list(result_dir.glob(f"*{image_path.stem}*"))
            if translated_files:
                actual_output = str(translated_files[0])
            else:
                actual_output = output_path

            return {
                "success": True,
                "input": str(image_path),
                "output": actual_output,
                "source_lang": self.source_lang,
                "target_lang": self.target_lang,
            }

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "success": False,
                "input": str(image_path),
                "error": str(e),
            }

    async def translate_batch(
        self,
        image_paths: List[str],
        output_dir: str = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Dịch batch nhiều ảnh manga.

        Args:
            image_paths: Danh sách đường dẫn ảnh
            output_dir: Thư mục output
            **kwargs: Các tham số override

        Returns:
            List kết quả dịch
        """
        self._init_translator()

        if output_dir is None:
            output_dir = str(Path(image_paths[0]).parent / "translated") if image_paths else "translated"

        os.makedirs(output_dir, exist_ok=True)

        results = []
        for i, img_path in enumerate(image_paths, 1):
            logger.info(f"Translating {i}/{len(image_paths)}: {img_path}")
            output_path = str(Path(output_dir) / f"translated_{Path(img_path).name}")
            result = await self.translate_image(img_path, output_path, **kwargs)
            results.append(result)

        return results

    async def translate_directory(
        self,
        input_dir: str,
        output_dir: str = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Dịch tất cả ảnh trong thư mục.

        Args:
            input_dir: Thư mục chứa ảnh
            output_dir: Thư mục output
            **kwargs: Các tham số override

        Returns:
            List kết quả dịch
        """
        input_path = Path(input_dir)
        if not input_path.is_dir():
            return [{"success": False, "error": f"Không tìm thấy thư mục: {input_dir}"}]

        # Tìm tất cả ảnh
        exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
        images = sorted([
            str(f) for f in input_path.iterdir()
            if f.suffix.lower() in exts
        ])

        if not images:
            return [{"success": False, "error": "Không tìm thấy ảnh nào"}]

        if output_dir is None:
            output_dir = str(input_path / "translated")

        return await self.translate_batch(images, output_dir, **kwargs)


# Singleton instance
_wrapper_instance: Optional[MangaImageTranslatorWrapper] = None


def get_manga_translator_wrapper(
    target_lang: str = "vi",
    source_lang: str = "ja",
    **kwargs,
) -> MangaImageTranslatorWrapper:
    """Lấy singleton wrapper instance."""
    global _wrapper_instance
    if _wrapper_instance is None:
        _wrapper_instance = MangaImageTranslatorWrapper(
            target_lang=target_lang,
            source_lang=source_lang,
            **kwargs,
        )
    return _wrapper_instance


async def translate_manga_image(
    image_path: str,
    output_path: str = None,
    target_lang: str = "vi",
    source_lang: str = "ja",
) -> Dict[str, Any]:
    """Hàm convenience để dịch một ảnh manga."""
    wrapper = get_manga_translator_wrapper(target_lang, source_lang)
    return await wrapper.translate_image(image_path, output_path)


async def translate_manga_directory(
    input_dir: str,
    output_dir: str = None,
    target_lang: str = "vi",
    source_lang: str = "ja",
) -> List[Dict[str, Any]]:
    """Hàm convenience để dịch tất cả ảnh trong thư mục."""
    wrapper = get_manga_translator_wrapper(target_lang, source_lang)
    return await wrapper.translate_directory(input_dir, output_dir)