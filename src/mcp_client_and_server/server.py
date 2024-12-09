import asyncio
import logging
from typing import Dict, Optional, List, Any
import mcp.types as types
import mcp.server as server
from mcp.server import request_ctx
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)

# Initialize an empty dictionary to store notes
notes = {}

# Create a server instance
server_instance = server.Server("notes-server")

@server_instance.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available resources."""
    return []

@server_instance.read_resource()
async def handle_read_resource(uri: types.AnyUrl) -> str:
    """Read notes resource."""
    logger.debug(f"Handling read_resource request for URI: {uri}")
    if uri.scheme != "notes":
        logger.error(f"Unsupported URI scheme: {uri.scheme}")
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    path = str(uri).replace("notes://", "")
    if path == "list":
        return "\n".join(notes.keys())
    
    logger.error(f"Unknown resource path: {path}")
    raise ValueError(f"Unknown resource path: {path}")

@server_instance.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """Handle prompts/list request.
    
    Returns:
        List[types.Prompt]: Empty list of prompts in mock mode
    """
    return []

@server_instance.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    logger.debug("Listing tools")
    return []

@server_instance.call_tool()
async def handle_call_tool(name: str, arguments: Dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    logger.debug(f"Calling tool: {name} with arguments: {arguments}")
    
    try:
        # Lazy import to avoid circular import
        from mcp_client_and_server.client import MCPChainedClient
        
        # Instantiate client if not already set
        chained_client = MCPChainedClient()

        if name == "add-note":
            notes[arguments['name']] = arguments['content']
            return [types.TextContent(type="text", text=f"Note '{arguments['name']}' added successfully")]
        
        elif name == "get-note":
            note = notes.get(arguments['name'], "Note not found")
            return [types.TextContent(type="text", text=note)]
        
        elif name == "list-notes":
            return [types.TextContent(type="text", text="\n".join(notes.keys()))]
        
        elif name == "connect-server":
            server = await chained_client.connect_server(
                name=arguments['name'], 
                command=arguments['command'], 
                cwd=arguments.get('cwd')
            )
            return [types.TextContent(type="text", text=f"Server '{arguments['name']}' connected successfully")]
        
        elif name == "disconnect-server":
            await chained_client.disconnect_server(arguments['name'])
            return [types.TextContent(type="text", text=f"Server '{arguments['name']}' disconnected successfully")]
        
        elif name == "list-servers":
            try:
                servers = await chained_client.list_servers()
                
                # Ensure servers is a list, convert to list if it's not
                if not isinstance(servers, list):
                    servers = list(servers)
                
                # If servers is empty, create a meaningful message
                if not servers:
                    return [types.TextContent(type="text", text="No servers connected")]
                
                # Return list of servers
                return [types.TextContent(type="text", text="\n".join(servers))]
                
            except Exception as e:
                logger.error(f"Error listing servers: {e}")
                return [types.TextContent(type="text", text=f"Error listing servers: {e}")]
        
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.exception(f"Error in call_tool: {e}")
        return [types.TextContent(type="text", text=str(e))]

async def handle_initialize(options: Optional[Dict] = None) -> dict:
    """Handle initialize request from client.
    
    Args:
        options: Optional initialization options. If provided, must be a dict.
                Any capabilities must be provided as a dict.
                
    Returns:
        A dict containing the server's capabilities, protocol version, and server info.
        
    Raises:
        TypeError: If options is provided but is not a dict
        ValueError: If options contains invalid values or unexpected keys
    """
    # Validate input type
    if options is not None and not isinstance(options, dict):
        raise TypeError("Options must be a dictionary")
        
    # Validate options structure if provided
    if options:
        # Check for unexpected keys
        valid_keys = {"capabilities", "protocolVersion", "serverInfo"}
        unexpected_keys = set(options.keys()) - valid_keys
        if unexpected_keys:
            raise ValueError(f"Unexpected keys in options: {unexpected_keys}")
            
        # Validate capabilities if present
        if "capabilities" in options:
            if not isinstance(options["capabilities"], dict):
                raise ValueError("capabilities must be a dictionary")
                
        # Validate protocolVersion if present
        if "protocolVersion" in options:
            if not isinstance(options["protocolVersion"], str):
                raise ValueError("protocolVersion must be a string")
                
        # Validate serverInfo if present
        if "serverInfo" in options:
            if not isinstance(options["serverInfo"], dict):
                raise ValueError("serverInfo must be a dictionary")
    
    # Return standard response
    return {
        "capabilities": {},  # Empty dict as we haven't defined any special capabilities yet
        "protocolVersion": "0.1.0",
        "serverInfo": {
            "name": "notes-server",
            "version": "0.1.0"
        }
    }

async def handle_ping(params: Any = None) -> dict:
    """Handle ping request from client.
    
    Args:
        params: Any parameters passed to ping (all ignored)
        
    Returns:
        An empty dict as per MCP spec
    """
    return {}

async def main():
    """Main server entry point"""
    logger.info("Starting NotesServer")
    try:
        initialization_options = server.InitializationOptions(
            server_name="notes-server",
            server_version="0.1.0",
            capabilities=server_instance.get_capabilities(
                notification_options=server.NotificationOptions(),
                experimental_capabilities={}
            )
        )

        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server running with stdio transport")
            await server_instance.run(
                read_stream=read_stream, 
                write_stream=write_stream,
                initialization_options=initialization_options,
                ping_handler=handle_ping
            )
    except Exception as e:
        logger.exception(f"Error in main: {e}")
        raise

def run_server():
    """Entry point for the package"""
    asyncio.run(main())

if __name__ == "__main__":
    run_server()