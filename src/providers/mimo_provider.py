"""
MiMo Provider - Gọi Xiaomi MiMo API qua Anthropic-compatible endpoint.
Endpoint: https://token-plan-sgp.xiaomimimo.com/anthropic
Format: Anthropic Messages API (x-api-key header, /v1/messages)
"""
from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

import httpx

from .base import TranslationProvider

logger = logging.getLogger(__name__)

# Models MiMo hỗ trợ
MIMO_MODELS = {
    "mimo-v2.5-pro": "Pro — reasoning mạnh nhất",
    "mimo-v2.5": "Standard — nhanh, đa năng",
    "mimo-v2-pro": "V2 Pro — thế hệ trước",
    "mimo-v2.5-omni": "Omni — đa modal (text+image+audio)",
    "mimo-v2.5-tts": "TTS — text-to-speech",
    "mimo-v2.5-tts-voiceclone": "TTS Voice Clone",
    "mimo-v2.5-tts-voicedesign": "TTS Voice Design",
    "mimo-v2-tts": "TTS V2 — legacy",
}

DEFAULT_MODEL_MAP: Dict[str, str] = {
    "director": "mimo-v2.5-pro",
    "translator": "mimo-v2.5",
    "ocr": "mimo-v2.5",
    "qa": "mimo-v2.5",
    "tts": "mimo-v2.5-tts",
    "voice_clone": "mimo-v2.5-tts-voiceclone",
    "voice_design": "mimo-v2.5-tts-voicedesign",
}

ANTHROPIC_VERSION = "2023-06-01"


class MiMoProvider(TranslationProvider):
    """
    Provider gọi MiMo qua Anthropic-compatible endpoint.
    Auth: x-api-key header. Format: /v1/messages.
    Hỗ trợ extended thinking (thinking + text blocks).
    """

    def __init__(
        self,
        api_keys: Optional[List[str]] = None,
        base_url: str = "https://token-plan-sgp.xiaomimimo.com/anthropic",
        model_map: Optional[Dict[str, str]] = None,
        timeout: float = 60.0,
    ):
        if api_keys:
            self.api_keys = [k.strip() for k in api_keys if k.strip()]
        else:
            env_key = os.environ.get("MIMO_API_KEY", "")
            if env_key:
                self.api_keys = [k.strip() for k in env_key.split(",") if k.strip()]
            else:
                self.api_keys = []

        self.base_url = base_url.rstrip("/")
        self.model_map = model_map or DEFAULT_MODEL_MAP.copy()
        self.timeout = timeout
        self._key_index = 0

    def get_name(self) -> str:
        return "mimo"

    def is_available(self) -> bool:
        return bool(self.api_keys)

    def _next_key(self) -> str:
        if not self.api_keys:
            raise ValueError("Không có MiMo API key")
        key = self.api_keys[self._key_index % len(self.api_keys)]
        self._key_index += 1
        return key

    def _get_model(self, role: str = "translator") -> str:
        return self.model_map.get(role, "mimo-v2.5")

    def _build_headers(self, key: str) -> Dict[str, str]:
        return {
            "x-api-key": key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }

    def _extract_text(self, data: Dict) -> str:
        """Trích xuất text từ response, xử lý cả thinking + text blocks."""
        text_parts = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                text_parts.append(block["text"])
        return "\n".join(text_parts).strip()

    async def _call_api(self, model: str, messages: List[Dict], max_tokens: int = 1024, temperature: float = 0.3) -> Dict:
        """Gọi MiMo API qua Anthropic format."""
        key = self._next_key()
        url = f"{self.base_url}/v1/messages"
        headers = self._build_headers(key)
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def translate(self, text: str, source_lang: str = "auto", target_lang: str = "vi") -> str:
        if not text or not text.strip():
            return ""

        model = self._get_model("translator")
        if source_lang == "auto":
            lang_inst = f"Auto-detect source language, translate into {target_lang}."
        else:
            lang_inst = f"Translate from {source_lang} to {target_lang}."

        messages = [
            {"role": "user", "content": f"{lang_inst} Return ONLY the translated text, no explanations.\n\n{text}"}
        ]

        data = await self._call_api(model, messages, max_tokens=1024, temperature=0.3)
        result = self._extract_text(data)
        return result if result else text

    async def translate_batch(self, texts: List[str], source_lang: str = "auto", target_lang: str = "vi") -> List[str]:
        if not texts:
            return []

        results = []
        for i, text in enumerate(texts):
            try:
                translated = await self.translate(text, source_lang, target_lang)
                results.append(translated)
            except Exception as e:
                logger.warning("Lỗi dịch #%d: %s", i, e)
                results.append(text)
        return results

    async def chat(self, role: str, messages: List[Dict], temperature: float = 0.7) -> str:
        """Gọi MiMo chat (dùng cho agents)."""
        model = self._get_model(role)
        data = await self._call_api(model, messages, max_tokens=2048, temperature=temperature)
        return self._extract_text(data)

    async def chat_with_thinking(self, role: str, messages: List[Dict], temperature: float = 0.7) -> Dict:
        """Gọi MiMo chat, trả về cả thinking + text."""
        model = self._get_model(role)
        key = self._next_key()
        url = f"{self.base_url}/v1/messages"
        headers = self._build_headers(key)
        payload = {
            "model": model,
            "max_tokens": 4096,
            "temperature": temperature,
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        result = {"thinking": "", "text": "", "stop_reason": data.get("stop_reason", "")}
        for block in data.get("content", []):
            if block.get("type") == "thinking":
                result["thinking"] = block.get("thinking", "")
            elif block.get("type") == "text":
                result["text"] = block.get("text", "")
        return result

    def list_models(self) -> Dict[str, str]:
        return MIMO_MODELS.copy()
