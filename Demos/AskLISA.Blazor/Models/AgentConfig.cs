namespace AskLISA.Blazor.Models;

/// <summary>
/// Configuration for OpenAI/Azure OpenAI settings
/// </summary>
public class AgentConfig
{
  public string ApiKey { get; set; } = string.Empty;
  public string Endpoint { get; set; } = string.Empty;
  public string Model { get; set; } = "gpt-4";
  public double Temperature { get; set; } = 0.2;
  public bool UseAzureOpenAI { get; set; } = false;
}
