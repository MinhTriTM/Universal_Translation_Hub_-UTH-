"""
TTSAgent - Agent Text-to-Speech.
Fallback chain: MiMo TTS (API) → edge-tts (free local).
Hỗ trợ giọng Việt Nam: HoaiMyNeural (nữ), NamMinhNeural (nam).
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

from .base import BaseAgent


class TTSAgent(BaseAgent):
    """Agent TTS tạo file audio từ văn bản."""

    VOICE_FEMALE: str = "vi-VN-HoaiMyNeural"
    VOICE_MALE: str = "vi-VN-NamMinhNeural"
    DEFAULT_VOICE: str = VOICE_FEMALE

    _edge_tts_available: Optional[bool] = None

    def __init__(
        self,
        provider: Any = None,
        memory: Any = None,
        default_voice: Optional[str] = None,
        tts_engine: str = "auto",
    ):
        """
        Args:
            tts_engine: "auto" (MiMo→edge), "mimo", "edge"
        """
        super().__init__(name="TTSAgent", provider=provider, memory=memory)
        self.default_voice = default_voice or self.DEFAULT_VOICE
        self.tts_engine = tts_engine

    @classmethod
    def is_edge_tts_available(cls) -> bool:
        if cls._edge_tts_available is not None:
            return cls._edge_tts_available
        try:
            import edge_tts
            cls._edge_tts_available = True
        except ImportError:
            cls._edge_tts_available = False
        return cls._edge_tts_available

    def is_mimo_tts_available(self) -> bool:
        """Kiểm tra provider có hỗ trợ TTS không."""
        return (
            self.provider is not None
            and hasattr(self.provider, 'tts')
            and hasattr(self.provider, 'is_available')
            and self.provider.is_available()
        )

    def is_available(self) -> bool:
        return self.is_mimo_tts_available() or self.is_edge_tts_available()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        text = task.get("text", "")
        voice = task.get("voice", self.default_voice)
        output_path = task.get("output_path", "")
        engine = task.get("engine", self.tts_engine)

        if not text:
            return {"success": False, "error": "Không có văn bản để TTS"}
        if not output_path:
            return {"success": False, "error": "Không có đường dẫn output"}

        # Fallback chain
        engines_to_try = []
        if engine == "auto":
            if self.is_mimo_tts_available():
                engines_to_try.append("mimo")
            if self.is_edge_tts_available():
                engines_to_try.append("edge")
        elif engine == "mimo":
            engines_to_try = ["mimo"]
        elif engine == "edge":
            engines_to_try = ["edge"]

        if not engines_to_try:
            return {"success": False, "error": "Không có TTS engine nào khả dụng"}

        for eng in engines_to_try:
            try:
                if eng == "mimo":
                    await self.provider.tts(text, voice, output_path)
                    self.log(f"MiMo TTS OK: {output_path}")
                    return {"success": True, "output_path": output_path, "voice": voice, "engine": "mimo"}
                elif eng == "edge":
                    await self._generate_edge_tts(text, voice, output_path)
                    self.log(f"edge-tts OK: {output_path}")
                    return {"success": True, "output_path": output_path, "voice": voice, "engine": "edge"}
            except Exception as e:
                self.log(f"{eng} TTS lỗi: {e}, thử engine tiếp...")
                continue

        return {"success": False, "error": "Tất cả TTS engines đều lỗi"}

    async def generate_audio_batch(
        self,
        texts: List[str],
        output_dir: str,
        voice: Optional[str] = None,
        filename_prefix: str = "tts",
    ) -> List[Dict[str, Any]]:
        os.makedirs(output_dir, exist_ok=True)
        voice = voice or self.default_voice
        results = []

        self.log(f"Tạo audio batch: {len(texts)} văn bản → {output_dir}")

        for i, text in enumerate(texts):
            if not text.strip():
                results.append({"success": False, "error": "Văn bản rỗng", "index": i})
                continue

            output_path = os.path.join(output_dir, f"{filename_prefix}_{i:04d}.mp3")
            result = await self.execute({
                "text": text, "voice": voice, "output_path": output_path
            })
            result["index"] = i
            results.append(result)

        success = sum(1 for r in results if r.get("success"))
        self.log(f"Batch TTS: {success}/{len(texts)} thành công")
        return results

    async def _generate_edge_tts(self, text: str, voice: str, output_path: str) -> None:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice, rate="+15%", pitch="+0Hz")
        await communicate.save(output_path)
