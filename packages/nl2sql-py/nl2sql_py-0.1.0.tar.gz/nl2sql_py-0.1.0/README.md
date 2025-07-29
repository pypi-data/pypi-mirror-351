# NL2SQL: Natural Language to SQL Converter

A Python package that converts natural language questions into SQL queries using Large Language Models (LLMs) and executes them on connected databases.

## Features

- 🤖 **Multiple LLM Providers**: Support for OpenAI GPT, Cohere, and Anthropic Claude
- 🗄️ **Database Agnostic**: Works with any SQLAlchemy-supported database
- 🔍 **Schema Analysis**: Automatic database schema detection and analysis
- ✅ **Query Validation**: Built-in SQL query validation and safety checks
- 📊 **Pandas Integration**: Results returned as pandas DataFrames
- 🛡️ **Safety First**: Read-only query enforcement and dangerous pattern detection
- 🔧 **Extensible**: Easy to add new LLM providers and database types

## Installation

```bash
pip install nl2sql
```

Or install from source:

```bash
git clone https://github.com/MohamedElghobary/nl2sql.git
cd nl2sql
pip install -e .
```

### Database Driver Dependencies

Install additional database drivers as needed:

```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install mysql-connector-python

# SQL Server
pip install pyodbc

# Oracle
pip install cx_Oracle
```

## Quick Start

```python
import os
from nl2sql import NL2SQL

# Initialize with your preferred LLM provider
nl2sql = NL2SQL(
    database_url="sqlite:///your_database.db",
    llm_provider="openai",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Ask a natural language question
result = nl2sql.ask("Show me the top 10 customers by total orders")

print(f"Generated SQL: {result['sql_query']}")
print(f"Results:\n{result['results']}")

# Close connection
nl2sql.close()
```

## Usage Examples

### Basic Usage

```python
from nl2sql import NL2SQL

# Using context manager (recommended)
with NL2SQL(
    database_url="postgresql://user:pass@localhost/mydb",
    llm_provider="openai",
    api_key="your-openai-key"
) as nl2sql:
    
    # Simple query
    result = nl2sql.ask("How many users signed up last month?")
    
    # Query with explanation
    result = nl2sql.ask(
        "What's the average order value by region?",
        explain=True
    )
    
    # Generate SQL without execution
    result = nl2sql.ask(
        "Find duplicate email addresses",
        execute=False
    )
```

### Multiple LLM Providers

```python
# OpenAI GPT
nl2sql_openai = NL2SQL(
    database_url=db_url,
    llm_provider="openai",
    api_key=openai_key,
    model="gpt-4"
)

# Cohere
nl2sql_cohere = NL2SQL(
    database_url=db_url,
    llm_provider="cohere",
    api_key=cohere_key
)

# Anthropic Claude
nl2sql_anthropic = NL2SQL(
    database_url=db_url,
    llm_provider="anthropic",
    api_key=anthropic_key
)
```

### Advanced Configuration

```python
nl2sql = NL2SQL(
    database_url="your-db-url",
    llm_provider="openai",
    api_key="your-key",
    model="gpt-4",
    temperature=0.1,
    max_tokens=1000
)

# Custom query parameters
result = nl2sql.ask(
    "Complex analytical question here...",
    temperature=0.05,  # Override default
    validate=True,     # Validate before execution
    explain=True       # Include explanation
)
```

### Direct SQL Operations

```python
with NL2SQL(db_url, "openai", api_key) as nl2sql:
    
    # Execute custom SQL
    results = nl2sql.execute_sql("SELECT COUNT(*) FROM users")
    
    # Explain existing SQL
    explanation = nl2sql.explain_sql("SELECT * FROM orders WHERE status = 'pending'")
    
    # Get database schema
    tables = nl2sql.get_tables()
    schema_info = nl2sql.get_schema_info()
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY=your-openai-api-key
COHERE_API_KEY=your-cohere-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

DATABASE_URL=your-database-connection-string
```

### Database Connection Strings

```python
# SQLite
database_url = "sqlite:///path/to/database.db"

# PostgreSQL
database_url = "postgresql://username:password@host:port/database"

# MySQL
database_url = "mysql+mysqlconnector://username:password@host:port/database"

# SQL Server
database_url = "mssql+pyodbc://username:password@host:port/database?driver=ODBC+Driver+17+for+SQL+Server"
```

## API Reference

### NL2SQL Class

```python
class NL2SQL:
    def __init__(self, database_url: str, llm_provider: str, api_key: str, **kwargs)
    
    def ask(self, question: str, execute: bool = True, explain: bool = False, 
            validate: bool = True, **llm_kwargs) -> Dict[str, Any]
    
    def execute_sql(self, sql_query: str) -> pd.DataFrame
    
    def explain_sql(self, sql_query: str) -> str
    
    def get_tables(self) -> List[str]
    
    def get_schema_info(self, refresh: bool = False) -> str
    
    def close(self)
```

### Response Format

The `ask()` method returns a dictionary with:

```python
{
    "question": "Original natural language question",
    "sql_query": "Generated SQL query",
    "results": "pandas.DataFrame with results (if executed)",
    "explanation": "Natural language explanation (if requested)",
    "error": "Error message (if any)"
}
```

## Safety Features

- **Read-only Operations**: Only SELECT queries are allowed by default
- **Query Validation**: Dangerous patterns are detected and blocked
- **SQL Injection Protection**: Parameterized queries and input validation
- **Schema-based Generation**: Queries are generated based on actual database schema

## Custom LLM Providers

You can extend the package with custom LLM providers:

```python
from nl2sql.llm_providers.base import BaseLLMProvider

class MyCustomProvider(BaseLLMProvider):
    def generate_sql(self, question: str, schema_info: str, **kwargs) -> str:
        # Implement your custom logic here
        pass
    
    def explain_query(self, sql_query: str, **kwargs) -> str:
        # Implement query explanation logic
        pass

# Use custom provider
nl2sql = NL2SQL(
    database_url=db_url,
    llm_provider=MyCustomProvider(api_key="your-key")
)
```

## Error Handling

```python
try:
    result = nl2sql.ask("Your question here")
    
    if result['error']:
        print(f"Error: {result['error']}")
    else:
        print(f"Results: {result['results']}")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Development Setup

```bash
git clone https://github.com/MohamedElghobary/nl2sql.git
cd nl2sql

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black nl2sql/
flake8 nl2sql/
```

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0
- Initial release
- Support for OpenAI, Cohere, and Anthropic providers
- SQLAlchemy-based database connectivity
- Basic query validation and safety features

## Support

- 📖 Documentation: [Link to docs]
- 🐛 Issues: [GitHub Issues](https://github.com/MohamedElghobary/nl2sql/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/MohamedElghobary/nl2sql/discussions)
