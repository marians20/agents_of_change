import os, json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from markitdown import MarkItDown
from agno.team.team import Team

MODEL='gpt-4o'

# Tool function for retrieving job candidates
def get_job_candidates():
    '''
    Retrieves job candidates and their resumes.

    Args:
        None

    Returns:
        str: JSON string containing a list of job candidates and their resumes.
    '''
    
    candidates = []
    directory = 'candidates'
    print('\x1b[32mRetrieving resumes\x1b[0m')
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        try:
            # Convert the document to markdown. Assumes the file name
            # is the candidate's name.
            md = MarkItDown(enable_plugins=False)
            result = md.convert(file_path)
            candidates.append({ 'Name': filename, 'Resume': result.text_content })

        except Exception as e:
            print(f'Unable to convert {file_path}: {e}')
    
    return json.dumps(candidates)

# Tool function for retrieving job descriptions
def get_job_descriptions():
    '''
    Retrieves job descriptions describing jobs needing to be filled.

    Args:
        None

    Returns:
        str: JSON string containing a list of companies and job openings at those companies.
    '''

    jobs = []
    directory = 'jobs'
    print('\x1b[32mRetrieving job listings\x1b[0m')
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        try:
            # Convert the document to markdown. Assumes the file name
            # is the company name.
            md = MarkItDown(enable_plugins=False)
            result = md.convert(file_path)
            jobs.append({ 'Company': filename, 'Job Description': result.text_content })

        except Exception as e:
            print(f'Unable to convert {file_path}: {e}')
   
    return json.dumps(jobs)

def create_team(session_id, memory):
    candidate_retrieval_agent = Agent(
        name='Candidate Retrieval Agent',
        role='Retrieves the resumes of all candidates currently looking for a job.',
        model=OpenAIChat(id=MODEL),
        tools=[get_job_candidates],
        markdown=True
    )

    job_retrieval_agent = Agent(
        name='Job Description Retrieval Agent',
        role='Retrieves descriptions of all job openings that are currently on file.',
        model=OpenAIChat(id=MODEL),
        tools=[get_job_descriptions],
        markdown=True
    )

    evaluation_agent = Agent(
        name='Evaluation Agent',
        role="Evaluates a candidate's fitness for a job.",
        model=OpenAIChat(id=MODEL),
        instructions='''
            Evaluate a candidate's fitness for a job by generating a numeric
            score from 0.0 to 10.0, where a higher score reflects higher fitness
            for the job. Be critical; make it difficult to earn a high score.
            Always include scores to help explain your reasoning.
            ''',
        markdown=True
    )

    team = Team(
        name='Team Lead',
        members=[candidate_retrieval_agent, job_retrieval_agent, evaluation_agent],
        instructions='''
            Your name is LISA, and you lead a team of hiring experts. Use the
            Candidate Retrieval Agent to retrieve resumes and answer questions
            about candidates. Use the Job Description Retrieval Agent to retrieve
            job openings and answer questions about them.
            
            To evaluate a candidate's fitness for a job, consult the Candidate
            Retrieval Agent for information about the candidate and the Job
            Description Retrieval Agent for information about the job opening.
            Then pass both to the Evaluation Agent. Include scores to support
            your reasoning.
            
            Only evaluate candidates for whom resumes are available from the
            Candidate Retrieval Agent. Only evaluate candidates for jobs that
            are currently available from the Job Description Retrieval Agent.
            Do not assume that the conversation history includes information
            about all current job candidates and all current job openings.
            Always consult the other agents for the latest resumes and job
            descriptions.

            If asked to evaluate several candidates for one job, include a table
            in the response with columns for the candidate name, the score (0.0 to
            10.0), and a brief explanation of the score. Use the table to show each
            candidate's fit for the job. Also provide a textual summary explaining
            why the highest-scoring candidate is the best for for the job.
            
            If asked to evaluate a single candidate for several jobs, include a table
            in the response containing columns for the company name, the score (0.0 to
            10.0), and a brief explanation of the score. Use the table to show each
            job's fit for the candidate. Also provide a textual summary explaining
            why the highest-scoring job is the best fit for the candidate.

            Make your output succint. Conversational responses are preferred to
            ones containing bulleted and numbered lists. Use numbered lists ONLY
            if necessary.
            ''',
        model=OpenAIChat(id=MODEL),
        add_history_to_context=True,
        num_history_runs=10,
        share_member_interactions=True,
        session_id=session_id,
        db=memory,
        markdown=True
    )

    return team
