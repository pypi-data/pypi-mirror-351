# dynamicwf: An Adobe Interns MCP server

## Overview

A Model Context Protocol server for accessing and filtering Adobe intern information. This server provides tools to retrieve and search for interns via Large Language Models.

Please note that dynamicwf is currently in early development. The functionality and available tools are subject to change and expansion as we continue to develop and improve the server.

### Tools

1. `get_adobe_interns`
   - Gets a list of all current Adobe interns
   - Input: None
   - Returns: List of all current Adobe interns as text output

2. `filter_adobe_interns`
   - Filters Adobe interns by name
   - Input:
     - `name_contains` (string, optional): String to filter interns by name
   - Returns: Filtered list of interns whose names contain the search string

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *dynamicwf*.

### Using PIP

Alternatively you can install `dynamicwf` via pip:

```
pip install dynamicwf
```

After installation, you can run it as a script using:

```
python -m dynamicwf
```

## Configuration

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "interns": {
    "command": "uvx",
    "args": ["dynamicwf"]
  }
}
```
</details>

<details>
<summary>Using docker</summary>

```json
"mcpServers": {
  "interns": {
    "command": "docker",
    "args": ["run", "--rm", "-i", "dynamicwf"]
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
"mcpServers": {
  "interns": {
    "command": "python",
    "args": ["-m", "dynamicwf"]
  }
}
```
</details>

### Usage with [Zed](https://github.com/zed-industries/zed)

Add to your Zed settings.json:

<details>
<summary>Using uvx</summary>

```json
"context_servers": [
  "dynamicwf": {
    "command": {
      "path": "uvx",
      "args": ["dynamicwf"]
    }
  }
],
```
</details>

<details>
<summary>Using pip installation</summary>

```json
"context_servers": {
  "dynamicwf": {
    "command": {
      "path": "python",
      "args": ["-m", "dynamicwf"]
    }
  }
},
```
</details>

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```
npx @modelcontextprotocol/inspector uvx dynamicwf
```

Or if you've installed the package in a specific directory or are developing on it:

```
cd path/to/servers/src/dynamicwf
npx @modelcontextprotocol/inspector uv run dynamicwf
```

## Development

If you are doing local development, there are two ways to test your changes:

1. Run the MCP inspector to test your changes. See [Debugging](#debugging) for run instructions.

2. Test using the Claude desktop app. Add the following to your `claude_desktop_config.json`:

### Docker

```json
{
  "mcpServers": {
    "interns": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "dynamicwf"
      ]
    }
  }
}
```

### UVX
```json
{
"mcpServers": {
  "interns": {
    "command": "uv",
    "args": [ 
      "--directory",
      "/<path to servers>/dynamicwf",
      "run",
      "dynamicwf"
    ]
  }
}
```

## Build

Docker build:

```bash
cd src/dynamicwf
docker build -t dynamicwf .
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
