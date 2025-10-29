"""
MCP Service module for managing Model Context Protocol connections.
Handles connection lifecycle, retries, and multiple MCP server support.
"""

import asyncio
import logging
from typing import List, Optional
from agno.tools.mcp import MCPTools
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
from config import config

logger = logging.getLogger(__name__)


class MCPService:
    """Service for managing MCP (Model Context Protocol) connections."""

    def __init__(self):
        """Initialize the MCP service."""
        self._mcp_tools_list: List[MCPTools] = []
        self._connection_lock = asyncio.Lock()

    @property
    def tools(self) -> List[MCPTools]:
        """Get the list of connected MCP tools."""
        return self._mcp_tools_list

    @property
    def is_connected(self) -> bool:
        """Check if any MCP connections are active."""
        return len(self._mcp_tools_list) > 0

    async def connect_all(self) -> None:
        """
        Connect to all configured MCP servers.

        Raises:
            Exception: If no MCP servers could be connected.
        """
        async with self._connection_lock:
            self._mcp_tools_list = await self._open_connections()
            logger.info(f"✓ Connected to {len(self._mcp_tools_list)} MCP server(s)")

    async def ensure_connected(self) -> None:
        """Ensure MCP connections are active, reconnect if needed."""
        if not self.is_connected:
            logger.warning("MCP connections not available, attempting to reconnect...")
            await self.connect_all()

    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        async with self._connection_lock:
            for mcp_tools in self._mcp_tools_list:
                try:
                    await mcp_tools.close()
                except Exception as e:
                    logger.error(f"Error closing MCP connection: {str(e)}")

            self._mcp_tools_list = []
            logger.info("✓ Disconnected from all MCP servers")

    async def _open_connections(self) -> List[MCPTools]:
        """
        Open connections to all configured MCP servers.

        Returns:
            List of connected MCPTools instances.

        Raises:
            Exception: If no servers could be connected.
        """
        mcp_list = []

        # Connect to Alpha Vantage MCP
        alpha_vantage_tools = await self._connect_alpha_vantage()
        if alpha_vantage_tools:
            mcp_list.append(alpha_vantage_tools)
            logger.info("✓ Alpha Vantage MCP connected")

        # Add more MCP servers here as they become available
        # Example:
        # other_tools = await self._connect_other_service()
        # if other_tools:
        #     mcp_list.append(other_tools)

        if not mcp_list:
            raise Exception("Failed to connect to any MCP servers")

        return mcp_list

    async def _connect_alpha_vantage(self) -> Optional[MCPTools]:
        """
        Connect to Alpha Vantage MCP server with retry logic using tenacity.

        Returns:
            MCPTools instance if successful, None otherwise.
        """
        mcp_url = config.get_alpha_vantage_url()
        if not mcp_url:
            logger.error("Alpha Vantage API key not configured")
            return None

        @retry(
            stop=stop_after_attempt(config.MCP_CONNECTION_RETRIES),
            wait=wait_exponential(
                multiplier=1,
                min=1,
                max=config.MCP_RETRY_BACKOFF_BASE ** (config.MCP_CONNECTION_RETRIES - 1)
            ),
            retry=retry_if_exception_type(Exception),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO)
        )
        async def _attempt_connection() -> MCPTools:
            """Attempt to connect to Alpha Vantage MCP."""
            mcp_tools = MCPTools(
                transport='streamable-http',
                url=mcp_url
            )
            await mcp_tools.connect()
            logger.info("✓ Alpha Vantage MCP connected successfully")
            return mcp_tools

        try:
            return await _attempt_connection()
        except Exception as e:
            logger.error(
                f"Failed to connect to Alpha Vantage after "
                f"{config.MCP_CONNECTION_RETRIES} attempts: {str(e)}"
            )
            return None

    # Add methods for other MCP servers as needed
    # async def _connect_other_service(self) -> Optional[MCPTools]:
    #     """Connect to another MCP service."""
    #     pass


# Create a singleton instance
mcp_service = MCPService()
