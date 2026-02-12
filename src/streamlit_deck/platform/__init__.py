"""
Platform-specific implementations for Streamlit Deck.
"""

import sys
from .base.apps import BaseApps
from .base.mappings import BaseMappings
from .base.executor import BaseExecutorExt

if sys.platform == "darwin":
    from .macos.apps import MacOSApps
    from .macos.mappings import MacOSMappings
    from .macos.executor import MacOSExecutorExt
else:
    from .linux.apps import LinuxApps
    from .linux.mappings import LinuxMappings
    from .linux.executor import LinuxExecutorExt


def get_apps() -> BaseApps:
    if sys.platform == "darwin":
        return MacOSApps()
    else:
        return LinuxApps()


def get_mappings() -> BaseMappings:
    if sys.platform == "darwin":
        return MacOSMappings()
    else:
        return LinuxMappings()


def get_executor_ext() -> BaseExecutorExt:
    if sys.platform == "darwin":
        return MacOSExecutorExt()
    else:
        return LinuxExecutorExt()
