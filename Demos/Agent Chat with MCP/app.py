# To run this app, use the command "quert run" or "quart app --reload"
# Since this is Quart, we no longer need stream_with_context

from quart import Quart, render_template, request, Response
from agno.db.in_memory import InMemoryDb
from agno.tools.mcp import MCPTools
from agents import create_agent
import uuid

app = Quart(__name__)
_memory = InMemoryDb() # Shared memory for agents
_mcp_tools = None # MCPTool instance

# Home page
@app.route('/', methods=['GET'])
async def index():
    return await render_template('index.html')
    
# REST method for chatting with an agent and generating a streaming response
@app.route('/streaming_chat', methods=['GET'])
async def streaming_chat():
    try:
        # Get the session ID or create a new one
        session_id = request.headers.get('X-Session-ID') or str(uuid.uuid4())

        # Create an agent and connect it to a session and GitHub's MCP server
        agent = create_agent(session_id, _memory, _mcp_tools)

        # Get the user input and generate a response
        user_input = request.args.get('input')
        output = agent.arun(user_input, stream=True)

        async def generate():
            async for chunk in output:
                if chunk.event == 'RunContent':
                    yield chunk.content

        response = Response(generate(), mimetype='text/plain; charset=utf-8')
        response.headers['X-Session-ID'] = session_id
        return response

    except Exception as e:
        output = f"I'm sorry, but something went wrong. ({str(e)})"
        response = Response(output, mimetype='text/plain; charset=utf-8')
        response.headers['X-Session-ID'] = session_id
        return response

# Startup function to open an MCP connection
@app.before_serving
async def startup():
    global _mcp_tools
    _mcp_tools = await open_mcp_connection()

# Shutdown function to close an MCP connection
@app.after_serving
async def shutdown():
    if _mcp_tools:
        await close_mcp_connection()
    
# Helper function to initialize an MCP connection
async def open_mcp_connection():
    _mcp_tools = MCPTools(transport='streamable-http', url='https://docs.agno.com/mcp')
    await _mcp_tools.connect()
    return _mcp_tools

# Helper function to close an MCP connection
async def close_mcp_connection():
    await _mcp_tools.close()
    