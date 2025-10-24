# Migration Guide: Python Flask to .NET Blazor

## Architecture Comparison

### Python (Flask) Version
- **Framework**: Flask (Python web framework)
- **Frontend**: Vanilla JavaScript with server-side rendering
- **AI Library**: Agno 2.0.7
- **Database**: SQLite with sqlite3
- **Deployment**: Python WSGI server

### .NET Blazor Version
- **Framework**: ASP.NET Core Blazor Server
- **Frontend**: Blazor components with C# code-behind
- **AI Library**: Azure.AI.OpenAI / OpenAI SDK
- **Database**: SQLite with Microsoft.Data.Sqlite
- **Deployment**: Kestrel / IIS / Azure App Service

## Key Differences

### 1. Communication Pattern

**Python/Flask:**
- REST endpoints (`/streaming_chat`, `/get_image`)
- Server-Sent Events for streaming
- Session ID passed via headers

**Blazor:**
- SignalR for real-time bi-directional communication
- Built-in streaming support via IAsyncEnumerable
- Session storage using ProtectedSessionStorage

### 2. Agent Implementation

**Python (Agno):**
```python
database_agent = Agent(
    name='Database Agent',
    role='Retrieves data from the NASDAQ database.',
    tools=[query_database],
    model=OpenAIChat(id=MODEL)
)
```

**C# (Custom Services):**
```csharp
public class DatabaseService : IDatabaseService
{
    private readonly IOpenAIService _openAIService;

    public async Task<string> QueryDatabaseAsync(string query)
    {
        var sql = await ConvertTextToSqlAsync(query);
        return await ExecuteQueryAsync(sql);
    }
}
```

### 3. Dependency Injection

**Python:**
- Manual service instantiation
- Global memory object
- Function-based architecture

**C#:**
- Built-in DI container
- Service lifetimes (Singleton, Scoped, Transient)
- Interface-based design

### 4. Configuration

**Python:**
```python
MODEL='gpt-4.1'
TOOL_PATH = Path(tempfile.gettempdir())
```

**C#:**
```csharp
// appsettings.json
{
  "AgentConfig": {
    "Model": "gpt-4",
    "Temperature": "0.7"
  }
}
```

### 5. Streaming Responses

**Python:**
```python
def generate(chunks):
    for chunk in chunks:
        if chunk.event == 'TeamRunContent':
            yield chunk.content

return Response(stream_with_context(generate(output)))
```

**C#:**
```csharp
public async IAsyncEnumerable<string> ProcessQueryAsync(...)
{
    await foreach (var chunk in _openAIService.GetStreamingCompletionAsync(...))
    {
        yield return chunk;
    }
}
```

## Feature Parity

| Feature | Python Version | Blazor Version | Status |
|---------|----------------|----------------|--------|
| Chat Interface | ✅ | ✅ | Complete |
| Streaming Responses | ✅ | ✅ | Complete |
| Database Queries | ✅ | ✅ | Complete |
| Session Management | ✅ | ✅ | Complete |
| Dark/Light Mode | ✅ | ✅ | Complete |
| Agent Team | ✅ | ⚠️ | Simplified |
| Chart Generation | ✅ | ❌ | Not Implemented* |
| Python Tools | ✅ | ❌ | Not Applicable |

*Chart generation in Blazor would require additional libraries (e.g., ScottPlot, Python.NET, or JavaScript charting libraries)

## Migration Benefits

### Advantages of Blazor Version

1. **Type Safety**: C# provides compile-time type checking
2. **Performance**: .NET runtime is generally faster than Python
3. **Scalability**: Better support for horizontal scaling
4. **Tooling**: Excellent IDE support (Visual Studio, Rider)
5. **Enterprise Integration**: Easier to integrate with Azure services
6. **Security**: Built-in features like CSRF protection, authentication

### Trade-offs

1. **Agent Flexibility**: Agno provides more sophisticated multi-agent orchestration
2. **Python Ecosystem**: Python has richer data science libraries
3. **Development Speed**: Python might be faster for prototyping
4. **Code Generation**: Python tools for chart/code generation are more mature

## Implementation Notes

### Simplified Agent Architecture

The Blazor version uses a simplified agent architecture compared to Python's Agno framework:

- **Team Lead**: Implemented as orchestration logic in `AgentTeamService`
- **Database Agent**: Implemented as `DatabaseService`
- **Quant Agent**: Logic can be added to `AgentTeamService` for calculations
- **Visualization Agent**: Would require additional implementation with charting libraries

### Chart Generation Options

To add chart generation similar to the Python version, consider:

1. **ScottPlot**: .NET native charting library
2. **Python.NET**: Call Python matplotlib from C#
3. **JavaScript Libraries**: Chart.js, D3.js, Plotly.js
4. **Azure AI Vision**: Use Azure services for chart generation

### Database Migration

No changes needed - both versions use the same SQLite database structure.

## Code Examples

### Converting Flask Routes to Blazor Components

**Before (Python):**
```python
@app.route('/streaming_chat', methods=['GET'])
def streaming_chat():
    user_input = request.args.get('input')
    team = create_team(session_id, _memory, file_name)
    output = team.run(user_input, stream=True)
    return Response(stream_with_context(generate(output)))
```

**After (C#):**
```csharp
private async Task SendMessage()
{
    await foreach (var chunk in AgentTeamService.ProcessQueryAsync(...))
    {
        assistantMessage.Content += chunk;
        StateHasChanged();
    }
}
```

### Configuration Migration

**Before (Python):**
```python
# Hardcoded in code
MODEL='gpt-4.1'
connection = sqlite3.connect('static/nasdaq.db')
```

**After (C#):**
```json
{
  "AgentConfig": {
    "Model": "gpt-4"
  },
  "DatabasePath": "wwwroot/nasdaq.db"
}
```

## Deployment Comparison

### Python Deployment
```bash
pip install -r requirements.txt
flask run
# Or with gunicorn:
gunicorn -w 4 app:app
```

### Blazor Deployment
```powershell
dotnet publish -c Release
dotnet AskLISA.Blazor.dll
# Or deploy to Azure:
az webapp up --name ask-lisa-blazor --runtime "DOTNETCORE:8.0"
```

## Performance Considerations

1. **Startup Time**: Blazor Server has faster startup than Flask
2. **Memory Usage**: .NET generally more efficient than Python
3. **Concurrent Users**: Blazor Server handles concurrency better
4. **Streaming**: Both handle streaming well, Blazor uses SignalR websockets

## Recommended Next Steps

1. **Add Chart Generation**: Implement using ScottPlot or JavaScript libraries
2. **Enhanced Agent Logic**: Implement full multi-agent orchestration
3. **Authentication**: Add user authentication and authorization
4. **Caching**: Implement response caching for common queries
5. **Monitoring**: Add Application Insights or similar monitoring
6. **CI/CD**: Set up automated deployment pipelines

## Conclusion

The Blazor version provides a production-ready foundation with better type safety, performance, and enterprise integration capabilities. While it simplifies some agent orchestration aspects, it offers a solid platform for building scalable, maintainable applications with Azure services integration.
