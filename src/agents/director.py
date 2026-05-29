"""
DirectorAgent - Agent điều phối trung tâm (orchestrator).
Tự động phát hiện loại pipeline phù hợp và dispatch đến agent tương ứng.
"""

from typing import Any, Dict, List, Optional

from .base import BaseAgent


class DirectorAgent(BaseAgent):
    """
    Agent điều phối: nhận task, phát hiện pipeline type,
    dispatch đến các agent phù hợp và tổng hợp kết quả.
    """

    def __init__(
        self,
        provider: Any = None,
        memory: Any = None,
        translator: Any = None,
        ocr_agent: Any = None,
        tts_agent: Any = None,
        qa_agent: Any = None,
    ):
        """
        Khởi tạo DirectorAgent với các sub-agent.

        Args:
            provider: TranslationProvider instance
            memory: TranslationMemory instance
            translator: TranslatorAgent instance
            ocr_agent: OCRAgent instance
            tts_agent: TTSAgent instance
            qa_agent: QAAgent instance
        """
        super().__init__(name="DirectorAgent", provider=provider, memory=memory)
        self.translator = translator
        self.ocr_agent = ocr_agent
        self.tts_agent = tts_agent
        self.qa_agent = qa_agent
        self._step_counter: int = 0

    def _next_step(self, description: str) -> int:
        """Tăng bộ đếm bước và log tiến trình."""
        self._step_counter += 1
        self.log(f"Bước {self._step_counter}: {description}")
        return self._step_counter

    def _reset_steps(self) -> None:
        """Reset bộ đếm bước về 0."""
        self._step_counter = 0

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Điều phối pipeline dịch thuật.

        Args:
            task: Dict chứa:
                - pipeline_type: str - loại pipeline ("text", "manga", "subtitle", "game")
                - source_lang: str - ngôn ngữ nguồn
                - target_lang: str - ngôn ngữ đích
                - texts: List[str] - danh sách văn bản cần dịch (cho text pipeline)
                - images: List[str] - danh sách đường dẫn ảnh (cho manga pipeline)
                - subtitle_path: str - đường dẫn file phụ đề (cho subtitle pipeline)
                - enable_tts: bool - có tạo audio TTS không (mặc định False)
                - enable_qa: bool - có kiểm tra chất lượng không (mặc định True)

        Returns:
            Dict chứa kết quả tổng hợp:
                - success: bool
                - pipeline_type: str
                - translations: List[Dict]
                - qa_results: List[Dict] (nếu enable_qa)
                - tts_results: List[Dict] (nếu enable_tts)
                - stats: Dict thống kê
        """
        self._reset_steps()
        pipeline_type = task.get("pipeline_type", "text")
        self.log(f"=== Bắt đầu pipeline: {pipeline_type} ===")

        try:
            # Bước 1: Phát hiện pipeline nếu chưa chỉ định
            if pipeline_type == "auto":
                pipeline_type = self._detect_pipeline(task)
                self._next_step(f"Tự động phát hiện pipeline: {pipeline_type}")

            # Bước 2: Dispatch đến pipeline phù hợp
            result: Dict[str, Any]
            if pipeline_type == "text":
                result = await self._pipeline_text(task)
            elif pipeline_type == "manga":
                result = await self._pipeline_manga(task)
            elif pipeline_type == "subtitle":
                result = await self._pipeline_subtitle(task)
            elif pipeline_type == "game":
                result = await self._pipeline_game(task)
            else:
                result = {
                    "success": False,
                    "error": f"Loại pipeline không hỗ trợ: {pipeline_type}",
                }

            result["pipeline_type"] = pipeline_type
            self.log(f"=== Hoàn thành pipeline: {pipeline_type} ===")
            return result

        except Exception as e:
            self.log(f"LỖI: {e}")
            return {
                "success": False,
                "pipeline_type": pipeline_type,
                "error": str(e),
            }

    def _detect_pipeline(self, task: Dict[str, Any]) -> str:
        """
        Phát hiện loại pipeline dựa trên nội dung task.

        Ưu tiên: images → subtitle_path → texts → game
        """
        # Thử import detect_pipeline từ utils
        try:
            from ..utils.file_detector import detect_pipeline
            return detect_pipeline(task)
        except ImportError:
            self.log("file_detector không khả dụng, dùng heuristic đơn giản")

        if task.get("images"):
            return "manga"
        if task.get("subtitle_path"):
            return "subtitle"
        if task.get("texts"):
            return "text"
        return "text"  # mặc định

    async def _pipeline_text(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Pipeline dịch văn bản thuần túy."""
        texts: List[str] = task.get("texts", [])
        source_lang: str = task.get("source_lang", "ja")
        target_lang: str = task.get("target_lang", "vi")
        enable_qa: bool = task.get("enable_qa", True)
        enable_tts: bool = task.get("enable_tts", False)

        if not texts:
            return {"success": False, "error": "Không có văn bản để dịch"}

        # Dịch thuật
        self._next_step(f"Dịch {len(texts)} văn bản ({source_lang} → {target_lang})")
        translation_result = await self.translator.execute({
            "texts": texts,
            "source_lang": source_lang,
            "target_lang": target_lang,
        })

        translations = translation_result.get("translations", [])
        result: Dict[str, Any] = {
            "success": True,
            "translations": translations,
            "stats": {
                "total": len(texts),
                "cache_hits": translation_result.get("cache_hits", 0),
                "api_calls": translation_result.get("api_calls", 0),
            },
        }

        # Kiểm tra chất lượng
        if enable_qa and self.qa_agent and translations:
            self._next_step("Kiểm tra chất lượng bản dịch")
            qa_results = []
            for item in translations:
                qa = await self.qa_agent.execute({
                    "original": item.get("original", ""),
                    "translated": item.get("translated", ""),
                    "source_lang": source_lang,
                })
                qa_results.append(qa)
            result["qa_results"] = qa_results
            result["stats"]["qa_passed"] = sum(
                1 for q in qa_results if q.get("passed")
            )

        # Tạo audio TTS
        if enable_tts and self.tts_agent and translations:
            self._next_step("Tạo audio TTS cho bản dịch")
            translated_texts = [t.get("translated", "") for t in translations]
            tts_result = await self.tts_agent.generate_audio_batch(
                translated_texts,
                output_dir=task.get("tts_output_dir", "./tts_output"),
            )
            result["tts_results"] = tts_result

        return result

    async def _pipeline_manga(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Pipeline dịch manga: OCR ảnh → dịch → (tùy chọn) TTS."""
        images: List[str] = task.get("images", [])
        source_lang: str = task.get("source_lang", "ja")
        target_lang: str = task.get("target_lang", "vi")

        if not images:
            return {"success": False, "error": "Không có ảnh manga để xử lý"}

        # OCR
        self._next_step(f"OCR {len(images)} ảnh manga")
        if not self.ocr_agent:
            return {"success": False, "error": "OCRAgent chưa được cấu hình"}

        ocr_result = await self.ocr_agent.execute({
            "type": "manga",
            "images": images,
        })
        texts = [item.get("text", "") for item in ocr_result.get("texts", [])]

        if not texts:
            return {"success": True, "translations": [], "stats": {"total": 0}}

        # Dịch
        self._next_step(f"Dịch {len(texts)} đoạn text từ manga")
        translation_result = await self.translator.execute({
            "texts": texts,
            "source_lang": source_lang,
            "target_lang": target_lang,
        })

        return {
            "success": True,
            "ocr_texts": ocr_result.get("texts", []),
            "translations": translation_result.get("translations", []),
            "stats": {
                "total_images": len(images),
                "total_texts": len(texts),
                "cache_hits": translation_result.get("cache_hits", 0),
                "api_calls": translation_result.get("api_calls", 0),
            },
        }

    async def _pipeline_subtitle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Pipeline dịch phụ đề: load ASS/SRT → dịch → ghi file mới."""
        subtitle_path: str = task.get("subtitle_path", "")
        source_lang: str = task.get("source_lang", "ja")
        target_lang: str = task.get("target_lang", "vi")

        if not subtitle_path:
            return {"success": False, "error": "Không có đường dẫn file phụ đề"}

        # OCR / Load phụ đề
        self._next_step(f"Load phụ đề từ: {subtitle_path}")
        if not self.ocr_agent:
            return {"success": False, "error": "OCRAgent chưa được cấu hình"}

        ocr_result = await self.ocr_agent.execute({
            "type": "subtitle",
            "subtitle_path": subtitle_path,
        })
        texts = [item.get("text", "") for item in ocr_result.get("texts", [])]

        if not texts:
            return {"success": True, "translations": [], "stats": {"total": 0}}

        # Dịch
        self._next_step(f"Dịch {len(texts)} dòng phụ đề")
        translation_result = await self.translator.execute({
            "texts": texts,
            "source_lang": source_lang,
            "target_lang": target_lang,
        })

        return {
            "success": True,
            "subtitle_entries": ocr_result.get("texts", []),
            "translations": translation_result.get("translations", []),
            "stats": {
                "total_entries": len(texts),
                "cache_hits": translation_result.get("cache_hits", 0),
                "api_calls": translation_result.get("api_calls", 0),
            },
        }

    async def _pipeline_game(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pipeline dịch game: nhận danh sách text đã extract,
        dịch, và trả về để inject lại.
        """
        texts: List[str] = task.get("texts", [])
        source_lang: str = task.get("source_lang", "ja")
        target_lang: str = task.get("target_lang", "vi")
        enable_qa: bool = task.get("enable_qa", True)

        if not texts:
            return {"success": False, "error": "Không có text game để dịch"}

        # Dịch
        self._next_step(f"Dịch {len(texts)} dòng text game ({source_lang} → {target_lang})")
        translation_result = await self.translator.execute({
            "texts": texts,
            "source_lang": source_lang,
            "target_lang": target_lang,
        })

        translations = translation_result.get("translations", [])
        result: Dict[str, Any] = {
            "success": True,
            "translations": translations,
            "stats": {
                "total": len(texts),
                "cache_hits": translation_result.get("cache_hits", 0),
                "api_calls": translation_result.get("api_calls", 0),
            },
        }

        # QA đặc biệt cho game: kiểm tra format code
        if enable_qa and self.qa_agent and translations:
            self._next_step("Kiểm tra chất lượng (focus: format code game)")
            qa_results = []
            for item in translations:
                qa = await self.qa_agent.execute({
                    "original": item.get("original", ""),
                    "translated": item.get("translated", ""),
                    "source_lang": source_lang,
                })
                qa_results.append(qa)
            result["qa_results"] = qa_results
            result["stats"]["qa_passed"] = sum(
                1 for q in qa_results if q.get("passed")
            )

        return result
