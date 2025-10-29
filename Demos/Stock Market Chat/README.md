# Stock Market Chat

AI-powered stock market analysis chatbot using OpenAI and Alpha Vantage MCP server for real-time market data.

## Features

- **Real-time Stock Data**: Access current and historical stock prices via Alpha Vantage API
- **Technical Analysis**: Query technical indicators like SMA, EMA, RSI, MACD
- **Company Information**: Get company overviews, earnings, and fundamental data
- **Market Intelligence**: Ask natural language questions about stocks, trends, and market conditions
- **MCP Integration**: Uses Model Context Protocol for structured data access

## Prerequisites

- Python 3.10 or higher
- Alpha Vantage API key (free tier available)
- OpenAI API key

## Setup

### 1. Clone and Navigate

```bash
cd "Stock Market Chat"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

1. Copy `.env.template` to `.env`:
   ```bash
   Copy-Item .env.template .env
   ```

2. Edit `.env` and add your API keys:
   ```
   ALPHA_VANTAGE_API_KEY=your_actual_key_here
   OPENAI_API_KEY=your_actual_key_here
   ```

#### Getting API Keys

- **Alpha Vantage**: Free at https://www.alphavantage.co/support/#api-key
  - Free tier: 25 requests/day, 5 requests/minute
  - No credit card required

- **OpenAI**: https://platform.openai.com/api-keys
  - Requires payment method
  - Uses gpt-4o-mini model (cost-effective)

### 5. Run the Application

```bash
python app.py
```

The application will start on http://localhost:5000

## Usage Examples

Try asking:

- "What's the current price of AAPL?"
- "Show me the 50-day moving average for TSLA"
- "Get company information for Microsoft"
- "What are the top gainers today?"
- "Compare the performance of GOOGL and MSFT over the last year"
- "What's the RSI for NVDA?"

## Available Tools (via MCP)

The agent has access to these Alpha Vantage functions:

- **TIME_SERIES_DAILY**: Daily stock prices
- **TIME_SERIES_INTRADAY**: Intraday prices (1min, 5min, 15min, 30min, 60min)
- **GLOBAL_QUOTE**: Real-time quote data
- **SYMBOL_SEARCH**: Search for stock symbols
- **COMPANY_OVERVIEW**: Fundamental data and company info
- **Technical Indicators**: SMA, EMA, RSI, MACD, BBANDS, and more
- **CURRENCY_EXCHANGE_RATE**: Forex rates
- **CRYPTO**: Cryptocurrency data

## Architecture

- **Backend**: Quart (async Flask) for WebSocket support
- **AI Framework**: Agno for agent orchestration
- **MCP Server**: Alpha Vantage MCP for structured API access
- **Frontend**: HTML/CSS/JavaScript with real-time streaming

## Rate Limits

Free Alpha Vantage tier limits:
- 25 API calls per day
- 5 API calls per minute

Consider upgrading to Premium if you need higher limits.

## Troubleshooting

### "API key not found" error
- Ensure `.env` file exists and contains valid keys
- Check that python-dotenv is installed

### "Rate limit exceeded"
- Free tier is limited to 5 calls/minute, 25/day
- Wait a few minutes and try again
- Consider Alpha Vantage Premium for higher limits

### Connection errors
- Verify internet connection
- Check API keys are valid
- Ensure MCP server is accessible

## Development

The application uses:
- `app.py`: Main Quart application with MCP connection handling
- `agents.py`: Stock analyst agent configuration with system prompts
- `templates/index.html`: Chat interface
- `static/`: CSS, JavaScript, and images

## License

MIT License - See LICENSE file for details
