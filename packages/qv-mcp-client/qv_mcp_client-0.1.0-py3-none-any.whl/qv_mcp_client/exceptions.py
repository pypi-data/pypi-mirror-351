"""Custom exceptions for MCP client"""


class MCPError(Exception):
    """Base exception for MCP client errors"""
    pass


class MCPConnectionError(MCPError):
    """Exception raised when connection to MCP server fails"""
    pass


class MCPTransportError(MCPError):
    """Exception raised for transport-related errors"""
    pass


class MCPToolError(MCPError):
    """Exception raised when tool execution fails"""
    pass


class MCPResourceError(MCPError):
    """Exception raised when resource access fails"""
    pass


class MCPPromptError(MCPError):
    """Exception raised when prompt access fails"""
    pass 