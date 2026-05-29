"""
Universal Translation Hub - Providers Package.

Cung cấp factory function get_provider() và re-export tất cả provider classes.

Sử dụng:
    from src.providers import get_provider

    # Tự động chọn provider (ưu tiên MiMo, fallback local)
    provider = get_provider()
    result = await provider.translate("Hello world")

    # Chỉ định provider cụ thể
    provider = get_provider("mimo")
    provider = get_provider("local")
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from .base import TranslationProvider
from .local_provider import LocalProvider
from .mimo_provider import MiMoProvider

logger = logging.getLogger(__name__)

# Re-export tất cả provider classes
__all__ = [
    "TranslationProvider",
    "MiMoProvider",
    "LocalProvider",
    "get_provider",
]


def get_provider(name: str = "auto") -> TranslationProvider:
    """
    Factory function — trả về translation provider theo tên.

    Args:
        name: Tên provider
            - "mimo"  → MiMoProvider (Xiaomi MiMo API)
            - "local" → LocalProvider (AG-Translator backend)
            - "auto"  → ưu tiên MiMo nếu có API key, fallback LocalProvider

    Returns:
        Instance của TranslationProvider

    Raises:
        ValueError: Nếu tên provider không hợp lệ
    """
    name = name.strip().lower()

    if name == "mimo":
        return MiMoProvider()

    if name == "local":
        return LocalProvider()

    if name == "auto":
        # Thử MiMo trước — nếu có API key thì dùng
        mimo = MiMoProvider()
        if mimo.is_available():
            logger.info("Auto-select: MiMo provider (API key found)")
            return mimo

        # Fallback: Local provider
        logger.info("Auto-select: Local provider (no MiMo API key)")
        return LocalProvider()

    raise ValueError(
        f"Unknown provider: '{name}'. "
        f"Valid options: 'mimo', 'local', 'auto'"
    )
