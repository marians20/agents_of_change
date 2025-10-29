"""
Stock Market Chat Application - Main entry point.

A modular, production-ready chatbot application for stock market analysis
using OpenAI and Alpha Vantage MCP (Model Context Protocol).

Architecture:
- config.py: Centralized configuration management
- services/: Business logic layer (MCP, Agent services)
- routes/: HTTP endpoint handlers
- utils/: Utility functions and error handling
"""

import logging
from quart import Quart, render_template
from agno.db.in_memory import InMemoryDb

from config import config
from services.mcp_service import mcp_service
from services.agent_service import AgentService
from routes.chat_routes import create_chat_routes
from utils.error_handler import ConfigurationError

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app() -> Quart:
    """
    Application factory pattern for creating the Quart app.

    Returns:
        Configured Quart application instance
    """
    # Validate configuration
    is_valid, errors = config.validate()
    if not is_valid:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        raise ConfigurationError("Invalid configuration. Check logs for details.")

    # Create Quart application
    app = Quart(__name__)

    # Initialize services
    memory_db = InMemoryDb()
    agent_service = AgentService(memory_db)

    # Register routes
    @app.route('/', methods=['GET'])
    async def index():
        """Serve the main chat interface."""
        return await render_template('index.html')

    # Register chat blueprint
    chat_blueprint = create_chat_routes(agent_service)
    app.register_blueprint(chat_blueprint)

    # Startup event - Connect to MCP servers
    @app.before_serving
    async def startup():
        """Initialize MCP connections before serving requests."""
        logger.info("Starting Stock Market Chat application...")
        logger.info(f"Using model: {config.AGENT_MODEL}")
        logger.info(f"Agent history runs: {config.AGENT_HISTORY_RUNS}")

        try:
            await mcp_service.connect_all()
            logger.info("✓ Application startup complete")
        except Exception as e:
            logger.error(f"Failed to start application: {str(e)}")
            raise

    # Shutdown event - Clean up MCP connections
    @app.after_serving
    async def shutdown():
        """Clean up resources when shutting down."""
        logger.info("Shutting down Stock Market Chat application...")
        await mcp_service.disconnect_all()
        logger.info("✓ Application shutdown complete")

    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    """
    Run the application in development mode.

    For production, use: hypercorn app:app
    """
    logger.info(f"Starting development server on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
