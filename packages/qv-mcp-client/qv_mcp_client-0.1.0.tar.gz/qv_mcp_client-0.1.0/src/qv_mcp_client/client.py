"""MCP Client implementation"""

import logging
from typing import Optional, Dict, Any, List, Tuple

from .config import MCPServerConfig, MCPTransportType
from .utils import is_windows, needs_cmd_wrapper
from .exceptions import MCPConnectionError, MCPTransportError, MCPToolError, MCPResourceError, MCPPromptError

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamablehttp_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP SDK not available. Install with: pip install mcp")


class MCPClient:
    """Simple MCP Client for connecting to MCP servers"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.config: Optional[MCPServerConfig] = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
    async def connect(self, config: MCPServerConfig) -> bool:
        """Connect to an MCP server"""
        if not MCP_AVAILABLE:
            raise MCPConnectionError("MCP SDK not available")
            
        try:
            self.config = config
            
            if config.transport == MCPTransportType.STDIO:
                await self._connect_stdio()
            elif config.transport == MCPTransportType.STREAMABLE_HTTP:
                await self._connect_streamable_http()
            else:
                raise MCPTransportError(f"Unsupported transport: {config.transport}")
                
            self.connected = True
            self.logger.info(f"Connected to MCP server: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")
            raise MCPConnectionError(f"Connection failed: {e}") from e
    
    async def _connect_stdio(self):
        """Connect using stdio transport"""
        if not self.config.command:
            raise MCPTransportError("Command required for stdio transport")
        
        # Handle Windows-specific commands that need cmd.exe
        command = self.config.command
        args = self.config.args or []
        
        if is_windows() and needs_cmd_wrapper(command):
            # Wrap command in cmd.exe for Windows
            args = ["/c", command] + args
            command = "cmd"
            self.logger.debug(f"Windows: Wrapping '{self.config.command}' in cmd.exe")
            
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=self.config.env
        )
        
        self._stdio_context = stdio_client(server_params)
        read, write = await self._stdio_context.__aenter__()
        
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
    
    async def _connect_streamable_http(self):
        """Connect using streamable HTTP transport"""
        if not self.config.url:
            raise MCPTransportError("URL required for streamable HTTP transport")
            
        self._http_context = streamablehttp_client(self.config.url)
        read, write, _ = await self._http_context.__aenter__()
        
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            except Exception:
                pass
                
        if hasattr(self, '_stdio_context'):
            try:
                await self._stdio_context.__aexit__(None, None, None)
            except Exception:
                pass
                
        if hasattr(self, '_http_context'):
            try:
                await self._http_context.__aexit__(None, None, None)
            except Exception:
                pass
                
        self.connected = False
        self.session = None
        self.logger.info("Disconnected from MCP server")
    
    def _ensure_connected(self):
        """Ensure client is connected, raise exception if not"""
        if not self.connected or not self.session:
            raise MCPConnectionError("Not connected to MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        self._ensure_connected()
            
        try:
            tools = await self.session.list_tools()
            return [tool.model_dump() for tool in tools.tools]
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            raise MCPToolError(f"Failed to list tools: {e}") from e
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Call a tool and return the result"""
        self._ensure_connected()
            
        try:
            result = await self.session.call_tool(name, arguments)
            
            # Extract text content from result
            if result.content:
                text_parts = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        text_parts.append(content.text)
                return "\n".join(text_parts)
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to call tool {name}: {e}")
            raise MCPToolError(f"Failed to call tool {name}: {e}") from e
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        self._ensure_connected()
            
        try:
            resources = await self.session.list_resources()
            return [resource.model_dump() for resource in resources.resources]
        except Exception as e:
            self.logger.error(f"Failed to list resources: {e}")
            raise MCPResourceError(f"Failed to list resources: {e}") from e
    
    async def read_resource(self, uri: str) -> Optional[Tuple[str, str]]:
        """Read a resource and return (content, mime_type)"""
        self._ensure_connected()
            
        try:
            content, mime_type = await self.session.read_resource(uri)
            return content, mime_type
        except Exception as e:
            self.logger.error(f"Failed to read resource {uri}: {e}")
            raise MCPResourceError(f"Failed to read resource {uri}: {e}") from e
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts"""
        self._ensure_connected()
            
        try:
            prompts = await self.session.list_prompts()
            return [prompt.model_dump() for prompt in prompts.prompts]
        except Exception as e:
            self.logger.error(f"Failed to list prompts: {e}")
            raise MCPPromptError(f"Failed to list prompts: {e}") from e
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Get a prompt and return the formatted text"""
        self._ensure_connected()
            
        try:
            result = await self.session.get_prompt(name, arguments or {})
            
            # Extract text from messages
            text_parts = []
            for message in result.messages:
                if hasattr(message.content, 'text'):
                    text_parts.append(message.content.text)
                elif isinstance(message.content, list):
                    for content in message.content:
                        if hasattr(content, 'text'):
                            text_parts.append(content.text)
            
            return "\n".join(text_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to get prompt {name}: {e}")
            raise MCPPromptError(f"Failed to get prompt {name}: {e}") from e 