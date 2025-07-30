# db_provider/exceptions.py
"""
Custom exceptions for the db_provider package.
"""

class DatabaseError(Exception):
    """Base exception for all database errors."""
    pass


class ConnectionError(DatabaseError):
    """Exception raised for connection errors."""
    pass


class ConfigurationError(DatabaseError):
    """Exception raised for configuration errors."""
    pass