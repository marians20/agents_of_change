# Built and tested against Agno 2.0.7 and OpenAI 1.109.1. If something
# doesn't work, try installing these versions.

import tempfile
import json, sqlite3, re
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.python import PythonTools
from agno.models.message import Message
from agno.team.team import Team
from pathlib import Path

MODEL='gpt-4.1'
TOOL_PATH = Path(tempfile.gettempdir()) # For .py files created by the Python tool

# Tool function for querying the database
def query_database(text):
    '''
    Queries the NASDAQ database.

    Args:
        text (str): Natural-language query describing the data to be retrieved.

    Returns:
        str: JSON string containing query results.
    '''

    sql = text2sql(text)
    print(f'\x1b[32m{sql}\x1b[0m')
    connection = sqlite3.connect('static/nasdaq.db')
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    return json.dumps(rows)

# Helper function to convert natural-language queries into SQL queries
def text2sql(text):
    prompt = f'''
        Generate a well-formed SQLite query from the prompt below. Return
        the SQL only. Do not use markdown formatting, and do not use SELECT *.

        PROMPT: {text}
	
        The database targeted by the query contains the following table:

        CREATE TABLE Stocks (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Symbol TEXT NOT NULL,   -- Stock symbol (for example, "MSFT")
            Date DATE NOT NULL,     -- Date
            Open NUMERIC NOT NULL,  -- Opening price of the stock on that date
            Low NUMERIC NOT NULL,   -- Lowest price of the stock on that date
            High NUMERIC NOT NULL,  -- Highest price of the stock on that date
            Close NUMERIC NOT NULL, -- Closing price of the stock on that date
            Volume INT NOT NULL     -- Number of shares traded on that date
        )
        '''

    model=OpenAIChat(id=MODEL, temperature=0.2)
    messages = [Message(role='user', content=prompt)]
    response = model.response(messages)
    pattern = r'^```[\w]*\n|\n```$'
    content = re.sub(pattern, '', response.content, flags=re.MULTILINE)
    return content

# Function to hook into function calls and show member delegations
def delegation_hook(function_name, function_call, arguments):
    if function_name == 'delegate_task_to_member':
        member_id = arguments.get('member_id')
        print(f'\x1b[33mDelegating to {member_id}\x1b[0m')

    return function_call(**arguments)

# Function to create a team of agents
def create_team(session_id, memory, file_name):
    database_agent = Agent(
        name='Database Agent',
        role='Retrieves data from the NASDAQ database.',
        instructions='''
            Use the query_database tool to retrieve data from NASDAQ
            database. The database contains historical stock prices for
            selected NASDAQ stocks from 2020 through 2024.
            
            Return ALL of the data produced by a database query, not just a
            representative sample. This data may be required by other agents.
            ''',
        model=OpenAIChat(id=MODEL, temperature=0.2),
        tools=[query_database],
        markdown=True
    )

    quant_agent = Agent(
        name='Quant Agent',
        role='Performs quantitative analyses using code.',
        instructions='''
            Use the Python tool to generate and execute code needed to
            perform calculations.
            ''',
        model=OpenAIChat(id=MODEL, temperature=0.2),
        tools=[PythonTools(
            base_dir=TOOL_PATH, # Keep .py files out of the working directory
            exclude_tools=['pip_install_package', 'uv_pip_install_package']
        )],
        markdown=True
    )

    visualization_agent = Agent(
        name='Visualization Agent',
        role='Generates images containing charts and graphs.',
        instructions=f'''
            Use the Python tool to generate an image containing a
            professional-looking chart or graph. Minimum image width is
            960px. Use a black background with light text and graphics
            unless directed to do otherwise. For example, set axes.facecolor
            and figure.facecolor to black. Use 3-letter abbreviations such
            as Jan, Feb, and Mar to represent months. Use plt.savefig() to
            save the plot as a PNG at "static/{file_name}".

            Do not generate code that could be harmful to the computer
            it's running on, and do not call plt.show(). Include a call
            to plt.close() at the end and a call to matplotlib.use('Agg')
            at the beginning. Also include code to suppress any warnings.
            If necessary, write code to perform any calculations required
            for a visualization.
            
            Do NOT plot a subset of the data or ask the user to upload a
            dataset. Just chart the data provided to you, no questions asked.
            ''',
        model=OpenAIChat(id=MODEL, temperature=0.2),
        tools=[PythonTools(
            base_dir=TOOL_PATH, # Keep .py files out of the working directory
            exclude_tools=['pip_install_package', 'uv_pip_install_package']
        )],
        markdown=True
    )

    team = Team(
        name='Team Lead',
        members=[database_agent, quant_agent, visualization_agent],
        tool_hooks=[delegation_hook],
        instructions='''
            You are an analyst named LISA who leads a team of stock experts.
            When asked about stock prices, use daily closing prices unless
            directed to do otherwise. Assume that monetary amounts are in
            dollars. Round such amounts to the nearest dollar in your output,
            and use commas as separators for amounts greater than $999.

            Use the database agent if you need data from the NASDAQ database.
            The database contains daily OHLC prices and trading volumes for
            selected NASDAQ stocks from 2020 through 2024. Feel free to use
            SQL functioons such as MIN, MAX, and AVG to perform simple
            calculations and avoid having to call the quant agent.

            Use the quant agent to perform calculations that do NOT produce a
            chart or graph. Calculations that produce a chart or graph can be
            performed by the visualization agent. If necessary, use the database
            agent to obtain data for the quant agent to analyze.

            When asked to produce a chart, graph, or other visualization, use
            the visualization agent. Instruct it to plot all of the data provided
            to it. If necessary, use the database agent to obtain data for the
            visualization agent to chart.

            IMPORTANT: Do NOT include a link to any image that was generated
            in your output or offer to let the user download an image. Images
            are shown to the user automatically.            
            ''',
        model=OpenAIChat(id=MODEL),
        share_member_interactions=True,
        add_history_to_context=True,
        num_history_runs=12,
        session_id=session_id,
        db=memory,
        markdown=True
    )

    return team
