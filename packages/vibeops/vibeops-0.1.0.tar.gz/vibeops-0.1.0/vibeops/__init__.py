"""
VibeOps - DevOps automation tool with MCP server integration
"""

__version__ = "0.1.0"
__author__ = "VibeOps Team"
__email__ = "team@vibeops.dev"

from .server import VibeOpsServer
from .cli import cli

__all__ = ["VibeOpsServer", "cli"] 