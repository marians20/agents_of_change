"""
Configuration module for Stock Market Chat application.
Centralizes all configuration settings and environment variables.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""

    # Application settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', '5000'))

    # API Keys
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Agent settings
    AGENT_MODEL = os.getenv('AGENT_MODEL', 'gpt-4o-mini')
    AGENT_TEMPERATURE = float(os.getenv('AGENT_TEMPERATURE', '0.3'))
    AGENT_HISTORY_RUNS = int(os.getenv('AGENT_HISTORY_RUNS', '3'))

    # MCP settings
    MCP_CONNECTION_RETRIES = int(os.getenv('MCP_CONNECTION_RETRIES', '3'))
    MCP_RETRY_BACKOFF_BASE = int(os.getenv('MCP_RETRY_BACKOFF_BASE', '2'))

    # Alpha Vantage MCP
    ALPHA_VANTAGE_MCP_URL_TEMPLATE = 'https://mcp.alphavantage.co/mcp?apikey={api_key}'

    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate required configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not cls.ALPHA_VANTAGE_API_KEY:
            errors.append(
                "ALPHA_VANTAGE_API_KEY not set. "
                "Get a free API key at https://www.alphavantage.co/support/#api-key"
            )

        if not cls.OPENAI_API_KEY:
            errors.append(
                "OPENAI_API_KEY not set. "
                "Get your API key at https://platform.openai.com/api-keys"
            )

        return len(errors) == 0, errors

    @classmethod
    def get_alpha_vantage_url(cls) -> Optional[str]:
        """Get the Alpha Vantage MCP URL with API key."""
        if not cls.ALPHA_VANTAGE_API_KEY:
            return None
        return cls.ALPHA_VANTAGE_MCP_URL_TEMPLATE.format(
            api_key=cls.ALPHA_VANTAGE_API_KEY
        )


# Create a singleton instance
config = Config()
