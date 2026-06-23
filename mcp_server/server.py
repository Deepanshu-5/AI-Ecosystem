from mcp.server.fastmcp import FastMCP
from memory.memory_service import recall

mcp = FastMCP("KnowledgeBase")


@mcp.tool()
def ping() -> str:
    return "pong"


@mcp.tool()
def recall_memory(
    query: str
) -> str:

    memories = recall(query)

    return "\n".join(memories)


if __name__ == "__main__":
    print("SERVER STARTING")
    mcp.run()