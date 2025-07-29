import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, connection_string: str):
        """
        Initialize database manager.
        
        Args:
            connection_string: SQLAlchemy connection string
        """
        self.connection_string = connection_string
        self.engine = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.engine = create_engine(self.connection_string)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def get_schema_info(self, include_sample_data: bool = True) -> str:
        """
        Get database schema information as formatted string.
        
        Args:
            include_sample_data: Whether to include sample data for each table
            
        Returns:
            Formatted schema information
        """
        try:
            inspector = inspect(self.engine)
            schema_info = []
            
            # Get all table names
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                schema_info.append(f"\nTable: {table_name}")
                
                # Get columns
                columns = inspector.get_columns(table_name)
                schema_info.append("Columns:")
                for col in columns:
                    col_info = f"  - {col['name']} ({col['type']}"
                    if not col.get('nullable', True):
                        col_info += ", NOT NULL"
                    if col.get('primary_key'):
                        col_info += ", PRIMARY KEY"
                    col_info += ")"
                    schema_info.append(col_info)
                
                # Get foreign keys
                foreign_keys = inspector.get_foreign_keys(table_name)
                if foreign_keys:
                    schema_info.append("Foreign Keys:")
                    for fk in foreign_keys:
                        fk_info = f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}"
                        schema_info.append(fk_info)
                
                # Include sample data if requested
                if include_sample_data:
                    try:
                        sample_query = f"SELECT * FROM {table_name} LIMIT 3"
                        sample_data = self.execute_query(sample_query)
                        if not sample_data.empty:
                            schema_info.append("Sample Data:")
                            schema_info.append(sample_data.to_string(index=False))
                    except Exception as e:
                        logger.warning(f"Could not fetch sample data for {table_name}: {str(e)}")
                
                schema_info.append("-" * 50)
            
            return "\n".join(schema_info)
            
        except Exception as e:
            logger.error(f"Failed to get schema info: {str(e)}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results as pandas DataFrame
        """
        try:
            with self.engine.connect() as conn:
                result = pd.read_sql(text(query), conn)
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"SQL execution error: {str(e)}")
            raise Exception(f"Query execution failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {str(e)}")
            raise
    
    def validate_query(self, query: str) -> bool:
        """
        Validate SQL query without executing it.
        
        Args:
            query: SQL query to validate
            
        Returns:
            True if query is valid, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                # Use EXPLAIN to validate without executing
                explain_query = f"EXPLAIN {query}"
                conn.execute(text(explain_query))
            return True
        except Exception as e:
            logger.warning(f"Query validation failed: {str(e)}")
            return False
    
    def get_table_names(self) -> List[str]:
        """Get list of all table names."""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            logger.error(f"Failed to get table names: {str(e)}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
