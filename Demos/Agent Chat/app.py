import uuid
from flask import Flask, render_template, request, Response, stream_with_context
from agno.models.openai import OpenAIChat
from agno.db.in_memory import InMemoryDb
from agno.agent import Agent

app = Flask(__name__)
_memory = InMemoryDb() # Shared memory for agents

# Home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
    
# REST method for chatting with an agent and generating a streaming response
@app.route('/streaming_chat', methods=['GET'])
def streaming_chat():
    try:
        # Get the session ID or create a new one
        session_id = request.headers.get('X-Session-ID') or str(uuid.uuid4())

        # Create an agent and connect it to a session
        agent = Agent(
            name='Chat Agent',
            model=OpenAIChat(id='gpt-4o-mini'),
            instructions='You are a helpful AI assistant named LISA.',
            add_history_to_context=True,
            num_history_runs=10,
            session_id=session_id,
            db=_memory,
            markdown=True
        )

        # Get the user input and generate a response
        user_input = request.args.get('input')
        output = agent.run(user_input, stream=True)

        # Inline generator for streaming output
        def generate(chunks):
            for chunk in chunks:
                if chunk.event == 'RunContent':
                    yield chunk.content

        response = Response(stream_with_context(generate(output)),
                            mimetype='text/plain; charset=utf-8')
        response.headers['X-Session-ID'] = session_id
        return response

    except Exception as e:
        output = f"I'm sorry, but something went wrong. ({str(e)})"
        response = Response(stream_with_context(output),
                            mimetype='text/plain; charset=utf-8')
        response.headers['X-Session-ID'] = session_id
        return response
