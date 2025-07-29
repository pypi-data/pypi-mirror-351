import logging
import json
import textwrap
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack, asynccontextmanager

from pydantic import AnyUrl
from mcp_cli.utils import async_command, expand_env_vars
import typer

from mcp_cli.config import load_config
from mcp import ClientSession, ReadResourceResult, Resource, StdioServerParameters
from mcp.types import Tool, CallToolResult, ResourceTemplate, Prompt
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

tool_app = typer.Typer(help="Commands for listing and executing tools on MCP servers.")


@asynccontextmanager
async def get_server_session(server_name: str, server_config: Dict[str, Any]):
    async with AsyncExitStack() as exit_stack:
        server_params = None
        try:
            expanded_config = expand_env_vars(server_config)

            server_params = StdioServerParameters(**expanded_config)

            transport_context = stdio_client(server_params)
            reader, writer = await exit_stack.enter_async_context(transport_context)
            
            session_context = ClientSession(reader, writer)
            session = await exit_stack.enter_async_context(session_context)
            
            await session.initialize() 
            
            yield session

        except Exception as e:
            typer.secho(f"Error connecting to {server_name}: {e}", fg=typer.colors.RED, err=True)
            raise

@dataclass
class ServerCapabilities:
    tools: List[Tool]
    resources: List[Resource | ResourceTemplate]
    prompts: List[Prompt]

async def inspect_server_capabilities(server_name: str, server_config: Dict[str, Any]) -> ServerCapabilities:
    """
    Helper function to connect to a single MCP server and inspect its capabilities.
    Uses the get_server_session context manager for session handling.
    """
    logger.info(f"Inspecting server capabilities: {server_name}...")
    try:
        async with get_server_session(server_name, server_config) as session:
            response_tools = await session.list_tools()
            tools = response_tools.tools

            try:
                response_resources = await session.list_resources()
                response_resource_templates = await session.list_resource_templates()

                all_resources = [*response_resources.resources, *response_resource_templates.resourceTemplates]
            except Exception as e:
                logger.info(f"Error listing resources: {e}")
                all_resources = []

            try:
                response_prompts = await session.list_prompts()
                prompts = response_prompts.prompts
            except Exception as e:
                logger.info(f"Error listing prompts: {e}")
                prompts = []

            return ServerCapabilities(tools=tools, resources=all_resources, prompts=prompts)
        
    except Exception as e:
        typer.secho(f"Failed to fetch tools from {server_name}: {type(e).__name__} - {e}", fg=typer.colors.RED, err=True)
        raise

def parse_tool_result(result: CallToolResult) -> str:
    tool_result_text = ""
    if result and hasattr(result, 'content') and result.content:
        for content_item in result.content:
            if hasattr(content_item, 'text') and content_item.text: # type: ignore
                tool_result_text += str(content_item.text) + "\n" # type: ignore
            elif isinstance(content_item, str):
                tool_result_text += content_item + "\n"
            elif isinstance(content_item, dict) and "text" in content_item:
                tool_result_text += str(content_item["text"]) + "\n"
            elif hasattr(content_item, '__str__'): # Fallback to string representation
                tool_result_text += str(content_item) + "\n"

    return tool_result_text.strip()

def parse_resource_result(result: ReadResourceResult) -> str:
    resource_result_text = ""
    if result and hasattr(result, 'contents') and result.contents:
        for content_item in result.contents:
            # Assuming TextResourceContents has a 'text' attribute
            if hasattr(content_item, 'text') and content_item.text: # type: ignore
                resource_result_text += str(content_item.text) + "\n" # type: ignore
            # Add handling for BlobResourceContents or other types if necessary
            elif hasattr(content_item, '__str__'): # Fallback to string representation
                 resource_result_text += str(content_item) + "\n"
            # Placeholder for unhandled types
            else:
                resource_result_text += "[Unhandled resource content type]\n"

    return resource_result_text.strip()

async def call_tool_on_server(server_name: str, server_config: Dict[str, Any], tool_name: str, input_args: Dict[str, Any]) -> str:
    """
    Helper function to connect to a single MCP server and call a tool.
    Uses the get_server_session context manager for session handling.
    """
    logger.info(f"Attempting to call tool '{tool_name}' on server: {server_name}...")

    try:
        async with get_server_session(server_name, server_config) as session:
            result = await session.call_tool(tool_name, input_args)
            
            result_text = parse_tool_result(result)

            return result_text

    except Exception as e: 
        typer.secho(f"Error when calling tool '{tool_name}' on {server_name}: {type(e).__name__} - {e}", fg=typer.colors.RED, err=True)
        raise

async def call_resource_on_server(server_name: str, server_config: Dict[str, Any], resource_name: str) -> str:
    """
    Helper function to connect to a single MCP server and call a resource.
    Uses the get_server_session context manager for session handling.
    """
    logger.info(f"Attempting to call resource '{resource_name}' on server: {server_name}...")   
    
    try:
        async with get_server_session(server_name, server_config) as session:
            uri = AnyUrl(resource_name)
            result = await session.read_resource(uri)

            result_text = parse_resource_result(result)

            return result_text

    except Exception as e: 
        typer.secho(f"Error when calling resource '{resource_name}' on {server_name}: {type(e).__name__} - {e}", fg=typer.colors.RED, err=True)
        raise


def print_tools(server_name: str, server_capabilities: ServerCapabilities):
    typer.secho(f"\nTools available on server '{server_name}':", fg=typer.colors.CYAN, bold=True)

    for tool in server_capabilities.tools:
        typer.secho(f"\nTool: {tool.name}", fg=typer.colors.GREEN, bold=True)
        
        description = tool.description
        typer.echo("  Description:")
        if description:
            # Dedent the description and remove leading/trailing blank lines from the block
            dedented_description = textwrap.dedent(str(description)).strip()
            if dedented_description: # Ensure there's content after stripping
                description_lines = dedented_description.split('\n')
                for line in description_lines:
                    typer.echo(f"    {line}")
            else:
                typer.echo("    N/A")
        else:
            typer.echo("    N/A")
        
        input_schema = tool.inputSchema 
        
        if input_schema and isinstance(input_schema, dict) and input_schema.get('properties'):
            typer.echo("  Inputs:")
            for prop_name, prop_details in input_schema['properties'].items():
                typer.echo(f"    - {prop_name}:")
                typer.echo(f"        Type: {prop_details.get('type', 'N/A')}")
                if 'description' in prop_details:
                    typer.echo(f"        Description: {prop_details['description']}")
                
                is_required = False
                if 'required' in input_schema and isinstance(input_schema['required'], list):
                    if prop_name in input_schema['required']:
                        is_required = True
                typer.echo(f"        Required: {is_required}")
        elif input_schema and isinstance(input_schema, dict) and not input_schema.get('properties') and input_schema.get('type') == 'object':
            typer.echo("  Inputs: Takes an object, but no specific properties defined (or empty properties section).")
        else:
            typer.echo("  Inputs: None or schema not in expected format")

    for resource in server_capabilities.resources:
        typer.secho(f"\nResource: {resource.name}", fg=typer.colors.GREEN, bold=True)
        
        description = resource.description
        typer.echo("  Description:")
        if description:
            # Dedent the description and remove leading/trailing blank lines from the block
            dedented_description = textwrap.dedent(str(description)).strip()
            if dedented_description: # Ensure there's content after stripping
                description_lines = dedented_description.split('\n')
                for line in description_lines:
                    typer.echo(f"    {line}")
            else:
                typer.echo("    N/A")
        else:
            typer.echo("    N/A")

        if isinstance(resource, Resource):
            uri = resource.uri
            typer.echo(f"  URI:")
            if uri:
                typer.echo(f"    {uri}")
        elif isinstance(resource, ResourceTemplate):
            uri_template = resource.uriTemplate
            typer.echo(f"  URI Template:")
            if uri_template:
                typer.echo(f"    {uri_template}")
        else:
            typer.echo("    N/A")

    if len(server_capabilities.tools) == 0:
        typer.echo(f"No tools listed for server '{server_name}' or an error occurred during fetching.")


def parse_input_args(input_args_json: Optional[str]) -> Dict[str, Any]:
    if input_args_json:
        try:
            return json.loads(input_args_json)
        except json.JSONDecodeError as e:
            typer.secho(f"Error: Invalid JSON provided for --input: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
    return {}


def get_server_config(server_name: str, config_file: Optional[str]) -> Dict[str, Any]:
    config = load_config(config_file)

    mcp_servers_config: Dict[str, Any] = config["mcpServers"]

    if server_name not in mcp_servers_config:
        typer.secho(f"Server '{server_name}' not found in configuration file '{config_file}'.", fg=typer.colors.RED, err=True)
        available_servers = list(mcp_servers_config.keys())
        if available_servers:
            typer.echo("Available servers are: " + ", ".join(available_servers))
        raise typer.Exit(code=1)
        
    server_config_dict = mcp_servers_config[server_name]

    return server_config_dict


@tool_app.command("list")
@async_command
async def list_tools(
    server_name: Optional[str] = typer.Option(
        None,
        "--server",
        "-s",
        help="Specify a server to list tools for. If omitted, lists tools for all servers.",
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config",
        "-C",
        help="Path to the server configuration file.",
    ),
):
    """
    Lists available tools for MCP servers.
    Lists tools for a specific server if --server is provided,
    otherwise lists tools for all configured servers.
    """
    if server_name:
        server_config_dict = get_server_config(server_name, config_file)

        logger.info(f"Creating connection parameters for server '{server_name}' with config: {server_config_dict}")

        server_capabilities = await inspect_server_capabilities(server_name, server_config_dict)
        
        print_tools(server_name, server_capabilities)
    else:
        # not implemented yet
        typer.echo("Listing tools for all servers is not implemented yet.")
        raise typer.Exit(code=1)


@tool_app.command("call")
@async_command
async def execute_tool(
    tool_name: str = typer.Argument(..., help="The name of the tool to execute."),
    server_name: str = typer.Option(
        ..., # Make server mandatory for execute
        "--server",
        "-s",
        help="The MCP server on which to run the tool.",
    ),
    input_args_json: Optional[str] = typer.Option(
        None,
        "--input",
        "-i",
        help="Tool input as a JSON string. E.g., '{\"query\": \"hello world\"}'",
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config",
        "-C",
        help="Path to the server configuration file.",
    ),
):
    """
    Executes a given tool on a specified MCP server.
    Tool input can be provided as a JSON string via --input
    or from a JSON file via --input-file.
    """
    typer.echo(
        f"Executing tool: \n"
        f"  Tool name: {tool_name}\n"
        f"  Server: {server_name}\n"
        f"  Input: {input_args_json}\n"
    )

    server_config = get_server_config(server_name, config_file)

    tool_input_args: Dict[str, Any] = parse_input_args(input_args_json)

    try:
        server_capabilities = await inspect_server_capabilities(server_name, server_config)
        
        tool = next((tool for tool in server_capabilities.tools if tool.name == tool_name), None)
      
        if not tool:
            typer.secho(f"Tool '{tool_name}' not found on server '{server_name}'.", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

        tool_result_text = await call_tool_on_server(server_name, server_config, tool_name, tool_input_args)
        
        typer.echo(f"Tool result: \n{tool_result_text}\n")
    except Exception as e:
        raise typer.Exit(code=1)


@tool_app.command("read")
@async_command
async def read_resource(
    uri: str = typer.Argument(
        ...,
        help="The URI of the resource to execute.",
    ),
    server_name: str = typer.Option(
        ..., # Make server mandatory for execute
        "--server",
        "-s",
        help="The MCP server on which to run the tool.",
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config",
        "-C",
        help="Path to the server configuration file.",
    ),
):
    """
    Reads a given resource from a specified MCP server.
    """
    typer.echo(
        f"Reading resource: \n"
        f"  Server: {server_name}\n"
        f"  URI: {uri}\n"
    )

    server_config = get_server_config(server_name, config_file)

    try:
        # server_capabilities = await inspect_server_capabilities(server_name, server_config)
        
        # resource = next((resource for resource in server_capabilities.resources if resource.name == uri), None)

        # if not resource:
        #     typer.secho(f"Resource '{uri}' not found on server '{server_name}'.", fg=typer.colors.RED, err=True)
        #     raise typer.Exit(code=1)

        resource_result_text = await call_resource_on_server(server_name, server_config, uri)
        
        typer.echo(f"Resource result: \n{resource_result_text}\n")
    except Exception as e:
        raise typer.Exit(code=1)
