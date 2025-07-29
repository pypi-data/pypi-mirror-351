"""Basic usage example for QV MCP Client"""

import asyncio
import logging
from qv_mcp_client import MCPClient, MCPServerConfig, MCPTransportType
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)


async def main():
    """Example of using MCP client"""
    
    # Example 1: Connect to a stdio MCP server
    config = MCPServerConfig(
        name="example-server",
        transport=MCPTransportType.STDIO,
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    )
    
    client = MCPClient()
    
    try:
        # Connect to server
        await client.connect(config)
        print("Connected successfully!")
        
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[tool['name'] for tool in tools]}")
        
        # Beispiel: Verzeichnisinhalt auflisten mit list_directory
        dir_path = "/tmp" if platform.system().lower() != "windows" else "C:\\tmp"
        if any(tool['name'] == 'list_directory' for tool in tools):
            result = await client.call_tool("list_directory", {"path": dir_path})
            print(f"Verzeichnisinhalt von {dir_path}:")
            print(result)
        else:
            print("Das Tool 'list_directory' ist auf diesem Server nicht verfügbar.")
        
        # List available resources
        resources = await client.list_resources()
        print(f"Available resources: {len(resources)}")
        
        # Example tool call (if available)
        if tools:
            tool_name = tools[0]['name']
            print(f"Calling tool: {tool_name}")
            # Note: Adjust arguments based on the actual tool
            result = await client.call_tool(tool_name, {})
            print(f"Tool result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await client.disconnect()
        print("Disconnected")


async def manager_example():
    """Example of using MCP manager for multiple connections"""
    from qv_mcp_client import MCPManager
    
    manager = MCPManager()
    
    # Add multiple servers
    configs = [
        MCPServerConfig(
            name="filesystem",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        ),
        # Add more server configs as needed
    ]
    
    try:
        for config in configs:
            success = await manager.add_server(config)
            print(f"Added server {config.name}: {success}")
        
        # List connected servers
        print(f"Connected servers: {manager.list_servers()}")
        
        # Use a specific client
        client = manager.get_client("filesystem")
        if client:
            tools = await client.list_tools()
            print(f"Filesystem tools: {len(tools)}")
    
    finally:
        await manager.disconnect_all()


if __name__ == "__main__":
    print("Running basic MCP client example...")
    asyncio.run(main())
    
    print("\nRunning manager example...")
    asyncio.run(manager_example()) 