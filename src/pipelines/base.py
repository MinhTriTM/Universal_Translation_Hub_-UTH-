"""Base pipeline — ABC cho tất cả pipelines."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import time


@dataclass
class PipelineResult:
    """Kết quả chung của mọi pipeline."""
    success: bool = False
    pipeline: str = ""
    input_path: str = ""
    output_path: str = ""
    total_items: int = 0
    translated_items: int = 0
    failed_items: int = 0
    errors: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    elapsed_seconds: float = 0.0

    def summary(self) -> str:
        lines = [
            f"Pipeline: {self.pipeline}",
            f"Success: {self.success}",
            f"Items: {self.translated_items}/{self.total_items} translated, {self.failed_items} failed",
            f"Time: {self.elapsed_seconds:.1f}s",
        ]
        if self.errors:
            lines.append(f"Errors: {len(self.errors)}")
            for err in self.errors[:5]:
                lines.append(f"  - {err}")
        return "\n".join(lines)


class BasePipeline(ABC):
    """Lớp cơ sở trừu tượng cho tất cả pipelines."""

    name: str = "base"

    def __init__(self, provider=None, memory=None):
        self.provider = provider  # TranslationProvider
        self.memory = memory      # TranslationMemory

    @abstractmethod
    async def run(self, input_path: str, options: Dict[str, Any] = None) -> PipelineResult:
        """Chạy pipeline chính."""
        pass

    @abstractmethod
    async def validate(self, result: PipelineResult) -> List[str]:
        """Kiểm tra kết quả, trả về list lỗi (rỗng = OK)."""
        pass

    def log(self, step: str, message: str):
        print(f"  [{self.name}] Step {step}: {message}")

    async def execute(self, input_path: str, options: Dict[str, Any] = None) -> PipelineResult:
        """Wrapper: chạy pipeline + validate + timing."""
        t0 = time.time()
        result = await self.run(input_path, options or {})
        result.elapsed_seconds = time.time() - t0

        errors = await self.validate(result)
        if errors:
            result.errors.extend(errors)
            if not result.success:
                result.success = False

        return result
