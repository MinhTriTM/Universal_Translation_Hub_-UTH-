# -*- coding: utf-8 -*-
"""
Package memory - Bộ nhớ đệm dịch thuật.
Cung cấp TranslationMemory để cache kết quả dịch thuật qua SQLite.
"""

from .translation_memory import TranslationMemory

__all__ = ["TranslationMemory"]
