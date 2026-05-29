"""
BaseAgent - Lớp cơ sở cho tất cả agent trong hệ thống multi-agent.
Mọi agent kế thừa từ lớp này và override phương thức execute().
"""

from typing import Any, Dict, Optional


class BaseAgent:
    """Lớp cơ sở trừu tượng cho mọi agent."""

    def __init__(
        self,
        name: str,
        provider: Any = None,
        memory: Any = None,
    ):
        """
        Khởi tạo agent.

        Args:
            name: Tên định danh của agent (ví dụ: "TranslatorAgent")
            provider: Instance TranslationProvider để gọi API dịch thuật
            memory: Instance TranslationMemory để truy xuất TM cache
        """
        self.name: str = name
        self.provider: Optional[Any] = provider
        self.memory: Optional[Any] = memory

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực thi nhiệm vụ. Lớp con PHẢI override phương thức này.

        Args:
            task: Dict chứa thông tin nhiệm vụ, schema tùy từng agent

        Returns:
            Dict chứa kết quả thực thi

        Raises:
            NotImplementedError: Nếu lớp con không override
        """
        raise NotImplementedError(
            f"[{self.name}] Chưa implement execute(). "
            "Lớp con phải override phương thức này."
        )

    def log(self, message: str) -> None:
        """In log với prefix tên agent."""
        print(f"  [{self.name}] {message}")
