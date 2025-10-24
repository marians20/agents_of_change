# Ask LISA - Blazor Edition

A .NET Blazor Server application that provides an AI-powered Language-Integrated Stock Analyst using OpenAI/Azure OpenAI.

## Features

- 🤖 **AI Agent Team**: Team Lead orchestrating Database, Quant, and Visualization agents
- 💬 **Real-time Chat**: Streaming responses using SignalR
- 📊 **Stock Data Analysis**: Natural language queries against NASDAQ database
- 🎨 **Modern UI**: Responsive design with dark/light mode support
- 🔐 **Session Management**: Conversation history maintained per session

## Architecture

### Services

- **OpenAIService**: Handles communication with OpenAI/Azure OpenAI API
- **DatabaseService**: Converts natural language to SQL and queries SQLite database
- **AgentTeamService**: Orchestrates multiple AI agents to process user queries

### Models

- **ChatMessage**: Represents individual messages in the conversation
- **AgentConfig**: Configuration for AI services
- **StockData**: Stock market data structure

## Prerequisites

- .NET 8.0 SDK or later
- OpenAI API key or Azure OpenAI access
- NASDAQ stock database (SQLite)

## Configuration

Update `appsettings.json` or `appsettings.Development.json`:

```json
{
  "AgentConfig": {
    "ApiKey": "YOUR_OPENAI_API_KEY_HERE",
    "Endpoint": "https://YOUR_AZURE_OPENAI_ENDPOINT.openai.azure.com/",
    "Model": "gpt-4",
    "Temperature": "0.7",
    "UseAzureOpenAI": "false"
  },
  "DatabasePath": "wwwroot/nasdaq.db"
}
```

### For OpenAI:
- Set `UseAzureOpenAI` to `false`
- Provide your OpenAI `ApiKey`
- Leave `Endpoint` empty or remove it

### For Azure OpenAI:
- Set `UseAzureOpenAI` to `true`
- Provide your Azure OpenAI `Endpoint`
- Provide your Azure OpenAI `ApiKey`
- Set `Model` to your deployment name

## Database Setup

Place your `nasdaq.db` SQLite database in the `wwwroot` folder. The database should contain a `Stocks` table with the following schema:

```sql
CREATE TABLE Stocks (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Symbol TEXT NOT NULL,
    Date DATE NOT NULL,
    Open NUMERIC NOT NULL,
    Low NUMERIC NOT NULL,
    High NUMERIC NOT NULL,
    Close NUMERIC NOT NULL,
    Volume INT NOT NULL
)
```

## Running the Application

1. **Restore dependencies:**
   ```powershell
   dotnet restore
   ```

2. **Build the project:**
   ```powershell
   dotnet build
   ```

3. **Run the application:**
   ```powershell
   dotnet run
   ```

4. **Access the app:**
   Navigate to `https://localhost:5001` or the URL shown in the console

## Usage Examples

Ask LISA questions like:
- "What was Microsoft's closing price on January 15, 2024?"
- "Compare Apple and Google stock performance in 2023"
- "What was the highest trading volume for Tesla in 2024?"
- "Show me a chart of Amazon's stock price over the last year"

## Best Practices Implemented

### .NET Best Practices
- ✅ Dependency Injection for all services
- ✅ Interface-based programming (IOpenAIService, IDatabaseService, etc.)
- ✅ Async/await throughout for non-blocking operations
- ✅ IAsyncEnumerable for streaming responses
- ✅ Proper exception handling and logging
- ✅ Configuration management using IConfiguration
- ✅ Strongly-typed models

### Blazor Best Practices
- ✅ Component-based architecture
- ✅ Scoped services for user-specific data
- ✅ Session storage for state management
- ✅ Real-time updates using StateHasChanged()
- ✅ Proper disposal of resources

### Security Best Practices
- ✅ API keys stored in configuration (use Azure Key Vault in production)
- ✅ Protected browser storage for session data
- ✅ Input validation and sanitization
- ✅ HTTPS enforcement

## Project Structure

```
AskLISA.Blazor/
├── Models/
│   ├── ChatMessage.cs
│   ├── AgentConfig.cs
│   └── StockData.cs
├── Services/
│   ├── OpenAIService.cs
│   ├── DatabaseService.cs
│   └── AgentTeamService.cs
├── Pages/
│   ├── Index.razor (Main chat interface)
│   └── _Host.cshtml
├── wwwroot/
│   ├── css/
│   │   └── app.css
│   ├── js/
│   │   └── site.js
│   ├── images/
│   │   ├── user.jpg
│   │   └── chatbot.jpg
│   └── nasdaq.db
├── appsettings.json
└── Program.cs
```

## Deployment

### Azure App Service

1. Create an Azure App Service (Windows or Linux)
2. Configure Application Settings in Azure Portal:
   - Add `AgentConfig:ApiKey`
   - Add `AgentConfig:Endpoint` (if using Azure OpenAI)
   - Add other configuration values

3. Deploy using Visual Studio, VS Code, or Azure CLI:
   ```powershell
   dotnet publish -c Release
   az webapp deployment source config-zip --resource-group <group> --name <app-name> --src <zip-file>
   ```

### Docker

Create a `Dockerfile`:

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["AskLISA.Blazor.csproj", "./"]
RUN dotnet restore "AskLISA.Blazor.csproj"
COPY . .
RUN dotnet build "AskLISA.Blazor.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AskLISA.Blazor.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AskLISA.Blazor.dll"]
```

## Troubleshooting

### Common Issues

1. **No response from AI**: Check your API key and endpoint configuration
2. **Database errors**: Ensure `nasdaq.db` is in the `wwwroot` folder
3. **Streaming not working**: Verify SignalR connection in browser console
4. **Theme not applying**: Check browser console for JavaScript errors

## Future Enhancements

- [ ] Python integration for chart generation (via Python.NET)
- [ ] Support for multiple database formats
- [ ] User authentication and authorization
- [ ] Save/export conversation history
- [ ] Custom chart configurations
- [ ] Real-time stock data integration
- [ ] Multi-language support

## License

This project is based on the Ask LISA Python application and adapted to .NET Blazor.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
