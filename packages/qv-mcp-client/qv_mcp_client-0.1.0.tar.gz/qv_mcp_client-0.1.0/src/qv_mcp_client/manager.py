"""MCP Manager for handling multiple connections"""

import logging
from typing import Dict, List, Optional

from .client import MCPClient
from .config import MCPServerConfig
from .exceptions import MCPConnectionError


class MCPManager:
    """Manager for multiple MCP connections"""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.logger = logging.getLogger(__name__)
    
    async def add_server(self, config: MCPServerConfig) -> bool:
        """Add and connect to an MCP server"""
        if config.name in self.clients:
            await self.remove_server(config.name)
            
        client = MCPClient()
        
        try:
            await client.connect(config)
            self.clients[config.name] = client
            return True
        except MCPConnectionError as e:
            self.logger.error(f"Failed to add server {config.name}: {e}")
            return False
    
    async def remove_server(self, name: str):
        """Remove and disconnect from an MCP server"""
        if name in self.clients:
            await self.clients[name].disconnect()
            del self.clients[name]
            self.logger.info(f"Removed server: {name}")
    
    def get_client(self, name: str) -> Optional[MCPClient]:
        """Get a specific MCP client"""
        return self.clients.get(name)
    
    def list_servers(self) -> List[str]:
        """List connected server names"""
        return list(self.clients.keys())
    
    async def disconnect_all(self):
        """Disconnect from all servers"""
        for name, client in list(self.clients.items()):
            await client.disconnect()
        self.clients.clear()
        self.logger.info("Disconnected from all servers") 