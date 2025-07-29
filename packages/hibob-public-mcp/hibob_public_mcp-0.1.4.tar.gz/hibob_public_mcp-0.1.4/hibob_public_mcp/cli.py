from .mcp_server import mcp

def main():
    mcp.serve(transport="stdio")