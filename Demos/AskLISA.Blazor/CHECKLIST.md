# Pre-Launch Checklist

## ✅ Before Running the Application

### 1. Database Setup
- [ ] Copy `nasdaq.db` from original Ask LISA demo to `wwwroot/nasdaq.db`
  ```powershell
  Copy-Item "d:\work\poc\Agents of Change\Demos\Ask LISA\static\nasdaq.db" "d:\work\poc\Agents of Change\Demos\AskLISA.Blazor\wwwroot\nasdaq.db"
  ```

### 2. API Configuration
- [ ] Choose your AI provider (OpenAI or Azure OpenAI)
- [ ] Update `appsettings.Development.json` with your API key
- [ ] For Azure OpenAI: Add your endpoint URL
- [ ] Set `UseAzureOpenAI` to `true` or `false` accordingly

### 3. Verify File Structure
- [ ] Check that avatar images are in `wwwroot/images/`
  - user.jpg
  - chatbot.jpg
- [ ] Verify CSS file exists: `wwwroot/css/app.css`
- [ ] Verify JS file exists: `wwwroot/js/site.js`

### 4. Build and Test
- [ ] Run `dotnet restore`
- [ ] Run `dotnet build`
- [ ] Fix any compilation errors
- [ ] Run `dotnet run`
- [ ] Open browser to https://localhost:5001

### 5. First Test
- [ ] Verify chat interface loads
- [ ] Test dark/light mode toggle
- [ ] Send a simple message (e.g., "Hello")
- [ ] Test a database query (e.g., "What was Microsoft's closing price on January 15, 2024?")
- [ ] Check for streaming responses
- [ ] Verify conversation can be cleared

## ⚙️ Configuration Examples

### For OpenAI (appsettings.Development.json):
```json
{
  "AgentConfig": {
    "ApiKey": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "Model": "gpt-4",
    "Temperature": "0.7",
    "UseAzureOpenAI": "false"
  }
}
```

### For Azure OpenAI (appsettings.Development.json):
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

## 🧪 Test Queries

Once running, try these queries to verify functionality:

### Basic Queries
- [ ] "Hello, who are you?"
- [ ] "What can you help me with?"

### Database Queries
- [ ] "What was Microsoft's closing price on January 15, 2024?"
- [ ] "Show me Apple's stock prices for the first week of January 2024"
- [ ] "What was the highest trading volume for Tesla in 2023?"

### Analytical Queries
- [ ] "Compare Microsoft and Apple stock performance in Q1 2024"
- [ ] "What was the average closing price for Google in 2024?"
- [ ] "Which stock had the highest trading volume on March 1, 2024?"

## 🐛 Troubleshooting

### Database Not Found
**Error**: "Could not find database file"

**Solution**:
```powershell
# Verify database exists
Test-Path "d:\work\poc\Agents of Change\Demos\AskLISA.Blazor\wwwroot\nasdaq.db"

# If false, copy the file
Copy-Item "d:\work\poc\Agents of Change\Demos\Ask LISA\static\nasdaq.db" "d:\work\poc\Agents of Change\Demos\AskLISA.Blazor\wwwroot\nasdaq.db"
```

### API Key Invalid
**Error**: "401 Unauthorized" or "Invalid API key"

**Solution**:
- Verify API key is correct in `appsettings.Development.json`
- Check for extra spaces or quotes
- Ensure key has proper permissions
- For Azure: Verify endpoint URL format

### Port Already in Use
**Error**: "Failed to bind to address"

**Solution**:
Edit `Properties/launchSettings.json` and change ports:
```json
"applicationUrl": "https://localhost:5002;http://localhost:5001"
```

### SignalR Connection Failed
**Error**: "WebSocket connection failed"

**Solution**:
- Check browser console for errors
- Verify no firewall blocking websockets
- Try different browser
- Clear browser cache

## 📋 Post-Launch Checklist

### Security
- [ ] Never commit API keys to source control
- [ ] Use Azure Key Vault for production secrets
- [ ] Enable HTTPS only in production
- [ ] Implement rate limiting
- [ ] Add authentication if exposing publicly

### Performance
- [ ] Monitor memory usage
- [ ] Check SignalR connection limits
- [ ] Implement response caching
- [ ] Add Application Insights

### Deployment
- [ ] Set up CI/CD pipeline
- [ ] Configure production appsettings.json
- [ ] Test on target environment
- [ ] Set up monitoring and alerts
- [ ] Create backup strategy

## 📚 Documentation Reference

- **Quick Start**: See `QUICKSTART.md`
- **Full Documentation**: See `README.md`
- **Migration Info**: See `MIGRATION_GUIDE.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`

## ✨ Ready to Go!

If all items above are checked, you're ready to use Ask LISA Blazor!

Run the application:
```powershell
cd "d:\work\poc\Agents of Change\Demos\AskLISA.Blazor"
dotnet run
```

Then open: https://localhost:5001

---

**Need Help?** Refer to the comprehensive documentation in the project folder.
