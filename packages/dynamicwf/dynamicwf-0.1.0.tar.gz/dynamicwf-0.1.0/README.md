# DynamicWF

A specialized MCP server for Adobe intern information with filtering capabilities.

## Installation

```bash
pip install dynamicwf
```

## Usage

After installation, you can run the server using either:

```bash
# Using the installed command
dynamicwf

# Or as a Python module
python -m dynamicwf
```

### Command Line Options

```bash
# Run with verbose logging
dynamicwf -v

# Run with debug logging
dynamicwf -vv
```

### API Usage

You can also use the package programmatically:

```python
import asyncio
from dynamicwf import serve

# Run the server
asyncio.run(serve())
```

## Features

- Get a list of all Adobe interns
- Filter interns by name
- Simple CLI interface with logging options
- REST API for integration with other services

## API Endpoints

- `GET /interns` - Get a list of all interns
- `GET /interns?name=John` - Filter interns by name

## Development

To install in development mode:

```bash
pip install -e .
```

Running tests:

```bash
python -m unittest discover -s tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
