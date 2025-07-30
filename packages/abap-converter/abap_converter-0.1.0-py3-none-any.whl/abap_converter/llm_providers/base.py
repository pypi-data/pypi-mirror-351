from __future__ import annotations
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Return the fully-converted code as **one string**."""

    @abstractmethod
    def modernise_code(self, legacy_code: str) -> str: ...
