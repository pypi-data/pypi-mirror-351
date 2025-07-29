"""Configuration classes for MCP client"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List


class MCPTransportType(Enum):
    """Transport types for MCP connections"""
    STDIO = "stdio"
    HTTP = "http"
    STREAMABLE_HTTP = "streamable_http"


@dataclass
class MCPServerConfig:
    """Configuration for MCP server connection"""
    name: str
    transport: MCPTransportType
    # For stdio transport
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    # For HTTP transports
    url: Optional[str] = None 