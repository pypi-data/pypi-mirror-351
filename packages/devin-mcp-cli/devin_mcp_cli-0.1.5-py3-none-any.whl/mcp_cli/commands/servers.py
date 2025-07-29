import typer
from typing import Optional, List, Dict, Tuple
from mcp_cli.config import load_config, extract_server_names
import logging

server_app = typer.Typer(help="Commands for managing MCP servers.")


def process_options(
    server: Optional[str],
    config_file: Optional[str] = None
) -> Tuple[List[str], List[str], Dict[int, str]]:
    """
    Process CLI options to produce a list of server names and set environment variables.
    
    Returns:
        Tuple of (servers_list, user_specified, server_names)
    """
    servers_list: List[str] = []
    user_specified: List[str] = []
    server_names: Dict[int, str] = {}
    
    logging.debug(f"Processing options: server={server}")
    
    if server:
        # Allow comma-separated servers.
        user_specified = [s.strip() for s in server.split(",")]
        logging.debug(f"Parsed server parameter into: {user_specified}")
        servers_list.extend(user_specified)
    
    logging.debug(f"Initial servers list: {servers_list}")
    
    # Load configuration to get server names and default servers
    config = load_config(config_file)
    if not servers_list and config and "mcpServers" in config:
        # Default to all configured servers if none specified
        servers_list = list(config["mcpServers"].keys())
    
    # Extract server names mapping (for display)
    server_names = extract_server_names(config, user_specified)
    
    return servers_list, user_specified, server_names


@server_app.command("list")
def list_mcp_servers(
    config_file: Optional[str] = typer.Option(
        None,
        "--config",
        "-C",
        help="Path to the server configuration file.",
    )
):
    """
    Lists available MCP servers from the configuration file.
    """
    servers, _, _ = process_options(
        server=None,
        config_file=config_file,
    )

    if servers:
        typer.echo("Available MCP Servers:")
        for s_name in servers:
            typer.echo(f"- {s_name}")
    else:
        typer.echo(f"No MCP servers found. Verify the configuration file: '{config_file}'")

