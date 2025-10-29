# Alpha Vantage API Rate Limits & Usage

## Official Rate Limits

### Free Tier
- **25 API requests per day**
- No per-minute or per-hour limits
- **No official usage API** to check current consumption

### Premium Tiers

Alpha Vantage offers several premium tiers with higher limits:

| Plan | Requests/Minute | Requests/Day | Price |
|------|----------------|--------------|-------|
| **Free** | N/A | **25** | $0 |
| **Basic** | 75 | 9,000 | ~$50/month |
| **Plus** | 150 | 18,000 | ~$100/month |
| **Premium** | 600 | 72,000 | ~$250/month |
| **Enterprise** | 1200+ | Custom | Contact Sales |

🔗 Check current pricing: https://www.alphavantage.co/premium/

## How to Monitor Your Usage

Since Alpha Vantage doesn't provide an API to check your current usage, you need to track it yourself.

### Method 1: Use the Built-in Usage Tracker

The application now includes `api_usage_tracker.py` that automatically tracks your daily API usage.

```python
from utils.api_usage_tracker import api_usage_tracker

# Record an API call
api_usage_tracker.record_api_call("GLOBAL_QUOTE")

# Check if you can make another request
if api_usage_tracker.can_make_request():
    # Make API call
    pass
else:
    # Show error message
    print("Daily API limit reached!")

# Get usage summary
print(api_usage_tracker.get_usage_summary())
```

**Output Example:**
```
📊 Alpha Vantage API Usage Summary
═══════════════════════════════════
Date: 2025-10-29
Used: 18/25 requests (72.0%)
Remaining: 7 requests

Endpoint Breakdown:
  • GLOBAL_QUOTE: 12 calls
  • TOP_GAINERS_LOSERS: 4 calls
  • NEWS_SENTIMENT: 2 calls

First call: 2025-10-29T08:30:15
Last call:  2025-10-29T14:25:43
```

### Method 2: Check Application Logs

The app logs every MCP tool call. Check your console or log files:

```
2025-10-29 02:24:13 - httpx - INFO - HTTP Request: POST https://mcp.alphavantage.co/mcp?apikey=***
```

Each `POST https://mcp.alphavantage.co/mcp` request counts as 1 API call.

### Method 3: Monitor Error Messages

When you hit the limit, Alpha Vantage returns an error message:

```json
{
    "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 25 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency."
}
```

## Common API Endpoints Used

The MCP server uses these endpoints (each counts as 1 request):

| Tool | Endpoint | Typical Usage |
|------|----------|---------------|
| TOP_GAINERS_LOSERS | `TOP_GAINERS_LOSERS` | Market overview queries |
| GLOBAL_QUOTE | `GLOBAL_QUOTE` | Single stock price |
| TIME_SERIES_DAILY | `TIME_SERIES_DAILY` | Historical prices |
| COMPANY_OVERVIEW | `OVERVIEW` | Company fundamentals |
| NEWS_SENTIMENT | `NEWS_SENTIMENT` | News & sentiment |
| SYMBOL_SEARCH | `SYMBOL_SEARCH` | Symbol lookup |
| Technical Indicators | `RSI`, `MACD`, `SMA`, etc. | Chart analysis |

## Tips to Stay Within Limits

### 1. Cache Responses
```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def cached_stock_price(symbol: str, timestamp: int):
    # timestamp changes every 5 minutes
    # so cache lasts 5 minutes
    return api_usage_tracker.get_stock_price(symbol)

# Use it
five_min_bucket = int(time.time() // 300)
price = cached_stock_price("MSFT", five_min_bucket)
```

### 2. Batch Queries
Instead of:
```
User: "What's the price of MSFT?"  → 1 API call
User: "What about AAPL?"           → 1 API call
User: "And GOOGL?"                 → 1 API call
Total: 3 API calls
```

Ask:
```
User: "What are the prices of MSFT, AAPL, and GOOGL?"
Agent: Uses TOP_GAINERS_LOSERS to get all in one call
Total: 1 API call
```

### 3. Use Specific Queries
The agent instructions already optimize this:
```python
# GOOD - Uses TOP_GAINERS_LOSERS (1 call, gets 60 stocks)
"What are the top performers today?"

# LESS EFFICIENT - Multiple GLOBAL_QUOTE calls
"What's the price of MSFT, AAPL, GOOGL, AMZN, TSLA?"  # 5 calls
```

### 4. Clear Conversation History
Each conversation turn may trigger multiple API calls. Clear history:
- Click "Clear History" button in the UI
- Or refresh the page

### 5. Upgrade to Premium
If you need more than 25 requests/day:
- Visit https://www.alphavantage.co/premium/
- Plans start at ~$50/month for 9,000 requests/day

## Monitoring in Production

### Add to Your App

Integrate the tracker into `services/mcp_service.py`:

```python
from utils.api_usage_tracker import api_usage_tracker

async def _connect_alpha_vantage(self) -> Optional[MCPTools]:
    # Before connecting, check if we have quota
    if not api_usage_tracker.can_make_request():
        logger.error("Daily API limit reached!")
        return None

    # ... existing connection code ...

    # After successful connection, record usage
    api_usage_tracker.record_api_call("connection")

    return mcp_tools
```

### Create a Usage Endpoint

Add to `routes/chat_routes.py`:

```python
@chat_bp.route('/api_usage', methods=['GET'])
async def get_api_usage():
    """Get current API usage statistics."""
    from utils.api_usage_tracker import api_usage_tracker
    usage = api_usage_tracker.get_today_usage()
    return jsonify(usage)
```

Then display in your UI:
```javascript
fetch('/api_usage')
    .then(r => r.json())
    .then(data => {
        console.log(`Used ${data.count}/${data.limit} requests today`);
        if (data.remaining < 5) {
            alert(`Only ${data.remaining} API requests remaining today!`);
        }
    });
```

## Troubleshooting

### "Thank you for using Alpha Vantage..." Error

**Cause:** Hit the 25 requests/day limit

**Solutions:**
1. Wait until midnight UTC (limit resets daily)
2. Upgrade to premium tier
3. Use cached data for development
4. Get a second API key (but check ToS first)

### Can't See Current Usage

**Cause:** Alpha Vantage doesn't provide a usage API

**Solutions:**
1. Use the built-in `api_usage_tracker.py`
2. Monitor application logs
3. Count requests manually
4. Check for error messages

### Inconsistent Rate Limiting

**Cause:** API may have additional undocumented limits

**Observation:** Some users report occasional throttling before 25 requests

**Solution:**
- Always implement retry logic (we use tenacity)
- Add delays between requests (500ms recommended)
- Cache responses aggressively

## API Key Management

### Multiple Keys for Development

You can use different keys for dev/prod:

**.env.development**
```bash
ALPHA_VANTAGE_API_KEY=dev_key_here
```

**.env.production**
```bash
ALPHA_VANTAGE_API_KEY=prod_key_here
```

**Load based on environment:**
```python
from dotenv import load_dotenv
import os

env = os.getenv('ENVIRONMENT', 'development')
load_dotenv(f'.env.{env}')
```

### Rotate Keys

If you suspect your key is compromised or hitting limits:
1. Get a new key: https://www.alphavantage.co/support/#api-key
2. Update `.env` file
3. Restart the application

## References

- Official Documentation: https://www.alphavantage.co/documentation/
- Premium Plans: https://www.alphavantage.co/premium/
- Support: https://www.alphavantage.co/support/
- Terms of Service: https://www.alphavantage.co/terms_of_service/
- MCP Server: https://mcp.alphavantage.co/

## Quick Summary

✅ **Free Tier**: 25 requests/day
✅ **Premium**: Starting at 75 requests/min
✅ **No official usage API**
✅ **Use built-in tracker**: `api_usage_tracker.py`
✅ **Monitor logs**: Count `POST mcp.alphavantage.co` requests
✅ **Optimize queries**: Use TOP_GAINERS_LOSERS for batches
✅ **Cache responses**: Reduce redundant calls
✅ **Upgrade when needed**: Premium plans available
