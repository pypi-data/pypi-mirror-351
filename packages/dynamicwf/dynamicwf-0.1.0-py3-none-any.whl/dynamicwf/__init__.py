"""
DynamicWF - Adobe Interns MCP Server
"""

import click
from pathlib import Path
import logging
import sys
from .server import serve

__version__ = "0.1.0"

@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose: int = 0) -> None:
    """Adobe Interns MCP Server - Intern information for MCP"""
    import asyncio

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(serve())

# Export public API
__all__ = ["main", "serve"]

if __name__ == "__main__":
    main()
