using Microsoft.Data.Sqlite;
using System.Text.Json;
using AskLISA.Blazor.Models;

namespace AskLISA.Blazor.Services;

/// <summary>
/// Service for querying the NASDAQ stock database
/// </summary>
public interface IDatabaseService
{
  Task<string> QueryDatabaseAsync(string naturalLanguageQuery);
}

public class DatabaseService : IDatabaseService
{
  private readonly string _connectionString;
  private readonly IOpenAIService _openAIService;
  private readonly ILogger<DatabaseService> _logger;

  public DatabaseService(
      IConfiguration configuration,
      IOpenAIService openAIService,
      ILogger<DatabaseService> logger)
  {
    var dbPath = configuration["DatabasePath"] ?? "wwwroot/nasdaq.db";
    _connectionString = $"Data Source={dbPath}";
    _openAIService = openAIService;
    _logger = logger;
  }

  /// <summary>
  /// Queries the database using natural language
  /// </summary>
  public async Task<string> QueryDatabaseAsync(string naturalLanguageQuery)
  {
    try
    {
      // Convert natural language to SQL
      var sql = await ConvertTextToSqlAsync(naturalLanguageQuery);
      _logger.LogInformation("Generated SQL: {Sql}", sql);

      // Execute the query
      var results = await ExecuteQueryAsync(sql);
      return JsonSerializer.Serialize(results);
    }
    catch (Exception ex)
    {
      _logger.LogError(ex, "Error querying database");
      throw;
    }
  }

  private async Task<string> ConvertTextToSqlAsync(string text)
  {
    var prompt = $@"
Generate a well-formed SQLite query from the prompt below. Return
the SQL only. Do not use markdown formatting, and do not use SELECT *.

PROMPT: {text}

The database targeted by the query contains the following table:

CREATE TABLE Stocks (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Symbol TEXT NOT NULL,   -- Stock symbol (for example, ""MSFT"")
    Date DATE NOT NULL,     -- Date
    Open NUMERIC NOT NULL,  -- Opening price of the stock on that date
    Low NUMERIC NOT NULL,   -- Lowest price of the stock on that date
    High NUMERIC NOT NULL,  -- Highest price of the stock on that date
    Close NUMERIC NOT NULL, -- Closing price of the stock on that date
    Volume INT NOT NULL     -- Number of shares traded on that date
)
";

    var sql = await _openAIService.GetCompletionAsync(prompt, temperature: 0.2);

    // Remove any markdown formatting
    sql = sql.Replace("```sql", "").Replace("```", "").Trim();

    return sql;
  }

  private async Task<List<Dictionary<string, object>>> ExecuteQueryAsync(string sql)
  {
    var results = new List<Dictionary<string, object>>();

    using var connection = new SqliteConnection(_connectionString);
    await connection.OpenAsync();

    using var command = connection.CreateCommand();
    command.CommandText = sql;

    using var reader = await command.ExecuteReaderAsync();

    while (await reader.ReadAsync())
    {
      var row = new Dictionary<string, object>();
      for (int i = 0; i < reader.FieldCount; i++)
      {
        var value = reader.GetValue(i);
        row[reader.GetName(i)] = value ?? DBNull.Value;
      }
      results.Add(row);
    }

    return results;
  }
}
