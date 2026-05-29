"""Manga/Comic Translation Pipeline — OCR + Translate + Render."""
import os
import re
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import BasePipeline, PipelineResult


class MangaPipeline(BasePipeline):
    """
    Pipeline dịch manga/comic:
    1. Scan ảnh trong thư mục
    2. OCR text (manga-ocr / MiMo API / manga-image-translator)
    3. Detect text regions (OpenCV)
    4. Translate
    5. Inpaint xóa text gốc
    6. Render text tiếng Việt

    Hỗ trợ 2 chế độ:
    - manga-image-translator: Pipeline hoàn chỉnh (detection, OCR, inpainting, rendering)
    - manual: Pipeline thủ công (manga-ocr + OpenCV + provider)
    """

    name = "manga"

    def __init__(self, provider=None, memory=None, use_manga_translator: bool = True):
        super().__init__(provider, memory)
        self._ocr_model = None
        self._use_manga_translator = use_manga_translator
        self._manga_translator_wrapper = None

    def _get_image_files(self, input_path: str) -> List[Path]:
        """Lấy danh sách ảnh từ thư mục hoặc PDF."""
        p = Path(input_path)
        exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
        if p.is_dir():
            files = [f for f in p.iterdir() if f.suffix.lower() in exts]
            files.sort()
            return files
        elif p.suffix.lower() == ".pdf":
            # Convert PDF pages to images
            return self._pdf_to_images(p)
        return []

    def _pdf_to_images(self, pdf_path: Path) -> List[Path]:
        """Convert PDF sang list ảnh (dùng Pillow/PdfImage)."""
        try:
            from pdf2image import convert_from_path
            output_dir = pdf_path.parent / f"{pdf_path.stem}_pages"
            output_dir.mkdir(exist_ok=True)
            images = convert_from_path(str(pdf_path), dpi=200)
            paths = []
            for i, img in enumerate(images):
                path = output_dir / f"page_{i+1:03d}.png"
                img.save(str(path))
                paths.append(path)
            return paths
        except ImportError:
            print("  [manga] Cần cài pdf2image: pip install pdf2image")
            return []

    def _load_ocr(self):
        """Lazy-load manga-ocr model."""
        if self._ocr_model is None:
            try:
                from manga_ocr import MangaOcr
                print("  [manga] Đang nạp manga-ocr model...")
                self._ocr_model = MangaOcr()
                print("  [manga] manga-ocr sẵn sàng")
            except ImportError:
                print("  [manga] manga-ocr chưa cài. Dùng MiMo API OCR fallback.")
                self._ocr_model = False
        return self._ocr_model

    async def _ocr_image(self, image_path: Path) -> List[Dict]:
        """OCR một ảnh manga, trả về list text regions."""
        ocr = self._load_ocr()

        if ocr and ocr is not False:
            # Dùng manga-ocr
            return await self._ocr_with_manga_ocr(image_path, ocr)
        elif self.provider and hasattr(self.provider, 'chat'):
            # Fallback: MiMo API OCR
            return await self._ocr_with_mimo(image_path)
        else:
            # Không có OCR, trả về rỗng
            print(f"  [manga] Không có OCR engine cho {image_path.name}")
            return []

    async def _ocr_with_manga_ocr(self, image_path: Path, ocr_model) -> List[Dict]:
        """OCR bằng manga-ocr library."""
        import cv2
        import numpy as np
        from PIL import Image

        img = cv2.imread(str(image_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect text regions bằng threshold + contour
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < 20 or h < 20:  # Quá nhỏ, bỏ qua
                continue
            if w > img.shape[1] * 0.8 or h > img.shape[0] * 0.8:  # Quá lớn, bỏ qua
                continue

            # Crop region
            roi = img[y:y+h, x:x+w]
            pil_img = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))

            # OCR
            try:
                text = ocr_model(pil_img)
                if text and text.strip():
                    regions.append({
                        "text": text.strip(),
                        "bbox": [x, y, w, h],
                        "confidence": 0.9
                    })
            except Exception:
                pass

        return regions

    async def _ocr_with_mimo(self, image_path: Path) -> List[Dict]:
        """OCR bằng MiMo API (fallback)."""
        # Placeholder — cần implement MiMo vision API
        return []

    def _detect_text_regions(self, image_path: Path) -> List[Dict]:
        """Detect text regions bằng OpenCV (không OCR, chỉ tìm vị trí)."""
        try:
            import cv2
            import numpy as np

            img = cv2.imread(str(image_path))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # MSER detector
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)

            boxes = []
            for region in regions:
                x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
                if w > 15 and h > 15 and w < img.shape[1] * 0.7:
                    boxes.append({"bbox": [x, y, w, h]})

            return boxes
        except ImportError:
            return []

    async def _translate_regions(self, regions: List[Dict], source_lang: str, target_lang: str) -> List[Dict]:
        """Dịch text trong các regions."""
        if not regions:
            return []

        texts = [r["text"] for r in regions]

        # Check TM cache
        translations = [None] * len(texts)
        uncached = []
        uncached_idx = []

        for i, text in enumerate(texts):
            cached = None
            if self.memory:
                cached = self.memory.get(text, source_lang, target_lang)
            if cached:
                translations[i] = cached
            else:
                uncached.append(text)
                uncached_idx.append(i)

        # Dịch uncached
        if uncached and self.provider:
            try:
                batch_result = await self.provider.translate_batch(uncached, source_lang, target_lang)
                for j, idx in enumerate(uncached_idx):
                    translated = batch_result[j] if j < len(batch_result) else uncached[j]
                    translations[idx] = translated
                    if self.memory:
                        self.memory.put(uncached[j], translated, source_lang, target_lang)
            except Exception as e:
                print(f"  [manga] Lỗi dịch: {e}")
                for j, idx in enumerate(uncached_idx):
                    translations[idx] = uncached[j]
        else:
            for j, idx in enumerate(uncached_idx):
                translations[idx] = uncached[j]

        # Gán translation vào regions
        for i, region in enumerate(regions):
            region["translated"] = translations[i] if translations[i] else region["text"]

        return regions

    def _render_translated(self, image_path: Path, regions: List[Dict], output_path: Path):
        """Inpaint text gốc + render text tiếng Việt lên ảnh."""
        try:
            import cv2
            import numpy as np
            from PIL import Image, ImageDraw, ImageFont

            img = cv2.imread(str(image_path))

            # Inpaint: xóa text gốc
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            for region in regions:
                x, y, w, h = region["bbox"]
                cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
            img = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

            # Convert sang PIL để vẽ text
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)

            # Load font tiếng Việt
            font_path = self._find_vietnamese_font()
            font_size = 16

            for region in regions:
                x, y, w, h = region["bbox"]
                text = region.get("translated", region["text"])

                # Auto font size
                font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

                # Wrap text
                wrapped = self._wrap_text(text, w, font, draw)
                draw.text((x + 2, y + 2), wrapped, fill="black", font=font)

            # Save
            img_pil.save(str(output_path))

        except ImportError:
            print(f"  [manga] Cần cài OpenCV + Pillow để render")

    def _find_vietnamese_font(self) -> Optional[str]:
        """Tìm font hỗ trợ tiếng Việt trên Windows."""
        candidates = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\times.ttf",
            r"C:\Windows\Fonts\verdana.ttf",
            r"C:\Windows\Fonts\tahoma.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def _wrap_text(self, text: str, max_width: int, font, draw) -> str:
        """Wrap text vừa với width."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return "\n".join(lines)

    async def _run_with_manga_translator(self, input_path: str, options: Dict[str, Any]) -> PipelineResult:
        """Chạy pipeline sử dụng manga-image-translator."""
        from .manga_image_translator_wrapper import get_manga_translator_wrapper

        opts = options or {}
        result = PipelineResult(pipeline="manga", input_path=input_path)
        source_lang = opts.get("source_lang", "ja")
        target_lang = opts.get("target_lang", "vi")
        output_dir = opts.get("output_dir", str(Path(input_path) / "translated"))

        os.makedirs(output_dir, exist_ok=True)
        result.output_path = output_dir

        try:
            # Khởi tạo wrapper
            wrapper = get_manga_translator_wrapper(
                target_lang=target_lang,
                source_lang=source_lang,
            )

            # Scan ảnh
            self.log("1/3", f"Scanning images in {input_path}")
            images = self._get_image_files(input_path)
            self.log("1/3", f"Found {len(images)} images")

            if not images:
                result.errors.append("Không tìm thấy ảnh nào")
                return result

            result.total_items = len(images)

            # Dịch batch
            self.log("2/3", f"Translating {len(images)} images with manga-image-translator...")
            image_paths = [str(img) for img in images]
            results = await wrapper.translate_batch(
                image_paths=image_paths,
                output_dir=output_dir,
                target_lang=target_lang,
                source_lang=source_lang,
            )

            # Đếm kết quả
            success_count = sum(1 for r in results if r.get("success"))
            result.translated_items = success_count
            result.success = success_count > 0

            self.log("3/3", f"Done: {success_count}/{len(results)} images translated")

            # Ghi nhận lỗi
            for r in results:
                if not r.get("success") and r.get("error"):
                    result.errors.append(r["error"])

        except Exception as e:
            result.errors.append(str(e))
            result.success = False

        return result

    async def _run_manual_pipeline(self, input_path: str, options: Dict[str, Any]) -> PipelineResult:
        """Chạy pipeline thủ công (manga-ocr + OpenCV + provider)."""
        opts = options or {}
        result = PipelineResult(pipeline="manga", input_path=input_path)
        source_lang = opts.get("source_lang", "ja")
        target_lang = opts.get("target_lang", "vi")
        output_dir = opts.get("output_dir", str(Path(input_path) / "translated"))

        os.makedirs(output_dir, exist_ok=True)
        result.output_path = output_dir

        try:
            # Step 1: Scan ảnh
            self.log("1/6", f"Scanning images in {input_path}")
            images = self._get_image_files(input_path)
            self.log("1/6", f"Found {len(images)} images")

            if not images:
                result.errors.append("Không tìm thấy ảnh nào")
                return result

            result.total_items = len(images)

            # Step 2-6: Xử lý từng ảnh
            for i, img_path in enumerate(images, 1):
                self.log("2/6", f"[{i}/{len(images)}] OCR: {img_path.name}")
                regions = await self._ocr_image(img_path)

                if not regions:
                    self.log("3/6", f"[{i}] Không detect được text")
                    continue

                self.log("3/6", f"[{i}] Found {len(regions)} text regions")
                self.log("4/6", f"[{i}] Translating...")
                regions = await self._translate_regions(regions, source_lang, target_lang)

                self.log("5/6", f"[{i}] Rendering...")
                output_path = Path(output_dir) / img_path.name
                self._render_translated(img_path, regions, output_path)
                result.translated_items += 1

            result.success = True

        except Exception as e:
            result.errors.append(str(e))
            result.success = False

        return result

    async def run(self, input_path: str, options: Dict[str, Any] = None) -> PipelineResult:
        """
        Chạy manga pipeline.
        Ưu tiên dùng manga-image-translator, fallback sang manual pipeline.
        """
        opts = options or {}
        use_manga_translator = opts.get("use_manga_translator", self._use_manga_translator)

        if use_manga_translator:
            try:
                self.log("MODE", "Using manga-image-translator pipeline")
                return await self._run_with_manga_translator(input_path, opts)
            except Exception as e:
                self.log("FALLBACK", f"manga-image-translator failed: {e}")
                self.log("FALLBACK", "Switching to manual pipeline...")

        self.log("MODE", "Using manual pipeline (manga-ocr + OpenCV)")
        return await self._run_manual_pipeline(input_path, opts)

    async def validate(self, result: PipelineResult) -> List[str]:
        errors = []
        if not result.success:
            errors.append("Pipeline không thành công")
        if result.total_items > 0 and result.translated_items == 0:
            errors.append("Không có ảnh nào được dịch")
        return errors
