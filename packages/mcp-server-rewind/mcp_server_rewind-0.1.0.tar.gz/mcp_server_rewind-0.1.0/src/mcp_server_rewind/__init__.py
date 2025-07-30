import logging
import sys
from pathlib import Path

import click

from .server import serve


@click.command()
@click.option(
    "--base-path",
    "-b",
    help="Base path for Rewind chunks directory",
    envvar="REWIND_BASE_PATH",
    default=str(Path.home() / "Library/Application Support/com.memoryvault.MemoryVault/chunks"),
)
@click.option(
    "--timezone",
    "-t",
    help="Timezone for timestamp interpretation",
    envvar="REWIND_TIMEZONE",
    default=None,
)
@click.option("-v", "--verbose", count=True)
def main(base_path: str, timezone: str | None, verbose: bool) -> None:
    """MCP Rewind Server - Query your Rewind AI screen recording transcripts"""
    import asyncio
    import os

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)

    # Set environment variables for the server
    os.environ["REWIND_BASE_PATH"] = base_path
    if timezone:
        os.environ["REWIND_TIMEZONE"] = timezone

    asyncio.run(serve())


if __name__ == "__main__":
    main()