import asyncio
import logging
import os
import sys

import click

from airflow_mcp_server.config import AirflowConfig
from airflow_mcp_server.server_safe import serve as serve_safe
from airflow_mcp_server.server_unsafe import serve as serve_unsafe


@click.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@click.option("--safe", "-s", is_flag=True, help="Use only read-only tools")
@click.option("--unsafe", "-u", is_flag=True, help="Use all tools (default)")
@click.option("--static-tools", is_flag=True, help="Use static tools instead of hierarchical discovery")
@click.option("--base-url", help="Airflow API base URL")
@click.option("--auth-token", help="Authentication token (JWT)")
def main(verbose: int, safe: bool, unsafe: bool, static_tools: bool, base_url: str = None, auth_token: str = None) -> None:
    """MCP server for Airflow"""
    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)

    config_base_url = os.environ.get("AIRFLOW_BASE_URL") or base_url
    config_auth_token = os.environ.get("AUTH_TOKEN") or auth_token

    try:
        config = AirflowConfig(base_url=config_base_url, auth_token=config_auth_token)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)

    if safe and unsafe:
        raise click.UsageError("Options --safe and --unsafe are mutually exclusive")
    elif safe:
        asyncio.run(serve_safe(config, static_tools=static_tools))
    elif unsafe:
        asyncio.run(serve_unsafe(config, static_tools=static_tools))
    else:
        asyncio.run(serve_unsafe(config, static_tools=static_tools))


if __name__ == "__main__":
    main()
