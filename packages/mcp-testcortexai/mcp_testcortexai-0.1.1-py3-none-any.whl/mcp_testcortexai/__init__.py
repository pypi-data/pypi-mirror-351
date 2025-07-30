import argparse
from .server import mcp

def main():
    """MCP TestCortexAI: TestCortex AI is a specialized quality engineering tool built on top of the Goose AI platform."""
    parser = argparse.ArgumentParser(
        description="I’m your intelligent assistant for orchestrating end-to-end quality engineering!"
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()