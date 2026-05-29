"""
TranslatorAgent - Agent dịch thuật với Translation Memory cache.
Kiểm tra TM cache trước, chỉ gọi API cho các text chưa có trong cache.
"""

from typing import Any, Dict, List, Optional

from .base import BaseAgent


class TranslatorAgent(BaseAgent):
    """
    Agent dịch thuật: kết hợp provider (API) và Translation Memory (cache).
    Tối ưu số lần gọi API bằng cách ưu tiên cache.
    """

    def __init__(
        self,
        provider: Any = None,
        memory: Any = None,
    ):
        """
        Khởi tạo TranslatorAgent.

        Args:
            provider: TranslationProvider instance (OpenAI, Gemini, DeepSeek...)
            memory: TranslationMemory instance (SQLite TM cache)
        """
        super().__init__(name="TranslatorAgent", provider=provider, memory=memory)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dịch danh sách văn bản với TM cache.

        Args:
            task: Dict chứa:
                - texts: List[str] - danh sách văn bản cần dịch
                - source_lang: str - ngôn ngữ nguồn (ví dụ: "ja", "en")
                - target_lang: str - ngôn ngữ đích (ví dụ: "vi")

        Returns:
            Dict chứa:
                - translations: List[Dict] - mỗi dict có "original", "translated", "source"
                - cache_hits: int - số text lấy từ cache
                - api_calls: int - số lần gọi API
        """
        texts: List[str] = task.get("texts", [])
        source_lang: str = task.get("source_lang", "ja")
        target_lang: str = task.get("target_lang", "vi")

        if not texts:
            return {"translations": [], "cache_hits": 0, "api_calls": 0}

        self.log(f"Bắt đầu dịch {len(texts)} văn bản ({source_lang} → {target_lang})")

        translations: List[Dict[str, str]] = []
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []
        cache_hits: int = 0

        # Bước 1: Kiểm tra TM cache cho từng text
        for i, text in enumerate(texts):
            cached = self._check_cache(text, source_lang, target_lang)
            if cached is not None:
                translations.append({
                    "original": text,
                    "translated": cached,
                    "source": "cache",
                })
                cache_hits += 1
            else:
                # Giữ chỗ, sẽ điền sau
                translations.append({
                    "original": text,
                    "translated": "",
                    "source": "api",
                })
                uncached_indices.append(i)
                uncached_texts.append(text)

        if cache_hits > 0:
            self.log(f"Cache hit: {cache_hits}/{len(texts)}")

        # Bước 2: Gọi API cho các text chưa có trong cache
        api_calls: int = 0
        if uncached_texts:
            self.log(f"Gọi API dịch {len(uncached_texts)} văn bản...")
            try:
                api_translations = await self._call_provider(
                    uncached_texts, source_lang, target_lang
                )
                api_calls = 1  # coi như 1 batch call

                # Điền kết quả vào đúng vị trí
                for idx, translated_text in zip(uncached_indices, api_translations):
                    translations[idx]["translated"] = translated_text

                # Lưu vào TM cache
                self._save_to_cache(uncached_texts, api_translations, source_lang, target_lang)

            except Exception as e:
                self.log(f"LỖI khi gọi API: {e}")
                # Đánh dấu các text dịch lỗi
                for idx in uncached_indices:
                    translations[idx]["translated"] = f"[LỖI DỊCH: {e}]"
                    translations[idx]["source"] = "error"

        self.log(
            f"Hoàn thành: {len(texts)} text | "
            f"cache={cache_hits} | api={len(uncached_texts)}"
        )

        return {
            "translations": translations,
            "cache_hits": cache_hits,
            "api_calls": api_calls,
        }

    def _check_cache(
        self, text: str, source_lang: str, target_lang: str
    ) -> Optional[str]:
        """
        Kiểm tra Translation Memory cache.

        Args:
            text: Văn bản gốc
            source_lang: Ngôn ngữ nguồn
            target_lang: Ngôn ngữ đích

        Returns:
            Bản dịch nếu tìm thấy trong cache, None nếu không có
        """
        if self.memory is None:
            return None

        try:
            result = self.memory.lookup(text, source_lang, target_lang)
            return result
        except Exception:
            return None

    def _save_to_cache(
        self,
        originals: List[str],
        translations: List[str],
        source_lang: str,
        target_lang: str,
    ) -> None:
        """
        Lưu các cặp gốc-dịch vào Translation Memory.

        Args:
            originals: Danh sách văn bản gốc
            translations: Danh sách bản dịch
            source_lang: Ngôn ngữ nguồn
            target_lang: Ngôn ngữ đích
        """
        if self.memory is None:
            return

        for original, translated in zip(originals, translations):
            if translated and not translated.startswith("[LỖI"):
                try:
                    self.memory.save(original, translated, source_lang, target_lang)
                except Exception as e:
                    self.log(f"Không thể lưu TM: {e}")

    async def _call_provider(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str,
    ) -> List[str]:
        """
        Gọi TranslationProvider để dịch danh sách văn bản.

        Args:
            texts: Danh sách văn bản cần dịch
            source_lang: Ngôn ngữ nguồn
            target_lang: Ngôn ngữ đích

        Returns:
            Danh sách bản dịch tương ứng

        Raises:
            RuntimeError: Nếu provider chưa cấu hình
            Exception: Nếu API gọi thất bại
        """
        if self.provider is None:
            raise RuntimeError(
                "TranslationProvider chưa được cấu hình. "
                "Hãy truyền provider vào TranslatorAgent."
            )

        # Giả sử provider có phương thức translate_batch(texts, source, target)
        # hoặc translate(text, source, target) cho từng text
        if hasattr(self.provider, "translate_batch"):
            return await self.provider.translate_batch(texts, source_lang, target_lang)
        elif hasattr(self.provider, "translate"):
            results = []
            for text in texts:
                translated = await self.provider.translate(text, source_lang, target_lang)
                results.append(translated)
            return results
        else:
            raise RuntimeError(
                "Provider không có phương thức translate() hoặc translate_batch()."
            )
