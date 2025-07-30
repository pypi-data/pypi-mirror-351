# mcp-cli

Model Context Protocol Command Line Interface (MCP CLI)

A CLI for interacting with Model Context Protocol (MCP) servers. Allows listing and execution of tools, reading resources, and managing server configurations.

---

## 🌟 Features

- List available MCP servers defined in a JSON configuration file.
- Inspect and list available tools on an MCP server.
- Execute tools on MCP servers with JSON-formatted inputs.
- Read resources from MCP servers by URI.
- Support for environment variable expansion and `.env` files.
- Rich, colored output powered by Rich and Typer.

## 📋 Prerequisites

- Python 3.11 or higher
- uv

## 🚀 Installation

```bash
uv sync --reinstall
```

Run the CLI:

```bash
uv run mcp-cli --help
```

## 🧰 Global Options

- `--config`, `-C` <path>: Path to the server configuration file (default: `server_config.json`).
- `--server`, `-s` <name>: Specify the server name when listing or executing tools/resources.


## 🏷️ Available Commands

### Server Commands

- `mcp-cli server list`
  Lists all configured MCP servers.

### Tool Commands

- `mcp-cli tool list --server <server_name>`
  Lists all tools available on the specified server.

- `mcp-cli tool call <tool_name> --server <server_name> [--input '{"key": "value"}']`
  Executes a tool on the specified server. Provide inputs as a JSON string.

- `mcp-cli tool read <uri> --server <server_name>`
  Reads a resource from the server by its URI.

## ⚙️ Server Configuration

Create a `server_config.json` file in the project root or set the `$MCP_CLI_CONFIG_PATH` environment variable:

```json
{
  "mcpServers": {
    "example-server": {
      "command": "uv",
      "args": ["run", "example_mcp_server.py"],
      "env": {
        "EXAMPLE_API_KEY": "$EXAMPLE_API_KEY"
      },
    }
  }
}
```

Each server entry supports:
- `command`: The command to start the server.
- `args`: List of arguments for the command.
- `env`: Environment variables (values can reference host env vars).

## ⚙️ Environment Variables

Set the `MCP_CLI_CONFIG_PATH` variable to the path where your config lives, e.g.

- `export MCP_CLI_CONFIG_PATH="$HOME/.mcp/server_config.json"`

Also supports storing environment variables in a separate file, just set `$MCP_CLI_DOTENV_PATH`

- `export MCP_CLI_DOTENV_PATH="$HOME/.mcp/.env"`

## 📚 Examples

List servers:

```bash
mcp-cli server list
```

List tools on a server:

```bash
mcp-cli tool list --server sqlite
```

Execute a tool with JSON input:

```bash
mcp-cli tool call summarize --server sqlite --input '{"text": "Hello world"}'
```

Read a resource by URI:

```bash
mcp-cli tool read https://example.com/resource.txt --server sqlite
```
