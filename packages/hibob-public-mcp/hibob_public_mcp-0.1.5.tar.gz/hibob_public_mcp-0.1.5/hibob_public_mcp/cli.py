from .mcp_server import mcp

def main():
    mcp.server(transport="stdio")