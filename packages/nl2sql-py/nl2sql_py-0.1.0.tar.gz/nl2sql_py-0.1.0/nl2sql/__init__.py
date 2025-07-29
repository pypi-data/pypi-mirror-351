"""
NL2SQL: Natural Language to SQL Query Converter

A Python package that converts natural language questions into SQL queries
using various LLM providers and executes them on connected databases.
"""

from nl2sql.core.nl2sql import NL2SQL
from nl2sql.core.database import DatabaseManager
from nl2sql.llm_providers.openai_provider import OpenAIProvider
from nl2sql.llm_providers.cohere_provider import CohereProvider
from nl2sql.llm_providers.anthropic_provider import AnthropicProvider

__version__ = "0.1.0"
__author__ = "Mohamed Abdeltawab"

__all__ = [
    "NL2SQL",
    "DatabaseManager", 
    "OpenAIProvider",
    "CohereProvider",
    "AnthropicProvider",
]