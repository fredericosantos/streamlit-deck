"""
Abstract base interface for OS-specific character mappings.
"""

import string
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
    def extended_char_map(self) -> Dict[str, str]:
        """
        Return mapping from display names to internal key names.
        Subclasses should provide OS-specific modifier names.
        """
        mapping = {}
        # Add function keys (common across platforms)
        for i in range(1, 13):
            mapping[f"F{i}"] = f"f{i}"
        return mapping

    @property
    def basic_chars_display(self) -> List[str]:
        """Return list of basic characters for display."""
        return (
            [c.upper() for c in string.ascii_lowercase]
            + list(string.digits)
            + list("!@#$%^&*()[]{}|;:,.<>?/")
        )

    @property
    def basic_chars_map(self) -> Dict[str, str]:
        """Return mapping for basic characters."""
        mapping = {c.upper(): c for c in string.ascii_lowercase}
        mapping.update({d: d for d in string.digits})
        mapping.update({p: p for p in "!@#$%^&*()[]{}|;:,.<>?/"})
        return mapping
