# Quick Start Guide - Ask LISA Blazor

## Step 1: Prerequisites Check

Ensure you have the following installed:
- .NET 8.0 SDK or later
- An OpenAI API key OR Azure OpenAI access
- The NASDAQ database file from the original Ask LISA demo

## Step 2: Copy Database File

Copy the database from the original demo:

```powershell
Copy-Item "d:\work\poc\Agents of Change\Demos\Ask LISA\static\nasdaq.db" "d:\work\poc\Agents of Change\Demos\AskLISA.Blazor\wwwroot\nasdaq.db"
```

## Step 3: Configure API Keys

Update `appsettings.Development.json` with your API credentials:

### For OpenAI:
```json
{
  "AgentConfig": {
    "ApiKey": "sk-your-actual-openai-api-key-here",
    "Model": "gpt-4",
    "Temperature": "0.7",
    "UseAzureOpenAI": "false"
  }
}
```

### For Azure OpenAI:
```json
{
  "AgentConfig": {
    "ApiKey": "your-azure-openai-key-here",
    "Endpoint": "https://your-resource.openai.azure.com/",
    "Model": "gpt-4",
    "Temperature": "0.7",
    "UseAzureOpenAI": "true"
  }
}
```

## Step 4: Build and Run

```powershell
cd "d:\work\poc\Agents of Change\Demos\AskLISA.Blazor"
dotnet build
dotnet run
```

## Step 5: Access the Application

Open your browser and navigate to:
- HTTPS: `https://localhost:5001`
- HTTP: `http://localhost:5000`

## Sample Questions to Try

Once the app is running, try these questions:

1. "What was Microsoft's closing price on January 15, 2024?"
2. "Compare Apple and Microsoft stock prices in Q1 2024"
3. "What was the highest trading volume for TSLA in 2023?"
4. "Show me the average closing price for GOOGL in 2024"

## Troubleshooting

### Database Not Found
If you see errors about the database file:
- Verify `nasdaq.db` is in the `wwwroot` folder
- Check the `DatabasePath` setting in `appsettings.json`

### API Key Errors
If you see authentication errors:
- Verify your API key is correct in `appsettings.Development.json`
- For Azure OpenAI, ensure the endpoint URL is correct
- Check that `UseAzureOpenAI` is set correctly

### Build Errors
If the build fails:
```powershell
dotnet restore
dotnet clean
dotnet build
```

### Port Already in Use
If the default ports are in use, edit `Properties/launchSettings.json` to change ports.

## Next Steps

- Customize the UI by editing `wwwroot/css/app.css`
- Modify agent instructions in `Services/AgentTeamService.cs`
- Add new features or integrate with additional data sources
- Deploy to Azure App Service for production use

## Support

For issues or questions, refer to:
- Main README.md in the project root
- .NET Blazor documentation: https://learn.microsoft.com/aspnet/core/blazor
- OpenAI API documentation: https://platform.openai.com/docs
