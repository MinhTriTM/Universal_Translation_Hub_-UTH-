"""
Base provider - Abstract class cho tất cả translation providers.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class TranslationProvider(ABC):
    """
    Abstract base class cho translation provider.
    Mọi provider cụ thể phải kế thừa class này và implement tất cả abstract methods.
    """

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "vi",
    ) -> str:
        """
        Dịch một đoạn text.

        Args:
            text: Văn bản cần dịch
            source_lang: Ngôn ngữ nguồn (mặc định: "auto" = tự detect)
            target_lang: Ngôn ngữ đích (mặc định: "vi" = tiếng Việt)

        Returns:
            Văn bản đã dịch
        """
        ...

    @abstractmethod
    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "auto",
        target_lang: str = "vi",
    ) -> List[str]:
        """
        Dịch nhiều đoạn text cùng lúc.

        Args:
            texts: Danh sách văn bản cần dịch
            source_lang: Ngôn ngữ nguồn
            target_lang: Ngôn ngữ đích

        Returns:
            Danh sách văn bản đã dịch (cùng thứ tự với input)
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """
        Trả về tên hiển thị của provider.

        Returns:
            Tên provider (ví dụ: "mimo", "local")
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """
        Kiểm tra provider có sẵn sàng sử dụng ngay không.

        Returns:
            True nếu provider có thể dùng, False nếu không
        """
        ...
