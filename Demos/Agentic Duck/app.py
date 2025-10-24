import uuid, json
from flask import Flask, render_template, request, Response, stream_with_context
from agno.db.in_memory import InMemoryDb
from agents import create_team

app = Flask(__name__)
_memory = InMemoryDb() # Shared memory for agents

# Home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# REST method for invoking a team of agents
@app.route('/team', methods=['GET'])
def ask_team():
    try:
        # Get the session ID or create a new one
        session_id = request.headers.get('X-Session-ID') or str(uuid.uuid4())

        # Create a team and connect it to a session
        team = create_team(session_id, _memory)

        # Get the user input and generate a response
        user_input = request.args.get('input')
        output = team.run(user_input, stream=True)

        # Inline generator for streaming output
        def generate(chunks):
            for chunk in chunks:
                if chunk.event == 'TeamRunContent':
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
