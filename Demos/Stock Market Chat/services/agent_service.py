"""
Agent Service module for creating and managing AI agents.
Encapsulates agent configuration and creation logic.
"""

import logging
from typing import List
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.in_memory import InMemoryDb
from agno.tools.mcp import MCPTools
from config import config

logger = logging.getLogger(__name__)


class AgentService:
    """Service for creating and managing stock market analyst agents."""

    # Agent system instructions
    SYSTEM_INSTRUCTIONS = '''
        You are an expert stock market analyst with access to real-time and historical
        stock market data through Alpha Vantage. Your role is to help users understand
        stock market trends, company performance, and make informed decisions.

        AVAILABLE TOOLS:
        - TOP_GAINERS_LOSERS: Get top 20 gainers, losers, and most actively traded stocks (USE THIS for market movers!)
        - GLOBAL_QUOTE: Latest price and volume for a specific ticker
        - TIME_SERIES_DAILY: Daily historical prices for stocks
        - COMPANY_OVERVIEW: Fundamental data and company information
        - NEWS_SENTIMENT: Market news and sentiment analysis
        - Technical indicators: RSI, MACD, SMA, EMA, etc.
        - SYMBOL_SEARCH: Search for stock symbols by company name

        IMPORTANT USAGE GUIDELINES:
        1. For "top performers" or "best stocks today" questions, ALWAYS use TOP_GAINERS_LOSERS tool first
        2. Use SYMBOL_SEARCH when user mentions company names instead of symbols
        3. Get GLOBAL_QUOTE for current prices before analyzing stocks
        4. Be efficient - use one tool call when possible instead of multiple
        5. If a tool fails, try an alternative approach instead of giving up

        RESPONSE GUIDELINES:
        - Format prices with $ and percentages with %
        - Always provide data source and timestamp
        - Mention that you're not providing financial advice
        - If data is unavailable, explain why and suggest specific stocks to ask about
        - Keep responses concise but informative

        Use the Alpha Vantage tools to access stock market data and provide
        accurate, timely information to help users make informed decisions.
    '''

    def __init__(self, memory_db: InMemoryDb):
        """
        Initialize the agent service.

        Args:
            memory_db: Shared memory database for agent conversations
        """
        self.memory_db = memory_db

    def create_agent(
        self,
        session_id: str,
        mcp_tools_list: List[MCPTools]
    ) -> Agent:
        """
        Create a stock market analyst agent.

        Args:
            session_id: Unique session identifier
            mcp_tools_list: List of MCPTools instances for data access

        Returns:
            Configured Agent instance
        """
        logger.info(f"Creating agent for session {session_id}")

        agent = Agent(
            name='Stock Market Analyst',
            role='Expert financial analyst specializing in stock market data and analysis',
            instructions=self.SYSTEM_INSTRUCTIONS,
            model=OpenAIChat(
                id=config.AGENT_MODEL,
                temperature=config.AGENT_TEMPERATURE
            ),
            tools=mcp_tools_list if mcp_tools_list else [],
            session_id=session_id,
            db=self.memory_db,
            add_history_to_context=True,
            num_history_runs=config.AGENT_HISTORY_RUNS,
            markdown=True
        )

        logger.info(
            f"Agent created with {len(mcp_tools_list)} tool(s), "
            f"history: {config.AGENT_HISTORY_RUNS} runs"
        )

        return agent


# No singleton here - we create agents per request
