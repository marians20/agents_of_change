using Azure;
using Azure.AI.OpenAI;
using OpenAI.Chat;
using AskLISA.Blazor.Models;
using System.ClientModel;
using System.Text;
using ChatMessageModel = AskLISA.Blazor.Models.ChatMessage;
using OpenAIChatMessage = OpenAI.Chat.ChatMessage;

namespace AskLISA.Blazor.Services;

/// <summary>
/// Service for interacting with OpenAI/Azure OpenAI
/// </summary>
public interface IOpenAIService
{
  Task<string> GetCompletionAsync(string prompt, double temperature = 0.7, string? systemMessage = null);
  IAsyncEnumerable<string> GetStreamingCompletionAsync(string prompt, string? systemMessage = null, List<ChatMessageModel>? conversationHistory = null);
}

public class OpenAIService : IOpenAIService
{
  private readonly ChatClient _chatClient;
  private readonly AgentConfig _config;
  private readonly ILogger<OpenAIService> _logger;

  public OpenAIService(
      IConfiguration configuration,
      ILogger<OpenAIService> logger)
  {
    _logger = logger;

    // Load configuration
    _config = new AgentConfig
    {
      ApiKey = configuration["AgentConfig:ApiKey"] ?? throw new InvalidOperationException("ApiKey not configured"),
      Endpoint = configuration["AgentConfig:Endpoint"] ?? "",
      Model = configuration["AgentConfig:Model"] ?? "gpt-4",
      Temperature = double.Parse(configuration["AgentConfig:Temperature"] ?? "0.7"),
      UseAzureOpenAI = bool.Parse(configuration["AgentConfig:UseAzureOpenAI"] ?? "false")
    };

    // Initialize the appropriate client
    if (_config.UseAzureOpenAI && !string.IsNullOrEmpty(_config.Endpoint))
    {
      var azureClient = new AzureOpenAIClient(
          new Uri(_config.Endpoint),
          new AzureKeyCredential(_config.ApiKey));
      _chatClient = azureClient.GetChatClient(_config.Model);
    }
    else
    {
      var openAIClient = new OpenAI.Chat.ChatClient(_config.Model, _config.ApiKey);
      _chatClient = openAIClient;
    }
  }

  /// <summary>
  /// Gets a single completion response
  /// </summary>
  public async Task<string> GetCompletionAsync(string prompt, double temperature = 0.7, string? systemMessage = null)
  {
    try
    {
      var messages = new List<OpenAIChatMessage>();

      if (!string.IsNullOrEmpty(systemMessage))
      {
        messages.Add(OpenAIChatMessage.CreateSystemMessage(systemMessage));
      }

      messages.Add(OpenAIChatMessage.CreateUserMessage(prompt));

      var options = new ChatCompletionOptions
      {
        Temperature = (float)temperature
      };

      var response = await _chatClient.CompleteChatAsync(messages, options);
      return response.Value.Content[0].Text;
    }
    catch (Exception ex)
    {
      _logger.LogError(ex, "Error getting completion");
      throw;
    }
  }

  /// <summary>
  /// Gets a streaming completion response
  /// </summary>
  public async IAsyncEnumerable<string> GetStreamingCompletionAsync(
      string prompt,
      string? systemMessage = null,
      List<ChatMessageModel>? conversationHistory = null)
  {
    var messages = new List<OpenAIChatMessage>();

    if (!string.IsNullOrEmpty(systemMessage))
    {
      messages.Add(OpenAIChatMessage.CreateSystemMessage(systemMessage));
    }

    // Add conversation history if provided
    if (conversationHistory != null)
    {
      foreach (var msg in conversationHistory)
      {
        if (msg.Role == "user")
        {
          messages.Add(OpenAIChatMessage.CreateUserMessage(msg.Content));
        }
        else if (msg.Role == "assistant")
        {
          messages.Add(OpenAIChatMessage.CreateAssistantMessage(msg.Content));
        }
      }
    }

    messages.Add(OpenAIChatMessage.CreateUserMessage(prompt));

    var options = new ChatCompletionOptions
    {
      Temperature = (float)_config.Temperature
    };

    await foreach (var update in _chatClient.CompleteChatStreamingAsync(messages, options))
    {
      foreach (var contentPart in update.ContentUpdate)
      {
        if (!string.IsNullOrEmpty(contentPart.Text))
        {
          yield return contentPart.Text;
        }
      }
    }
  }
}
