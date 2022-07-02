"""
Cataclysm DDA Python tools.
"""

from . import json, commands

try:
    from ._version import __version__
except ModuleNotFoundError:  # pragma: nocover
    # package is not installed
    __version__ = "0.0.0.dev0"
