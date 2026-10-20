import os
from fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from notes_app import add_note, delete_note, list_notes

load_dotenv()

mcp = FastMCP(name="Notes App")


@mcp.tool()
def list_my_notes() -> list[dict]:
    """List all saved notes."""
    return list_notes(owner="local")


@mcp.tool()
def add_a_note(text: str) -> dict:
    """Save a new note."""
    return add_note(owner="local", text=text)


@mcp.tool()
def delete_a_note(note_id: int) -> str:
    """Delete a note by id."""
    return "deleted" if delete_note(owner="local", note_id=note_id) else "none"


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",                       # bind to all interfaces (required on Render)
        port=int(os.getenv("PORT", 8000)),     # Render injects $PORT; fallback to 8000 locally
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]
    )


# MCP client config (HTTP):
# {
#     "mcpServers": {
#         "notes": {
#             "url": "http://localhost:8000/mcp"
#         }
#     }
# }
