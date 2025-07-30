# bark-mcp

A Model Context Protocol (MCP) server that connects to [Bark](https://github.com/Finb/bark-server), a notification server for iOS. This allows LLM applications to send notifications to iOS devices through the MCP standard.

## Features

- Simple MCP server implementation using FastMCP
- Single tool: `notify` to send notifications to iOS devices
- Configurable via environment variables
- Easy to use command-line interface

## Installation

```bash
# Install from PyPI
pip install bark-mcp

# Or install from source
git clone https://github.com/yourusername/bark-mcp.git
cd bark-mcp
pip install -e .
```

## Configuration

The server requires the following environment variables:

- `BARK_SERVER_URL`: URL of the Bark server (e.g., `https://api.day.app`)
- `BARK_API_KEY`: Your Bark API key/device key

You can set these variables in your environment or create a `.env` file:

```
BARK_SERVER_URL=https://api.day.app
BARK_API_KEY=your_api_key_here
```

### Bark API Format

The server uses the Bark API with the following URL formats:

- `GET /{bark-key}/{title}/{content}?url={url}` (when title and URL are provided)
- `GET /{bark-key}/{title}/{content}` (when only title is provided)
- `GET /{bark-key}/{content}` (when only content is provided)

## Usage

### Command Line

Start the MCP server using either of these commands:

```bash
# Using the standard command (after installing the package)
bark-mcp

# Using uvx (runs without installing the package)
uvx bark-mcp
```

Both commands support the same options:

```bash
# Specify a .env file
bark-mcp --env-file /path/to/.env
# or
uvx bark-mcp --env-file /path/to/.env

# Enable debug logging
bark-mcp --debug
# or
uvx bark-mcp --debug
```

> **Note**: `uvx` is a command from the `uv` package manager that runs Python tools in temporary, isolated environments without installing them permanently. Install it with `pip install uv`.
>
> **Important**: Make sure to use `uvx bark-mcp` with a hyphen, not `uvx bark_mcp` with an underscore. The command name must match the entry point defined in the package.

### Using with MCP Clients

The server provides a single tool:

- `notify`: Send a notification to an iOS device
  - Parameters:
    - `title` (optional): Title of the notification
    - `content` (required): Content of the notification
    - `url` (optional): URL to open when the notification is tapped

Example usage in an MCP client:

```python
# This would be handled by the MCP client
result = await call_tool("notify", {
    "title": "Hello from MCP",
    "content": "This is a notification sent via MCP",
    "url": "https://example.com"
})
```

## Development

### Prerequisites

- Python 3.8+
- FastMCP
- Requests
- Python-dotenv

### Running Tests

```bash
# TODO: Add testing instructions
```

## Troubleshooting

### Command Not Found

If you see an error like:

```
The executable `bark_mcp` was not found.
warning: An executable named `bark_mcp` is not provided by package `bark-mcp`.
```

Make sure you're using the correct command name: `bark-mcp` with a hyphen, not `bark_mcp` with an underscore.

### Environment Variables Not Set

If you see errors about missing environment variables:

```
BARK_SERVER_URL environment variable is required
```

Make sure to:
1. Create a `.env` file based on the `.env.example` template
2. Set the required environment variables in your shell or use the `--env-file` option

## License

This project is licensed under the MIT License - see the LICENSE file for details.
