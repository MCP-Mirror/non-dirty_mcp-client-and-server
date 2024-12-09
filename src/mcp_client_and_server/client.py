import asyncio
from typing import Dict, Any, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types


class MCPChainedClient:
    def __init__(self, server_name: str = "mcp-chained-client"):
        self.server_name = server_name
        self.connected_servers: Dict[str, Server] = {}
        
    async def connect_server(self, 
                              name: str, 
                              command: List[str], 
                              cwd: Optional[str] = None) -> Server:
        """Connect to a server using stdio"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        server = await stdio_server(process.stdin, process.stdout)
        self.connected_servers[name] = server
        return server
        
    async def disconnect_server(self, name: str):
        """Disconnect a specific server"""
        if name in self.connected_servers:
            await self.connected_servers[name].close()
            del self.connected_servers[name]
        
    async def list_servers(self) -> List[str]:
        """List all connected servers"""
        return list(self.connected_servers.keys())
        
    async def list_tools(self, server_name: Optional[str] = None) -> List[types.Tool]:
        """List tools from a specific server or all servers"""
        if server_name:
            if server_name not in self.connected_servers:
                raise ValueError(f"Server {server_name} not connected")
            return await self.connected_servers[server_name].list_tools()
        
        all_tools = []
        for name, server in self.connected_servers.items():
            server_tools = await server.list_tools()
            # Prefix tools with server name
            for tool in server_tools:
                tool.name = f"{name}:{tool.name}"
            all_tools.extend(server_tools)
        return all_tools
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> List[types.Content]:
        """Call a tool, potentially across servers"""
        # Check if tool is server-prefixed
        if ":" in tool_name:
            server_name, actual_tool_name = tool_name.split(":", 1)
            if server_name not in self.connected_servers:
                raise ValueError(f"Server {server_name} not connected")
            return await self.connected_servers[server_name].call_tool(actual_tool_name, arguments)
        
        # If no prefix, try all servers
        for server in self.connected_servers.values():
            try:
                return await server.call_tool(tool_name, arguments)
            except Exception:
                continue
        
        raise ValueError(f"Tool {tool_name} not found in any connected server")
        
    async def close(self):
        """Close all server connections"""
        for server in self.connected_servers.values():
            await server.close()
        self.connected_servers.clear()
