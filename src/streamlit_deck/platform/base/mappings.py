"""
Abstract base interface for OS-specific character mappings.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseMappings(ABC):
    """
    Interface for OS-specific key mappings and character sets.
    """

    @property
    @abstractmethod
    def extended_chars(self) -> List[str]:
        """Return list of extended/special characters for the OS."""
        pass

    @property
    @abstractmethod
    def extended_char_map(self) -> Dict[str, str]:
        """Return mapping from display names to internal key names."""
        pass

    @property
    @abstractmethod
    def basic_chars_display(self) -> List[str]:
        """Return list of basic characters for display."""
        pass

    @property
    @abstractmethod
    def basic_chars_map(self) -> Dict[str, str]:
        """Return mapping for basic characters."""
        pass
