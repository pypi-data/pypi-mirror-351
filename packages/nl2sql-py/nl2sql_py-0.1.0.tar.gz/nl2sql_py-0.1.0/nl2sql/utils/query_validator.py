import re
import logging
from typing import List
from sqlalchemy import text

logger = logging.getLogger(__name__)

class QueryValidator:
    """Utility class for validating SQL queries."""
    
    # Dangerous SQL patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r'\bDROP\b',
        r'\bDELETE\b(?!\s+.*\bFROM\b.*\bWHERE\b)',  # DELETE without WHERE
        r'\bTRUNCATE\b',
        r'\bALTER\b',
        r'\bCREATE\b',
        r'\bINSERT\b',
        r'\bUPDATE\b(?!\s+.*\bWHERE\b)',  # UPDATE without WHERE
        r'\bGRANT\b',
        r'\bREVOKE\b',
        r'--',  # SQL comments
        r'/\*.*\*/',  # Multi-line comments
    ]
    
    @staticmethod
    def is_safe_query(query: str) -> tuple[bool, List[str]]:
        """
        Check if a SQL query is safe to execute.
        
        Args:
            query: SQL query to validate
            
        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        issues = []
        query_upper = query.upper().strip()
        
        # Check for dangerous patterns
        for pattern in QueryValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                issues.append(f"Potentially dangerous pattern detected: {pattern}")
        
        # Must start with SELECT for read-only operations
        if not query_upper.startswith('SELECT') and not query_upper.startswith('WITH'):
            issues.append("Only SELECT queries are allowed")
        
        # Check for multiple statements (basic check)
        if ';' in query.strip()[:-1]:  # Allow semicolon at the end
            issues.append("Multiple statements not allowed")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_syntax(engine, query: str) -> tuple[bool, str]:
        """
        Validate SQL syntax using database engine.
        
        Args:
            engine: SQLAlchemy engine
            query: SQL query to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        try:
            with engine.connect() as conn:
                # Use EXPLAIN to validate syntax without executing
                explain_query = f"EXPLAIN {query}"
                conn.execute(text(explain_query))
            return True, ""
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def suggest_improvements(query: str) -> List[str]:
        """
        Suggest improvements for SQL query.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        query_upper = query.upper()
        
        # Check for SELECT *
        if 'SELECT *' in query_upper:
            suggestions.append("Consider specifying column names instead of SELECT *")
        
        # Check for missing LIMIT
        if 'LIMIT' not in query_upper and 'TOP' not in query_upper:
            suggestions.append("Consider adding LIMIT clause to prevent large result sets")
        
        # Check for ORDER BY with LIMIT
        if 'LIMIT' in query_upper and 'ORDER BY' not in query_upper:
            suggestions.append("Consider adding ORDER BY when using LIMIT for consistent results")
        
        return suggestions
