import logging
from typing import Dict, Any, Optional, Union
import pandas as pd
from nl2sql.llm_providers.base import BaseLLMProvider
from nl2sql.llm_providers.openai_provider import OpenAIProvider
from nl2sql.llm_providers.cohere_provider import CohereProvider
from nl2sql.llm_providers.anthropic_provider import AnthropicProvider
from nl2sql.core.database import DatabaseManager

logger = logging.getLogger(__name__)

class NL2SQL:
    """Main class for natural language to SQL conversion and execution."""
    
    def __init__(self, 
                 database_url: str,
                 llm_provider: Union[str, BaseLLMProvider],
                 api_key: Optional[str] = None,
                 **llm_config):
        """
        Initialize NL2SQL converter.
        
        Args:
            database_url: Database connection URL
            llm_provider: LLM provider name or instance
            api_key: API key for LLM provider
            **llm_config: Additional LLM configuration
        """
        # Initialize database manager
        self.db_manager = DatabaseManager(database_url)
        
        # Initialize LLM provider
        if isinstance(llm_provider, str):
            self.llm_provider = self._create_provider(llm_provider, api_key, **llm_config)
        elif isinstance(llm_provider, BaseLLMProvider):
            self.llm_provider = llm_provider
        else:
            raise ValueError("llm_provider must be a string or BaseLLMProvider instance")
        
        # Cache schema info for better performance
        self._schema_cache = None
    
    def _create_provider(self, provider_name: str, api_key: str, **config) -> BaseLLMProvider:
        """Create LLM provider instance."""
        providers = {
            "openai": OpenAIProvider,
            "cohere": CohereProvider,
            "anthropic": AnthropicProvider,
        }
        
        if provider_name.lower() not in providers:
            raise ValueError(f"Unsupported provider: {provider_name}. Supported: {list(providers.keys())}")
        
        if not api_key:
            raise ValueError(f"API key required for {provider_name}")
        
        return providers[provider_name.lower()](api_key, **config)
    
    def get_schema_info(self, refresh: bool = False) -> str:
        """Get database schema information with caching."""
        if self._schema_cache is None or refresh:
            self._schema_cache = self.db_manager.get_schema_info()
        return self._schema_cache
    
    def ask(self, question: str, 
            execute: bool = True,
            explain: bool = False,
            validate: bool = True,
            **llm_kwargs) -> Dict[str, Any]:
        """
        Convert natural language question to SQL and optionally execute it.
        
        Args:
            question: Natural language question
            execute: Whether to execute the generated SQL
            explain: Whether to include explanation of the query
            validate: Whether to validate SQL before execution
            **llm_kwargs: Additional arguments for LLM provider
            
        Returns:
            Dictionary containing SQL query, results, and explanation
        """
        result = {
            "question": question,
            "sql_query": None,
            "results": None,
            "explanation": None,
            "error": None
        }
        
        try:
            # Generate SQL query
            schema_info = self.get_schema_info()
            sql_query = self.llm_provider.generate_sql(question, schema_info, **llm_kwargs)
            result["sql_query"] = sql_query
            
            # Validate query if requested
            if validate and not self.db_manager.validate_query(sql_query):
                logger.warning("Generated SQL query failed validation")
                result["error"] = "Generated SQL query failed validation"
                return result
            
            # Execute query if requested
            if execute:
                try:
                    results_df = self.db_manager.execute_query(sql_query)
                    result["results"] = results_df
                except Exception as e:
                    result["error"] = f"Query execution failed: {str(e)}"
                    return result
            
            # Generate explanation if requested
            if explain:
                try:
                    explanation = self.llm_provider.explain_query(sql_query)
                    result["explanation"] = explanation
                except Exception as e:
                    logger.warning(f"Failed to generate explanation: {str(e)}")
            
        except Exception as e:
            result["error"] = f"Failed to generate SQL: {str(e)}"
            logger.error(f"Error in ask method: {str(e)}")
        
        return result
    
    def execute_sql(self, sql_query: str) -> pd.DataFrame:
        """
        Execute SQL query directly.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            Query results as DataFrame
        """
        return self.db_manager.execute_query(sql_query)
    
    def explain_sql(self, sql_query: str) -> str:
        """
        Get natural language explanation of SQL query.
        
        Args:
            sql_query: SQL query to explain
            
        Returns:
            Natural language explanation
        """
        return self.llm_provider.explain_query(sql_query)
    
    def get_tables(self) -> list:
        """Get list of available tables."""
        return self.db_manager.get_table_names()
    
    def close(self):
        """Close database connection."""
        self.db_manager.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
