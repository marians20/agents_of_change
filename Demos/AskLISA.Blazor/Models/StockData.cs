namespace AskLISA.Blazor.Models;

/// <summary>
/// Represents stock data from the NASDAQ database
/// </summary>
public class StockData
{
  public int Id { get; set; }
  public string Symbol { get; set; } = string.Empty;
  public DateTime Date { get; set; }
  public decimal Open { get; set; }
  public decimal Low { get; set; }
  public decimal High { get; set; }
  public decimal Close { get; set; }
  public long Volume { get; set; }
}
