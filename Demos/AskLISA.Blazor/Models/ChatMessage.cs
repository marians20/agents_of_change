namespace AskLISA.Blazor.Models;

/// <summary>
/// Represents a chat message in the conversation
/// </summary>
public class ChatMessage
{
  public string Role { get; set; } = string.Empty;
  public string Content { get; set; } = string.Empty;
  public DateTime Timestamp { get; set; } = DateTime.UtcNow;
  public string? ImageUrl { get; set; }
  public bool IsError { get; set; }
}
