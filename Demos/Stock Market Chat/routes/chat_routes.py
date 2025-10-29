"""
Chat routes for the Stock Market Chat application.
Handles all chat-related HTTP endpoints.
"""

import uuid
import logging
from quart import request, Response, Blueprint
from services.mcp_service import mcp_service
from services.agent_service import AgentService
from utils.error_handler import error_handler, validate_input, ValidationError

logger = logging.getLogger(__name__)

# Create blueprint for chat routes
chat_bp = Blueprint('chat', __name__)


def create_chat_routes(agent_service: AgentService) -> Blueprint:
    """
    Create and configure chat routes.

    Args:
        agent_service: The agent service instance to use

    Returns:
        Configured Blueprint
    """

    @chat_bp.route('/streaming_chat', methods=['GET'])
    async def streaming_chat():
        """
        Handle streaming chat requests.

        Query Parameters:
            input: The user's message

        Headers:
            X-Session-ID: Optional session identifier for conversation continuity

        Returns:
            Streaming text response with chat completion
        """
        session_id = None

        try:
            # Get or create session ID
            session_id = request.headers.get('X-Session-ID') or str(uuid.uuid4())

            # Get and validate user input
            user_input = request.args.get('input')
            is_valid, validation_error = validate_input(user_input)
            if not is_valid:
                raise ValidationError(validation_error)

            logger.info(f"Session {session_id[:8]}: Processing query: {user_input[:50]}...")

            # Ensure MCP connection is active
            await mcp_service.ensure_connected()

            # Create agent for this session
            agent = agent_service.create_agent(
                session_id=session_id,
                mcp_tools_list=mcp_service.tools
            )

            # Generate streaming response
            output = agent.arun(user_input, stream=True)

            async def generate():
                """Generator for streaming response chunks."""
                try:
                    async for chunk in output:
                        if chunk.event == 'RunContent':
                            yield chunk.content
                except Exception as e:
                    error_msg = error_handler.handle_streaming_error(e)
                    yield error_msg

            # Create streaming response
            response = Response(generate(), mimetype='text/plain; charset=utf-8')
            response.headers['X-Session-ID'] = session_id

            return response

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            output = f"Invalid input: {str(e)}"
            response = Response(output, mimetype='text/plain; charset=utf-8', status=400)
            if session_id:
                response.headers['X-Session-ID'] = session_id
            return response

        except Exception as e:
            error_handler.log_error(e, "streaming_chat")
            output = error_handler.get_user_friendly_message(e)

            response = Response(output, mimetype='text/plain; charset=utf-8', status=500)
            if session_id:
                response.headers['X-Session-ID'] = session_id
            return response

    return chat_bp
