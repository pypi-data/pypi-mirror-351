from typing import Dict, Any
from sqlalchemy import inspect
import logging

logger = logging.getLogger(__name__)

class SchemaAnalyzer:
    """Utility class for analyzing database schemas."""
    
    @staticmethod
    def analyze_relationships(engine) -> Dict[str, Any]:
        """
        Analyze table relationships and foreign key constraints.
        
        Args:
            engine: SQLAlchemy engine
            
        Returns:
            Dictionary containing relationship information
        """
        inspector = inspect(engine)
        relationships = {}
        
        for table_name in inspector.get_table_names():
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                relationships[table_name] = []
                for fk in foreign_keys:
                    relationships[table_name].append({
                        "local_columns": fk["constrained_columns"],
                        "remote_table": fk["referred_table"],
                        "remote_columns": fk["referred_columns"]
                    })
        
        return relationships
    
    @staticmethod
    def get_column_statistics(engine, table_name: str) -> Dict[str, Any]:
        """
        Get basic statistics about table columns.
        
        Args:
            engine: SQLAlchemy engine
            table_name: Name of the table to analyze
            
        Returns:
            Dictionary containing column statistics
        """
        try:
            with engine.connect() as conn:
                # Get row count
                row_count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                row_count = conn.execute(row_count_query).scalar()
                
                # Get column info
                inspector = inspect(engine)
                columns = inspector.get_columns(table_name)
                
                stats = {
                    "table_name": table_name,
                    "row_count": row_count,
                    "columns": {}
                }
                
                for col in columns:
                    col_name = col["name"]
                    col_type = str(col["type"])
                    
                    # Basic column info
                    stats["columns"][col_name] = {
                        "type": col_type,
                        "nullable": col.get("nullable", True),
                        "primary_key": col.get("primary_key", False)
                    }
                    
                    # Get null count for each column
                    null_query = f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL"
                    null_count = conn.execute(null_query).scalar()
                    stats["columns"][col_name]["null_count"] = null_count
                    stats["columns"][col_name]["null_percentage"] = (null_count / row_count * 100) if row_count > 0 else 0
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get column statistics for {table_name}: {str(e)}")
            return {}
