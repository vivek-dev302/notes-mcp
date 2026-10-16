from fastmcp import FastMCP

from notes_app import add_note, delete_note, list_notes

mcp = FastMCP("notes")


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


# http method running on localhost:8000/mcp
# if __name__ == "__main__":
#     mcp.run(transport="http", host="0.0.0.0", port=8000)

# agents mcp config
# {
#     "mcpServers": {
#         "notes": {
#           "url": "http://localhost:8000/mcp"
#          }
#     }
# }


# stdio method
if __name__ == "__main__":
    mcp.run()

# agents mcp config
# {
#     "mcpServers": {
#         "notes-local": {
#             "command": "uv",
#             "args": [
#                 "run",
#                 " -- directory",
#                 "/Users/timruscica/descope-mcp-video",
#                 "v1_local.py"
#             ]
#         }
#     }
# }
