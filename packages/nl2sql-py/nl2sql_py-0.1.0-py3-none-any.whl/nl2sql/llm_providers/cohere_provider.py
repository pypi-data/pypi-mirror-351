import cohere
from typing import Dict, Any, Optional
from .base import BaseLLMProvider

class CohereProvider(BaseLLMProvider):
    """Cohere LLM provider for SQL generation."""
    
    def __init__(self, api_key: str, model: str = "command", **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = cohere.Client(api_key)
        self.model = model
    
    def generate_sql(self, question: str, schema_info: str, **kwargs) -> str:
        """Generate SQL query using Cohere models."""
        
        prompt = f"""You are an expert SQL query generator. Convert the natural language question into a valid SQL query based on the provided database schema.

Database Schema:
{schema_info}

Question: {question}

Rules:
- Only use tables and columns that exist in the schema
- Generate syntactically correct SQL
- Return only the SQL query, no explanations
- Use appropriate JOINs when needed

SQL Query:"""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                temperature=kwargs.get("temperature", 0.1),
                max_tokens=kwargs.get("max_tokens", 500),
                stop_sequences=["--", "\n\n"]
            )
            
            sql_query = response.generations[0].text.strip()
            
            return sql_query
            
        except Exception as e:
            raise Exception(f"Cohere API error: {str(e)}")
    
    def explain_query(self, sql_query: str, **kwargs) -> str:
        """Explain SQL query in natural language."""
        
        prompt = f"""Explain what this SQL query does in simple, clear language:

{sql_query}

Explanation:"""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                temperature=0.3,
                max_tokens=300
            )
            
            return response.generations[0].text.strip()
            
        except Exception as e:
            raise Exception(f"Cohere API error: {str(e)}")
