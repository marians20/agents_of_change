import uuid, base64, os
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
@app.route('/streaming_chat', methods=['GET'])
def streaming_chat():
    try:
        # Get the session ID or create a new one
        session_id = request.headers.get('X-Session-ID') or str(uuid.uuid4())

        # Get the user input and the file name to use for
        # generated images, if any
        user_input = request.args.get('input')
        file_name = request.args.get('file_name')

        # Create a team, connect it to a session, and start a run
        team = create_team(session_id, _memory, file_name)
        output = team.run(user_input, stream=True)

        # Inline generator for streaming output
        def generate(chunks):
            for chunk in chunks:
                if chunk.event == 'TeamRunContent':
                    yield chunk.content

        # Stream the response
        response = Response(
            stream_with_context(generate(output)),
            mimetype='text/plain; charset=utf-8'
        )

        response.headers['X-Session-ID'] = session_id
        return response
    
    except Exception as e:
        # Stream back an error message
        output = f"I'm sorry, but something went wrong. ({str(e)})"

        response = Response(
            stream_with_context(output),
            mimetype='text/plain; charset=utf-8'
        )

        response.headers['X-Session-ID'] = session_id
        return response

# REST method for downloading generated images
@app.route('/get_image', methods=['GET'])
def get_image():
    try:
        file_name = request.args.get('file_name')
        root_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(root_dir, 'static', file_name)

        if os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()

            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            src = f'data:image/png;base64,{base64_image}'
            os.remove(image_path) # Clean up by deleting the image
            return Response(src, mimetype='text/plain; charset=utf-8')
        else:
            return '' # Image file doesn't exist
        
    except Exception as e:
        return ''