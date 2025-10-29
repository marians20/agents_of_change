# Adding Additional MCP Servers

The Stock Market Chat application now supports multiple MCP (Model Context Protocol) servers. This allows you to integrate various data sources to provide richer financial information.

## Current MCP Servers

1. **Alpha Vantage MCP** - Primary stock market data
   - URL: `https://mcp.alphavantage.co/mcp`
   - Provides: Stock quotes, historical data, technical indicators, fundamentals, news

## How to Add More MCP Servers

### Step 1: Find Available MCP Servers

Search for financial data MCP servers:
- Check the [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- Look for finance-specific MCPs
- Community-built MCP servers

### Step 2: Add Connection Code

Edit `app.py` in the `open_mcp_connections()` function:

```python
async def open_mcp_connections():
    mcp_list = []

    # 1. Alpha Vantage (existing)
    alpha_vantage_tools = await connect_alpha_vantage()
    if alpha_vantage_tools:
        mcp_list.append(alpha_vantage_tools)

    # 2. Add your new MCP here
    try:
        # Example: Yahoo Finance MCP (hypothetical)
        yahoo_url = 'https://mcp.yahoofinance.com/mcp'
        yahoo_tools = MCPTools(
            transport='streamable-http',
            url=yahoo_url
        )
        await yahoo_tools.connect()
        mcp_list.append(yahoo_tools)
        logger.info("✓ Yahoo Finance MCP connected")
    except Exception as e:
        logger.warning(f"Could not connect to Yahoo Finance MCP: {str(e)}")

    return mcp_list
```

### Step 3: Add API Keys to .env

If the new MCP requires authentication:

```bash
# .env file
ALPHA_VANTAGE_API_KEY=your_key_here
YAHOO_FINANCE_API_KEY=your_yahoo_key_here
```

### Step 4: Update Agent Instructions

Edit `agents.py` to inform the agent about new tools:

```python
instructions='''
    ...existing instructions...

    AVAILABLE DATA SOURCES:
    - Alpha Vantage: US stocks, forex, crypto, technical indicators
    - Yahoo Finance: International stocks, ETFs, mutual funds

    ...rest of instructions...
'''
```

## Potential MCP Servers to Add

### 1. **Finnhub MCP** (if available)
- Real-time stock data
- Company news and sentiment
- Economic calendar
- URL: Check https://finnhub.io/ for MCP support

### 2. **Polygon.io MCP** (if available)
- Stock market data
- Options data
- Forex and crypto
- URL: Check https://polygon.io/ for MCP support

### 3. **IEX Cloud MCP** (if available)
- Stock quotes and fundamentals
- Historical data
- Market movers
- URL: Check https://iexcloud.io/ for MCP support

### 4. **Economic Data MCP**
- FRED (Federal Reserve Economic Data)
- World Bank data
- IMF statistics

### 5. **News Sentiment MCP**
- Financial news aggregators
- Social media sentiment
- Earnings call transcripts

## Benefits of Multiple MCPs

1. **Redundancy**: If one API is down or rate-limited, use another
2. **Data Diversity**: Different sources provide different perspectives
3. **Feature Expansion**: Access specialized data (options, forex, crypto)
4. **Cost Optimization**: Mix free and paid tiers strategically

## Example: Adding a Fallback Strategy

```python
# In agents.py instructions
'''
DATA RETRIEVAL STRATEGY:
1. Try Alpha Vantage first for US stocks
2. If rate-limited, try Yahoo Finance
3. For international stocks, prefer Yahoo Finance
4. For crypto, try both sources and compare
'''
```

## Testing New MCPs

After adding a new MCP:

1. Restart the application
2. Check logs for connection status
3. Ask the agent to use tools from the new MCP
4. Verify data quality and response times

## Troubleshooting

**MCP won't connect:**
- Check API key is correct
- Verify MCP server URL
- Check internet connection
- Review server-specific documentation

**Rate limits:**
- Implement request caching
- Spread requests across multiple MCPs
- Upgrade to paid tiers if needed

**Token limits:**
- Each MCP adds ~5-15K tokens for tool definitions
- Limit to 3-5 MCPs maximum to avoid context overflow
- Choose MCPs with complementary, not overlapping, features

## Community MCP Servers

Check these resources for community-built MCPs:
- https://github.com/modelcontextprotocol/servers
- https://mcphub.io/ (if available)
- Financial data provider documentation

## Contributing

If you create a useful financial MCP integration, consider:
- Documenting the setup process
- Sharing API key requirements
- Noting rate limits and costs
- Creating example queries
