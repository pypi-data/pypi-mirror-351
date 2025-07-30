from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseToolCallModel(ABC):
    """Base class for all models in the application."""

    @abstractmethod
    def filter_for_llm(self) -> Dict[str, Any]:
        """Filter model for LLM."""
        pass
