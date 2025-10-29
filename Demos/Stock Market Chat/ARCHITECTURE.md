# Stock Market Chat - Refactored Architecture

## Overview

The Stock Market Chat application has been refactored following best practices for modularity, maintainability, and scalability.

## Architecture Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Services are injected rather than imported globally
3. **Application Factory Pattern**: App creation is encapsulated in a factory function
4. **Service Layer Pattern**: Business logic separated from HTTP handling
5. **Configuration Management**: Centralized configuration with validation
6. **Error Handling**: Consistent error handling across the application

## Project Structure

```
Stock Market Chat/
├── app_new.py                 # Main application entry point (NEW)
├── app.py                     # Legacy application (DEPRECATED)
├── agents.py                  # Legacy agents (DEPRECATED)
├── config.py                  # Configuration management (NEW)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .env.template              # Environment template
│
├── services/                  # Business logic layer (NEW)
│   ├── __init__.py
│   ├── mcp_service.py        # MCP connection management
│   └── agent_service.py      # Agent creation and configuration
│
├── routes/                    # HTTP route handlers (NEW)
│   ├── __init__.py
│   └── chat_routes.py        # Chat endpoints
│
├── utils/                     # Utility functions (NEW)
│   ├── __init__.py
│   └── error_handler.py      # Error handling utilities
│
├── templates/                 # Jinja2 templates
│   └── index.html
│
└── static/                    # Static assets
    ├── main.css
    ├── script.js
    ├── user.jpg
    └── chatbot.jpg
```

## Module Descriptions

### `app_new.py` - Application Entry Point
- Application factory pattern
- Initializes all services
- Registers routes
- Manages application lifecycle (startup/shutdown)
- **Migration**: Rename to `app.py` after testing

### `config.py` - Configuration Management
- Centralized configuration
- Environment variable loading
- Configuration validation
- Type-safe configuration access
- **Key Features**:
  - Validates required API keys
  - Provides sensible defaults
  - Type conversion (int, float, bool)

### `services/mcp_service.py` - MCP Connection Service
- Manages Model Context Protocol connections
- Handles connection lifecycle
- Implements retry logic with exponential backoff
- Supports multiple MCP servers
- **Singleton Pattern**: `mcp_service` instance

### `services/agent_service.py` - Agent Creation Service
- Creates and configures AI agents
- Encapsulates agent instructions
- Manages agent lifecycle per session
- **No Singleton**: New agent per request

### `routes/chat_routes.py` - Chat Route Handlers
- HTTP endpoint logic
- Request validation
- Session management
- Streaming response handling
- **Blueprint Pattern**: Modular route registration

### `utils/error_handler.py` - Error Handling
- Consistent error messages
- User-friendly error translation
- Error logging
- Custom exceptions
- Input validation

## Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Required
ALPHA_VANTAGE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Optional (with defaults)
DEBUG=True
HOST=127.0.0.1
PORT=5000
AGENT_MODEL=gpt-4o-mini
AGENT_TEMPERATURE=0.3
AGENT_HISTORY_RUNS=3
LOG_LEVEL=INFO
MCP_CONNECTION_RETRIES=3
```

### Configuration Access

```python
from config import config

# Access configuration
api_key = config.ALPHA_VANTAGE_API_KEY
model = config.AGENT_MODEL

# Validate configuration
is_valid, errors = config.validate()
```

## Service Layer

### MCP Service Usage

```python
from services.mcp_service import mcp_service

# Connect to all MCP servers
await mcp_service.connect_all()

# Ensure connection is active
await mcp_service.ensure_connected()

# Get tools
tools = mcp_service.tools

# Disconnect
await mcp_service.disconnect_all()
```

### Agent Service Usage

```python
from services.agent_service import AgentService
from agno.db.in_memory import InMemoryDb

# Initialize service
memory_db = InMemoryDb()
agent_service = AgentService(memory_db)

# Create agent
agent = agent_service.create_agent(
    session_id="session-123",
    mcp_tools_list=mcp_service.tools
)

# Use agent
output = agent.arun("What's the price of AAPL?", stream=True)
```

## Error Handling

### Custom Exceptions

```python
from utils.error_handler import ValidationError, ConfigurationError

# Validation error
raise ValidationError("Invalid input")

# Configuration error
raise ConfigurationError("API key missing")
```

### Error Messages

```python
from utils.error_handler import error_handler

# Get user-friendly message
message = error_handler.get_user_friendly_message(exception)

# Log error with context
error_handler.log_error(exception, "streaming_chat")

# Handle streaming errors
stream_message = error_handler.handle_streaming_error(exception)
```

## Migration Guide

### From Old to New Architecture

1. **Test the new app**:
   ```bash
   python app_new.py
   ```

2. **If successful, replace old app**:
   ```bash
   # Backup old files
   mv app.py app_old.py
   mv agents.py agents_old.py

   # Activate new app
   mv app_new.py app.py
   ```

3. **Clean up** (after confirming everything works):
   ```bash
   rm app_old.py agents_old.py
   ```

## Adding New Features

### Adding a New MCP Server

Edit `services/mcp_service.py`:

```python
async def _open_connections(self) -> List[MCPTools]:
    mcp_list = []

    # Existing Alpha Vantage
    alpha_tools = await self._connect_alpha_vantage()
    if alpha_tools:
        mcp_list.append(alpha_tools)

    # Add new MCP
    new_tools = await self._connect_new_service()
    if new_tools:
        mcp_list.append(new_tools)

    return mcp_list

async def _connect_new_service(self) -> Optional[MCPTools]:
    """Connect to new MCP service."""
    # Implementation here
    pass
```

### Adding a New Route

Create new blueprint in `routes/`:

```python
# routes/analytics_routes.py
from quart import Blueprint

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics', methods=['GET'])
async def get_analytics():
    # Implementation
    pass
```

Register in `app_new.py`:

```python
from routes.analytics_routes import analytics_bp
app.register_blueprint(analytics_bp)
```

### Adding New Configuration

Edit `config.py`:

```python
class Config:
    # Add new setting
    NEW_SETTING = os.getenv('NEW_SETTING', 'default_value')
```

## Testing

### Manual Testing

```bash
# Start the application
python app_new.py

# Test in browser
open http://localhost:5000

# Test API endpoint
curl "http://localhost:5000/streaming_chat?input=test" \
  -H "X-Session-ID: test-123"
```

### Unit Testing Structure (Future)

```
tests/
├── test_config.py
├── test_mcp_service.py
├── test_agent_service.py
├── test_error_handler.py
└── test_routes.py
```

## Production Deployment

### Using Hypercorn (Recommended)

```bash
# Install hypercorn
pip install hypercorn

# Run with hypercorn
hypercorn app_new:app --bind 0.0.0.0:8000
```

### Environment Configuration

```bash
# Production .env
DEBUG=False
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000
```

### Docker Support (Future)

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["hypercorn", "app_new:app", "--bind", "0.0.0.0:8000"]
```

## Benefits of Refactoring

1. **Maintainability**: Clear module boundaries make code easier to understand and modify
2. **Testability**: Services can be unit tested independently
3. **Scalability**: Easy to add new features without touching existing code
4. **Reliability**: Centralized error handling and validation
5. **Configuration**: Environment-specific settings without code changes
6. **Documentation**: Self-documenting code structure

## Best Practices Applied

- ✅ Single Responsibility Principle
- ✅ Dependency Injection
- ✅ Factory Pattern
- ✅ Service Layer Pattern
- ✅ Blueprint Pattern (routes)
- ✅ Singleton Pattern (services)
- ✅ Configuration Management
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ Type hints
- ✅ Docstrings

## Future Enhancements

1. **Unit Tests**: Add comprehensive test coverage
2. **Caching**: Implement response caching to reduce API calls
3. **Rate Limiting**: Add rate limiting to protect against abuse
4. **Metrics**: Add application metrics (request count, latency, etc.)
5. **Database**: Replace InMemoryDb with persistent storage (PostgreSQL, Redis)
6. **Authentication**: Add user authentication and authorization
7. **WebSockets**: Upgrade from HTTP streaming to WebSockets
8. **Docker**: Create Docker container for easy deployment
9. **CI/CD**: Add automated testing and deployment pipeline
10. **Monitoring**: Integrate with monitoring tools (Prometheus, Grafana)
