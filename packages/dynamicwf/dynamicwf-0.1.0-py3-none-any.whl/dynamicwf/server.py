import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from enum import Enum
from pydantic import BaseModel

class InternFilter(BaseModel):
    name_contains: str | None = None

class InternsTool(str, Enum):
    GET_INTERNS = "get_adobe_interns"
    FILTER_INTERNS = "filter_adobe_interns"

def get_adobe_interns() -> list[str]:
    """Return a list of current interns at Adobe"""
    interns = [
        "Ajay Paliwal",
        "Abhijeet Agarwal",
        "Siddhartha Rajeev",
        "Shrey Patel"
    ]
    return interns

def filter_adobe_interns(name_contains: str | None = None) -> list[str]:
    """Filter Adobe interns by name"""
    interns = get_adobe_interns()
    if name_contains:
        return [intern for intern in interns if name_contains.lower() in intern.lower()]
    return interns

async def serve() -> None:
    logger = logging.getLogger(__name__)
    server = Server("adobe-interns")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=InternsTool.GET_INTERNS,
                description="Gets a list of all current interns at Adobe",
                inputSchema={},
            ),
            Tool(
                name=InternsTool.FILTER_INTERNS,
                description="Filters Adobe interns by name",
                inputSchema=InternFilter.schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        match name:
            case InternsTool.GET_INTERNS:
                interns = get_adobe_interns()
                return [TextContent(
                    type="text",
                    text=f"Current Adobe interns:\n" + "\n".join(f"- {intern}" for intern in interns)
                )]

            case InternsTool.FILTER_INTERNS:
                name_contains = arguments.get("name_contains")
                filtered_interns = filter_adobe_interns(name_contains)
                
                if name_contains:
                    return [TextContent(
                        type="text",
                        text=f"Adobe interns containing '{name_contains}':\n" + 
                             "\n".join(f"- {intern}" for intern in filtered_interns)
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"All Adobe interns:\n" + 
                             "\n".join(f"- {intern}" for intern in filtered_interns)
                    )]

            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
