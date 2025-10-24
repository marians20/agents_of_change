using AskLISA.Blazor.Models;
using System.Text;
using System.Text.Json;

namespace AskLISA.Blazor.Services;

/// <summary>
/// Service that orchestrates multiple AI agents (Database, Quant, Visualization, Team Lead)
/// </summary>
public interface IAgentTeamService
{
  IAsyncEnumerable<string> ProcessQueryAsync(string userInput, string sessionId, List<ChatMessage> conversationHistory);
}

public class AgentTeamService : IAgentTeamService
{
  private readonly IOpenAIService _openAIService;
  private readonly IDatabaseService _databaseService;
  private readonly ILogger<AgentTeamService> _logger;
  private const string MODEL = "gpt-4";

  public AgentTeamService(
      IOpenAIService openAIService,
      IDatabaseService databaseService,
      ILogger<AgentTeamService> logger)
  {
    _openAIService = openAIService;
    _databaseService = databaseService;
    _logger = logger;
  }

  /// <summary>
  /// Processes user query through the team of agents
  /// </summary>
  public async IAsyncEnumerable<string> ProcessQueryAsync(
      string userInput,
      string sessionId,
      List<ChatMessage> conversationHistory)
  {
    var teamLeadInstructions = @"
You are an analyst named LISA who leads a team of stock experts.
When asked about stock prices, use daily closing prices unless
directed to do otherwise. Assume that monetary amounts are in
dollars. Round such amounts to the nearest dollar in your output,
and use commas as separators for amounts greater than $999.

You have access to:
1. A NASDAQ database containing daily OHLC prices and trading volumes for
   selected NASDAQ stocks from 2020 through 2024.
2. The ability to perform calculations.
3. The ability to generate charts and visualizations.

When responding to queries about stock data, you should:
- Analyze the user's question
- Determine if database queries are needed
- Perform calculations if necessary
- Provide clear, well-formatted responses

IMPORTANT: Be concise and professional in your responses.
";

    // Check if the query requires database access
    var requiresDatabase = await DetermineIfDatabaseNeededAsync(userInput);

    StringBuilder context = new StringBuilder();

    if (requiresDatabase)
    {
      try
      {
        _logger.LogInformation("Query requires database access");
        var dbResults = await _databaseService.QueryDatabaseAsync(userInput);
        context.AppendLine("Database query results:");
        context.AppendLine(dbResults);
        context.AppendLine();
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Error querying database");
        context.AppendLine($"Error accessing database: {ex.Message}");
      }
    }

    // Build the enhanced prompt with context
    var enhancedPrompt = userInput;
    if (context.Length > 0)
    {
      enhancedPrompt = $"{context}\n\nUser question: {userInput}";
    }

    // Stream the response from the team lead
    await foreach (var chunk in _openAIService.GetStreamingCompletionAsync(
        enhancedPrompt,
        teamLeadInstructions,
        conversationHistory))
    {
      yield return chunk;
    }
  }

  private async Task<bool> DetermineIfDatabaseNeededAsync(string userInput)
  {
    var prompt = $@"
Does the following user query require accessing a stock price database?
Answer with only 'yes' or 'no'.

Query: {userInput}
";

    try
    {
      var response = await _openAIService.GetCompletionAsync(prompt, temperature: 0.0);
      return response.Trim().ToLower().Contains("yes");
    }
    catch
    {
      // Default to true if we can't determine
      return true;
    }
  }
}
