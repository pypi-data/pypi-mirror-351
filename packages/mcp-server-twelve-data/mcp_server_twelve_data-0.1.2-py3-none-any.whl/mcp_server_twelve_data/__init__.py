from typing import Literal

import click
import logging
import sys

from .server import serve


@click.command()
@click.option("-v", "--verbose", count=True)
@click.option("-t", "--transport", default="stdio", help="stdio, streamable-http")
def main(verbose: bool, transport: Literal["stdio", "sse", "streamable-http"] = "stdio") -> None:
    """MCP Git Server - Git functionality for MCP"""
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    serve(api_base="https://api.twelvedata.com", transport=transport)


if __name__ == "__main__":
    main()