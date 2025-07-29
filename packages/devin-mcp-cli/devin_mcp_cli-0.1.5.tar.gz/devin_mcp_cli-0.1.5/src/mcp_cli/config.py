import json
import logging
from typing import Optional, Dict, Any
import os
import typer

def load_config(config_file: Optional[str]) -> Dict[str, Any]:
    """Load the configuration file.
    
    Args:
        config_file: Path to the config file. If not provided, the MCP_CLI_CONFIG_PATH environment variable is used, or the config file in the root of the repository.
        
    Returns:
        Dictionary containing the MCP servers configuration.
    """
    env_config_path = os.getenv("MCP_CLI_CONFIG_PATH", None)

    if config_file and os.path.exists(config_file):
        config_file_used = config_file
    elif env_config_path and os.path.exists(env_config_path):
        config_file_used = env_config_path
    else:
        typer.echo(f"Config file not found, please set the MCP_CLI_CONFIG_PATH environment variable to the path where your config lives, e.g. `export MCP_CLI_CONFIG_PATH=~/.mcp/server_config.json` or provide it with the --config flag.")
        raise typer.Exit(code=1)

    try:
        with open(config_file_used, 'r') as f:
            config = json.load(f)
            if "mcpServers" not in config or not isinstance(config["mcpServers"], dict) or not config["mcpServers"]:
                raise ValueError(f"MCP servers configuration ('mcpServers') is missing, not a valid dictionary, or empty in '{config_file_used}'.")
    
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in config file '{config_file_used}'")
        raise
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        raise
    
    return config


def extract_server_names(config, specified_servers=None):
    """
    Extract server names from the config.
    
    Args:
        config: Configuration dictionary
        specified_servers: Optional list of specific servers to use
        
    Returns:
        Dictionary mapping server indices to their names
    """
    server_names = {}
    
    # Return empty dict if no config
    if not config or "mcpServers" not in config:
        return server_names
    
    # Get the list of servers from config
    mcp_servers = config["mcpServers"]
    
    # If specific servers were requested, map them in order
    if specified_servers:
        for i, name in enumerate(specified_servers):
            if name in mcp_servers:
                server_names[i] = name
    else:
        # Map all servers to their indices
        for i, name in enumerate(mcp_servers.keys()):
            server_names[i] = name
    
    return server_names