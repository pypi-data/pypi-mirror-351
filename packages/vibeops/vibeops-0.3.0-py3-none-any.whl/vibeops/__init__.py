"""
VibeOps - Configure Cursor to use VibeOps MCP server for DevOps automation

This package provides a simple CLI tool to configure Cursor IDE to connect
to the VibeOps Universal MCP server for AI-powered DevOps automation.

Usage:
    pip install vibeops
    vibeops init
    
Then restart Cursor and start chatting with AI-powered DevOps assistance!
"""

__version__ = "0.2.0"
__author__ = "VibeOps Team"
__email__ = "team@vibeops.dev"

from .cli import cli

__all__ = ["cli"] 