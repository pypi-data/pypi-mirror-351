"""
Unreal MCP Server - A Model Context Protocol server for Unreal Engine integration.

This package provides comprehensive tools for automating Unreal Engine tasks
through the Model Context Protocol, including blueprint creation, actor manipulation,
UMG widget development, and more.
"""

__version__ = "0.1.0"
__author__ = "Symbiote Creative Labs"
__email__ = "jonasz@symbiote-labs.ai"

from .server import UnrealMCPServer

__all__ = ["UnrealMCPServer", "__version__"]