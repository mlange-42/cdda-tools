"""
Cataclysm DDA Python tools, package entrypoint.
"""

from . import cli, commands, game, json_utils

try:
    from ._version import __version__
except ModuleNotFoundError:  # pragma: nocover
    # package is not installed
    __version__ = "0.0.0.dev0"
