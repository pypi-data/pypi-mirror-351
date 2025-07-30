"""This module contains the core classes of the flock package."""

from flock.core.context.context import FlockContext
from flock.core.flock import Flock
from flock.core.flock_agent import FlockAgent
from flock.core.flock_factory import FlockFactory
from flock.core.registry import (
    RegistryHub as FlockRegistry,  # Keep FlockRegistry name for API compatibility
    flock_callable,
    flock_component,
    flock_tool,
    flock_type,
    get_registry,
)
from flock.core.mcp.flock_mcp_server import (
    FlockMCPServerBase,
)
from flock.core.mcp.flock_mcp_tool_base import FlockMCPToolBase
from flock.core.mcp.mcp_client import FlockMCPClientBase
from flock.core.mcp.mcp_client_manager import FlockMCPClientManagerBase

__all__ = [
    "Flock",
    "FlockAgent",
    "FlockContext",
    "FlockFactory",
    "FlockMCPClientBase",
    "FlockMCPClientManagerBase",
    "FlockMCPServerBase",
    "FlockMCPServerConfig",
    "FlockMCPToolBase",
    "FlockRegistry",
    "flock_callable",
    "flock_component",
    "flock_tool",
    "flock_type",
    "get_registry",
]
