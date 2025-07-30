# db_provider/utils.py
"""
Utility functions for database operations.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)


def load_sql_file(file_path: str) -> str:
    """
    Load SQL from a file.

    Args:
        file_path: Path to SQL file

    Returns:
        SQL query string

    Raises:
        FileNotFoundError: If file is not found
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    with open(file_path, 'r') as f:
        return f.read()


def format_query_params(query: str, params: Dict[str, Any]) -> str:
    """
    Format query with parameters for logging.

    Args:
        query: SQL query string
        params: Query parameters

    Returns:
        Formatted query string with parameters
    """
    formatted = query
    for key, value in params.items():
        placeholder = f":{key}"
        if placeholder in formatted:
            if isinstance(value, str):
                formatted = formatted.replace(placeholder, f"'{value}'")
            else:
                formatted = formatted.replace(placeholder, str(value))
    return formatted


def sanitize_sql_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize SQL parameters for logging.

    Args:
        params: Query parameters

    Returns:
        Sanitized parameters
    """
    sanitized = params.copy()
    sensitive_keys = ['password', 'passwd', 'secret', 'token', 'api_key', 'apikey']

    for key in sanitized:
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = '********'

    return sanitized


def rows_to_dict_list(rows: List[tuple], columns: List[str]) -> List[Dict[str, Any]]:
    """
    Convert database rows to a list of dictionaries.

    Args:
        rows: List of database row tuples
        columns: List of column names

    Returns:
        List of dictionaries with query results
    """
    return [dict(zip(columns, row)) for row in rows]