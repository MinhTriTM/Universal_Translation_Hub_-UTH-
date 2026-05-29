"""
Local Provider - Gọi AG-Translator backend để dịch thuật.
Hỗ trợ engine hymt (HY MT) và dolphin (Dolphin GGUF).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from .base import TranslationProvider

logger = logging.getLogger(__name__)

# Timeout cho dịch thuật (giây) — model local có thể chậm
TRANSLATE_TIMEOUT = 120.0

# Timeout ngắn hơn cho status check / init
STATUS_TIMEOUT = 10.0


class LocalProvider(TranslationProvider):
    """
    Provider gọi AG-Translator backend (FastAPI server).
    Hỗ trợ nhiều engine: hymt, dolphin, v.v.
    """

    def __init__(
        self,
        backend_url: str = "http://localhost:5000",
        engine: str = "hymt",
    ):
        """
        Khởi tạo Local Provider.

        Args:
            backend_url: URL của AG-Translator backend
            engine: Tên engine dịch thuật ("hymt" hoặc "dolphin")
        """
        self.backend_url = backend_url.rstrip("/")
        self.engine = engine
        self._model_loaded: bool = False  # Cache trạng thái model

    def get_name(self) -> str:
        """Trả về tên provider."""
        return "local"

    def _translate_url(self) -> str:
        """URL endpoint dịch single text."""
        return f"{self.backend_url}/api/translate/{self.engine}"

    def _batch_url(self) -> str:
        """URL endpoint dịch batch."""
        return f"{self.backend_url}/api/translate/{self.engine}"

    def _status_url(self) -> str:
        """URL endpoint kiểm tra trạng thái model."""
        return f"{self.backend_url}/api/translate/{self.engine}/status"

    def _init_url(self) -> str:
        """URL endpoint khởi tạo model."""
        return f"{self.backend_url}/api/translate/{self.engine}/init"

    async def _check_model_loaded(self) -> bool:
        """
        Kiểm tra model đã được load lên GPU chưa.

        Returns:
            True nếu model đã loaded, False nếu chưa
        """
        try:
            async with httpx.AsyncClient(timeout=STATUS_TIMEOUT) as client:
                response = await client.get(self._status_url())
                response.raise_for_status()
                data = response.json()
                loaded = data.get("loaded", False)
                self._model_loaded = loaded
                return loaded
        except Exception as e:
            logger.warning("Không thể kiểm tra trạng thái model: %s", e)
            return False

    async def init_model(self) -> bool:
        """
        Gọi API khởi tạo/load model lên GPU.

        Returns:
            True nếu khởi tạo thành công, False nếu lỗi
        """
        try:
            logger.info("Đang khởi tạo model '%s'...", self.engine)
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self._init_url())
                response.raise_for_status()
                data = response.json()
                success = data.get("success", False)
                if success:
                    self._model_loaded = True
                    logger.info("Khởi tạo model '%s' thành công.", self.engine)
                else:
                    logger.warning(
                        "Khởi tạo model '%s' thất bại: %s",
                        self.engine,
                        data.get("error", "unknown"),
                    )
                return success
        except Exception as e:
            logger.error("Lỗi khởi tạo model '%s': %s", self.engine, e)
            return False

    async def _ensure_model_loaded(self) -> None:
        """
        Đảm bảo model đã được load trước khi dịch.
        Nếu chưa load → tự động gọi init_model().
        """
        if self._model_loaded:
            return

        loaded = await self._check_model_loaded()
        if not loaded:
            await self.init_model()

    def is_available(self) -> bool:
        """
        Kiểm tra local provider có sẵn sàng không.
        Chỉ cần backend_url được cấu hình — trạng thái model sẽ check lúc dùng.
        """
        return bool(self.backend_url)

    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "vi",
    ) -> str:
        """
        Dịch một đoạn text qua AG-Translator backend.

        Tự động init model nếu chưa load.

        Args:
            text: Văn bản cần dịch
            source_lang: Ngôn ngữ nguồn (hiện tại backend tự detect)
            target_lang: Ngôn ngữ đích

        Returns:
            Văn bản đã dịch

        Raises:
            ValueError: Nếu text rỗng
            httpx.HTTPStatusError: Nếu API trả lỗi
        """
        if not text or not text.strip():
            return ""

        # Tự động init model nếu chưa load
        await self._ensure_model_loaded()

        url = self._translate_url()
        payload: Dict[str, Any] = {"text": text}

        async with httpx.AsyncClient(timeout=TRANSLATE_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()
        translated = data.get("translated_text", text)
        return translated

    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "auto",
        target_lang: str = "vi",
    ) -> List[str]:
        """
        Dịch nhiều text cùng lúc qua batch endpoint.
        Backend nhận texts_dict dạng {"0": text0, "1": text1, ...}.

        Args:
            texts: Danh sách văn bản cần dịch
            source_lang: Ngôn ngữ nguồn
            target_lang: Ngôn ngữ đích

        Returns:
            Danh sách văn bản đã dịch (cùng thứ tự với input)
        """
        if not texts:
            return []

        # Tự động init model nếu chưa load
        await self._ensure_model_loaded()

        # Build texts_dict theo format backend yêu cầu
        texts_dict: Dict[str, str] = {str(i): text for i, text in enumerate(texts)}

        url = self._batch_url()
        payload: Dict[str, Any] = {"texts_dict": texts_dict}

        async with httpx.AsyncClient(timeout=TRANSLATE_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()
        # Backend trả về dict {"0": translated0, "1": translated1, ...}
        translated_dict = data.get("translated_texts", {})

        # Sắp xếp lại theo thứ tự ban đầu
        results: List[str] = []
        for i in range(len(texts)):
            key = str(i)
            results.append(translated_dict.get(key, texts[i]))

        return results
