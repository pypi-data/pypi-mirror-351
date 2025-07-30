"""
Bark MCP Server implementation.
"""
import os
import logging
from typing import Optional, Dict, Any

import requests
from fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("bark-mcp")

class BarkMcpServer:
    """MCP server that talks to Bark notification server for iOS."""

    def __init__(self):
        # Get environment variables
        self.bark_server_url = os.environ.get("BARK_SERVER_URL")
        self.bark_api_key = os.environ.get("BARK_API_KEY")
        
        # Validate environment variables
        if not self.bark_server_url:
            raise ValueError("BARK_SERVER_URL environment variable is required")
        if not self.bark_api_key:
            raise ValueError("BARK_API_KEY environment variable is required")
        
        # Create the FastMCP server
        self.mcp = FastMCP(name="BarkNotificationServer")
        
        # Register tools
        @self.mcp.tool()
        async def notify(title: Optional[str] = None, content: str = "", url: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
            """Send a notification to an iOS device via Bark.
            
            Args:
                title: Title of the notification (optional)
                content: Content of the notification (required)
                url: URL to open when the notification is tapped (optional)
                ctx: MCP context (automatically injected)
                
            Returns:
                Dict containing the response from the Bark server
            """
            if ctx:
                await ctx.info(f"Sending notification - Title: {title}, Content: {content}, URL: {url}")
            else:
                logger.info("Sending notification - Title: %s, Content: %s, URL: %s", title, content, url)
            
            return await self._send_notification(title, content, url, ctx)
        
        logger.info("Bark MCP Server initialized with server URL: %s", self.bark_server_url)

    async def _send_notification(self, title: Optional[str] = None, content: str = "", url: Optional[str] = None, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Send a notification to an iOS device via Bark.
        
        Args:
            title: Title of the notification (optional)
            content: Content of the notification (required)
            url: URL to open when the notification is tapped (optional)
            ctx: MCP context (optional)
            
        Returns:
            Dict containing the response from the Bark server
        """
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
            
            if ctx:
                await ctx.info(f"Sending request to: {request_url}")
            else:
                logger.info("Sending request to: %s", request_url)
                
            # Send the request to the Bark server
            response = requests.get(request_url, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if ctx:
                await ctx.info("Notification sent successfully")
            else:
                logger.info("Notification sent successfully: %s", result)
            
            return {
                "success": True,
                "message": "Notification sent successfully",
                "response": result
            }
            
        except requests.RequestException as e:
            error_message = f"Failed to send notification: {str(e)}"
            
            if ctx:
                await ctx.error(error_message)
            else:
                logger.error(error_message)
            
            return {
                "success": False,
                "message": error_message
            }
    
    def start(self):
        """Start the MCP server."""
        self.mcp.run(transport="stdio")

def create_server() -> BarkMcpServer:
    """Create and return a new Bark MCP server instance."""
    return BarkMcpServer()
