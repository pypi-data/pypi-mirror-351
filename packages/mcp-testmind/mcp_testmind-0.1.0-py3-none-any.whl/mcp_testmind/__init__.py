import argparse
from .server import mcp

def main():
    """MCP TestRail: Facilitates Goose interactions with Testrail."""
    parser = argparse.ArgumentParser(
        description="Adds Testrail interaction support to Goose!"
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()