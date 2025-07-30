"""
Command-line interface for the Bark MCP server.
"""
import os
import sys
import logging
import argparse
from dotenv import load_dotenv

from bark_mcp.server import create_server

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("bark-mcp-cli")

def setup_environment(env_file=None, debug=False):
    """
    Set up the environment variables and logging.
    
    Args:
        env_file: Path to .env file
        debug: Whether to enable debug logging
    """
    # Set up logging level
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Load environment variables
    if env_file:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            logger.info(f"Loaded environment variables from {env_file}")
        else:
            logger.warning(f"Environment file {env_file} not found")
    else:
        # Try to load from .env in the current directory
        if os.path.exists(".env"):
            load_dotenv()
            logger.info("Loaded environment variables from .env")

def main():
    """Main entry point for the Bark MCP CLI."""
    parser = argparse.ArgumentParser(description="Bark MCP Server")
    parser.add_argument("--env-file", type=str, help="Path to .env file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment(args.env_file, args.debug)
    
    # Check for required environment variables
    if not os.environ.get("BARK_SERVER_URL"):
        logger.error("BARK_SERVER_URL environment variable is required")
        sys.exit(1)
    
    if not os.environ.get("BARK_API_KEY"):
        logger.error("BARK_API_KEY environment variable is required")
        sys.exit(1)
    
    try:
        # Create and start the server
        logger.info("Starting Bark MCP Server...")
        server = create_server()
        server.start()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.exception(f"Error starting server: {e}")
        sys.exit(1)
    
    logger.info("Server stopped")



if __name__ == "__main__":
    main()
