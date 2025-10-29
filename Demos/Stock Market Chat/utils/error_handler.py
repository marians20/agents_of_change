"""
Error handling utilities for the Stock Market Chat application.
Provides consistent error messages and handling across the application.
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling for the application."""

    @staticmethod
    def get_user_friendly_message(error: Exception) -> str:
        """
        Convert an exception into a user-friendly error message.

        Args:
            error: The exception to process

        Returns:
            User-friendly error message
        """
        error_str = str(error).lower()

        # Context length exceeded
        if "context_length_exceeded" in error_str or "maximum context length" in error_str:
            return (
                "The conversation history has exceeded the maximum token limit. "
                "Please refresh the page to start a new conversation."
            )

        # Network/connectivity issues
        if "network" in error_str or "connection" in error_str:
            return (
                "I'm experiencing connectivity issues with the data provider. "
                "This might be due to rate limits (free tier allows 5 calls/minute, 25/day). "
                "Please wait a moment and try again."
            )

        # Rate limiting
        if "rate limit" in error_str:
            return (
                "API rate limit reached. Free Alpha Vantage tier allows 5 requests per minute "
                "and 25 per day. Please wait a few minutes before trying again."
            )

        # Authentication/forbidden
        if "403" in error_str or "forbidden" in error_str:
            return (
                "Access denied by the API. Please verify your Alpha Vantage API key is valid."
            )

        # Unauthorized
        if "401" in error_str or "unauthorized" in error_str:
            return (
                "Authentication failed. Please check your API keys in the .env file."
            )

        # Timeout
        if "timeout" in error_str:
            return (
                "Request timed out. The API might be experiencing high load. "
                "Please try again in a moment."
            )

        # Default error message
        return (
            f"I'm sorry, but something went wrong: {str(error)}\n\n"
            "Please try rephrasing your question or wait a moment before trying again."
        )

    @staticmethod
    def log_error(error: Exception, context: str = "") -> None:
        """
        Log an error with context.

        Args:
            error: The exception to log
            context: Additional context about where the error occurred
        """
        if context:
            logger.error(f"Error in {context}: {str(error)}", exc_info=True)
        else:
            logger.error(f"Error: {str(error)}", exc_info=True)

    @staticmethod
    def handle_streaming_error(error: Exception) -> str:
        """
        Handle errors that occur during streaming responses.

        Args:
            error: The exception that occurred

        Returns:
            Error message formatted for streaming output
        """
        error_str = str(error)
        logger.error(f"Error during streaming: {error_str}")

        # Check for specific error types
        if "context_length_exceeded" in error_str or "maximum context length" in error_str:
            return (
                "\n\n**Context limit reached**. "
                "The conversation history has become too long. "
                "Please start a new conversation or refresh the page to continue."
            )

        return f"\n\n**Error**: {error_str}\n\nPlease try again or rephrase your question."


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


def validate_input(user_input: str) -> Tuple[bool, str]:
    """
    Validate user input.

    Args:
        user_input: The input to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not user_input:
        return False, "No input provided"

    if len(user_input.strip()) == 0:
        return False, "Input cannot be empty"

    if len(user_input) > 10000:
        return False, "Input is too long (maximum 10,000 characters)"

    return True, ""


# Create a singleton instance
error_handler = ErrorHandler()
