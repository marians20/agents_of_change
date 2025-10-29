# Tenacity Usage Examples

This document shows how to use the `tenacity` library for resilient retry logic in the Stock Market Chat application.

## What is Tenacity?

Tenacity is a Python library similar to Polly in .NET, providing declarative retry functionality with various strategies for handling transient failures.

## Installation

```bash
pip install tenacity
```

## Current Implementation

### MCP Connection with Tenacity

The `mcp_service.py` uses tenacity for robust connection handling:

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)

@retry(
    stop=stop_after_attempt(3),              # Stop after 3 attempts
    wait=wait_exponential(                   # Exponential backoff
        multiplier=1,
        min=1,
        max=8
    ),
    retry=retry_if_exception_type(Exception), # Retry on any exception
    before_sleep=before_sleep_log(logger, logging.WARNING),  # Log before retry
    after=after_log(logger, logging.INFO)     # Log after attempt
)
async def _attempt_connection() -> MCPTools:
    """Attempt to connect to Alpha Vantage MCP."""
    mcp_tools = MCPTools(transport='streamable-http', url=mcp_url)
    await mcp_tools.connect()
    return mcp_tools
```

## Additional Examples

### 1. Retry on Specific Exceptions Only

```python
from tenacity import retry, stop_after_attempt, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
)
async def fetch_api_data(url: str):
    """Retry only on connection or timeout errors."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### 2. Conditional Retry Based on Result

```python
from tenacity import retry, stop_after_attempt, retry_if_result

def is_rate_limited(result):
    """Check if we got a rate limit error."""
    return result.get('error') == 'rate_limit'

@retry(
    stop=stop_after_attempt(5),
    retry=retry_if_result(is_rate_limited),
    wait=wait_exponential(min=4, max=60)
)
async def call_alpha_vantage_api():
    """Retry if we get rate limited."""
    # API call logic
    pass
```

### 3. Custom Retry Condition

```python
from tenacity import retry, stop_after_attempt, retry_if_exception

def should_retry_error(exception):
    """Custom logic to determine if we should retry."""
    if isinstance(exception, ValueError):
        return False  # Don't retry ValueError
    if isinstance(exception, ConnectionError):
        return True   # Always retry connection errors
    return str(exception).startswith("Temporary")  # Retry temporary errors

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception(should_retry_error)
)
async def process_data():
    """Retry based on custom logic."""
    pass
```

### 4. Multiple Wait Strategies

```python
from tenacity import retry, stop_after_attempt, wait_fixed, wait_random, wait_combine

@retry(
    stop=stop_after_attempt(5),
    wait=wait_combine(
        wait_fixed(2),      # Fixed 2 seconds
        wait_random(0, 2)   # Plus 0-2 random seconds
    )
)
async def unreliable_operation():
    """Wait 2-4 seconds between retries."""
    pass
```

### 5. Retry with Timeout

```python
from tenacity import retry, stop_after_delay, wait_exponential

@retry(
    stop=stop_after_delay(30),  # Stop after 30 seconds total
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def time_limited_operation():
    """Stop retrying after 30 seconds regardless of attempts."""
    pass
```

### 6. Combining Multiple Stop Conditions

```python
from tenacity import retry, stop_after_attempt, stop_after_delay

@retry(
    stop=(stop_after_attempt(10) | stop_after_delay(60)),  # Stop after 10 attempts OR 60 seconds
    wait=wait_exponential(min=1, max=10)
)
async def resilient_operation():
    """Stop when either condition is met."""
    pass
```

### 7. Retry Statistics and Callbacks

```python
from tenacity import retry, stop_after_attempt, RetryCallState

def log_retry_attempt(retry_state: RetryCallState):
    """Custom callback for each retry."""
    logger.info(
        f"Attempt {retry_state.attempt_number} failed, "
        f"next sleep: {retry_state.next_action.sleep} seconds"
    )

@retry(
    stop=stop_after_attempt(3),
    before_sleep=log_retry_attempt
)
async def monitored_operation():
    """Track retry attempts with custom callback."""
    pass
```

### 8. Retry with Return Value

```python
from tenacity import retry, stop_after_attempt, RetryError

@retry(stop=stop_after_attempt(3))
async def may_fail():
    """Function that may fail."""
    # Your logic here
    pass

async def safe_caller():
    """Handle retry exhaustion gracefully."""
    try:
        result = await may_fail()
        return result
    except RetryError as e:
        logger.error(f"All retries exhausted: {e}")
        return None  # Or default value
```

### 9. Async Context Manager with Retry

```python
from tenacity import retry, stop_after_attempt
from contextlib import asynccontextmanager

@asynccontextmanager
async def retryable_connection():
    """Context manager with automatic retry."""
    @retry(stop=stop_after_attempt(3))
    async def connect():
        # Connection logic
        return connection

    conn = await connect()
    try:
        yield conn
    finally:
        await conn.close()

# Usage
async with retryable_connection() as conn:
    # Use connection
    pass
```

## Best Practices

### 1. Choose Appropriate Wait Strategy
- **Exponential backoff**: For rate-limited APIs
- **Fixed wait**: For predictable cooldown periods
- **Random jitter**: To avoid thundering herd

### 2. Set Reasonable Limits
```python
# Good: Limited attempts with max wait
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(min=1, max=30)
)

# Bad: Unlimited retries (can hang forever)
@retry(wait=wait_fixed(1))  # No stop condition!
```

### 3. Retry Specific Exceptions
```python
# Good: Only retry transient errors
@retry(
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)

# Less good: Retry all exceptions (might retry programming errors)
@retry(retry=retry_if_exception_type(Exception))
```

### 4. Log Retry Attempts
```python
# Always log retries for debugging
@retry(
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    after=after_log(logger, logging.DEBUG)
)
```

### 5. Handle Retry Exhaustion
```python
try:
    result = await retryable_function()
except RetryError:
    # Provide fallback or user-friendly error
    return default_value
```

## Tenacity vs Manual Retry Loops

### Manual Loop (Before)
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        result = await operation()
        return result
    except Exception as e:
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
        else:
            raise
```

### Tenacity (After)
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8)
)
async def operation():
    # Your code here
    pass
```

**Benefits:**
- ✅ More declarative and readable
- ✅ Consistent retry behavior across codebase
- ✅ Built-in logging and statistics
- ✅ Composable retry strategies
- ✅ Less boilerplate code

## References

- [Tenacity Documentation](https://tenacity.readthedocs.io/)
- [Tenacity GitHub](https://github.com/jd/tenacity)
- [Python retry patterns](https://www.python.org/dev/peps/pep-0343/)
