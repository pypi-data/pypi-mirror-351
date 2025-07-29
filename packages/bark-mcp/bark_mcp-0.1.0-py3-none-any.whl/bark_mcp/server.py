"""
Bark MCP Server implementation.
"""
import os
import logging
from typing import Optional, Dict, Any

import requests
from fastmcp import McpServer, Tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("bark-mcp")

class BarkMcpServer(McpServer):
    """MCP server that talks to Bark notification server for iOS."""

    def __init__(self):
        super().__init__()
        
        # Get environment variables
        self.bark_server_url = os.environ.get("BARK_SERVER_URL")
        self.bark_api_key = os.environ.get("BARK_API_KEY")
        
        # Validate environment variables
        if not self.bark_server_url:
            raise ValueError("BARK_SERVER_URL environment variable is required")
        if not self.bark_api_key:
            raise ValueError("BARK_API_KEY environment variable is required")
        
        # Register tools
        self.register_tool(
            Tool(
                name="notify",
                description="Send a notification to an iOS device via Bark",
                parameters={
                    "title": {
                        "type": "string",
                        "description": "Title of the notification (optional)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content of the notification (required)"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to open when the notification is tapped (optional)"
                    }
                },
                required_parameters=["content"],
                handler=self.notify
            )
        )
        
        logger.info("Bark MCP Server initialized with server URL: %s", self.bark_server_url)

    async def notify(self, title: Optional[str] = None, content: str = "", url: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification to an iOS device via Bark.
        
        Args:
            title: Title of the notification (optional)
            content: Content of the notification (required)
            url: URL to open when the notification is tapped (optional)
            
        Returns:
            Dict containing the response from the Bark server
        """
        logger.info("Sending notification - Title: %s, Content: %s, URL: %s", title, content, url)
        
        try:
            # Build the request URL based on available parameters
            base_url = self.bark_server_url.rstrip('/')
            
            if title:
                # Format: /{bark-key}/{title}/{content}
                request_url = f"{base_url}/{self.bark_api_key}/{title}/{content}"
            else:
                # Format: /{bark-key}/{content}
                request_url = f"{base_url}/{self.bark_api_key}/{content}"
            
            # Add URL parameter if provided
            params = {}
            if url:
                params['url'] = url
                
            # Send the request to the Bark server
            response = requests.get(request_url, params=params)
            response.raise_for_status()
            
            result = response.json()
            logger.info("Notification sent successfully: %s", result)
            
            return {
                "success": True,
                "message": "Notification sent successfully",
                "response": result
            }
            
        except requests.RequestException as e:
            error_message = f"Failed to send notification: {str(e)}"
            logger.error(error_message)
            
            return {
                "success": False,
                "message": error_message
            }

def create_server() -> BarkMcpServer:
    """Create and return a new Bark MCP server instance."""
    return BarkMcpServer()
