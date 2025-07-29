import anthropic
from typing import Dict, Any, Optional
from .base import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider for SQL generation."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_sql(self, question: str, schema_info: str, **kwargs) -> str:
        """Generate SQL query using Anthropic Claude."""
        
        prompt = f"""You are an expert SQL query generator. Convert the natural language question into a valid SQL query based on the provided database schema.

Database Schema:
{schema_info}

Question: {question}

Rules:
1. Only use tables and columns that exist in the schema
2. Generate syntactically correct SQL
3. Return only the SQL query, no explanations
4. Use appropriate JOINs when needed
5. Handle aggregations, filtering, and sorting as requested

Generate the SQL query:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 500),
                temperature=kwargs.get("temperature", 0.1),
                messages=[{"role": "user", "content": prompt}]
            )
            
            sql_query = response.content[0].text.strip()
            
            # Clean up the response
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            return sql_query.strip()
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def explain_query(self, sql_query: str, **kwargs) -> str:
        """Explain SQL query in natural language."""
        
        prompt = f"""Explain what this SQL query does in simple, clear language:

{sql_query}

Provide a concise explanation of what data is being retrieved and how."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
