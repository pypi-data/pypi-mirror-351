import logging
from typing import Sequence
from mcp.server import Server
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import (
    ClientCapabilities,
    TextContent,
    Tool,
    ListRootsResult,
    RootsCapability,
)
from enum import Enum
from pydantic import BaseModel
import click
import sys

class InternsTool(str, Enum):
    GET_INTERNS = "get_adobe_interns"

class GetInternsInput(BaseModel):
    year: int

def get_adobe_interns(year: int) -> list[str]:
    """Return a list of current interns at Adobe for a given year"""
    # Example: hardcoded data for demonstration
    interns_by_year = {
        2023: [
            "Ajay Paliwal",
            "Abhijeet Agarwal",
            "Siddhartha Rajeev",
            "Shrey Patel"
        ],
        2022: [
            "Jane Doe",
            "John Smith"
        ]
    }
    return interns_by_year.get(year, [])


async def serve() -> None:
    print({"message": "Starting latest DynamicWF MCP server"})
    logger = logging.getLogger(__name__)
    logger.info("Starting DynamicWF MCP server")

    server = Server("dynamicwf")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=InternsTool.GET_INTERNS,
                description="Get a list of all current Adobe interns for a given year",
                inputSchema=GetInternsInput.schema(),
            ),
        ]

    async def list_roots() -> Sequence[str]:
        if not isinstance(server.request_context.session, ServerSession):
            raise TypeError("server.request_context.session must be a ServerSession")

        if not server.request_context.session.check_client_capability(
            ClientCapabilities(roots=RootsCapability())
        ):
            return []

        roots_result: ListRootsResult = await server.request_context.session.list_roots()
        logger.debug(f"Roots result: {roots_result}")
        return []

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        match name:
            case InternsTool.GET_INTERNS:
                input_data = GetInternsInput(**arguments)
                interns = get_adobe_interns(input_data.year)
                return [TextContent(
                    type="text",
                    text=f"Current Adobe interns for {input_data.year}:\n" +
                        ("\n".join(f"- {intern}" for intern in interns) if interns else "No data available.")
                )]

            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)

@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose: bool) -> None:
    """DynamicWF MCP Server - Intern information for MCP"""
    import asyncio

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(serve())

# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(serve())