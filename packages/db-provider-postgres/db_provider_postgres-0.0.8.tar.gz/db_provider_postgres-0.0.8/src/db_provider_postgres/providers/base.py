"""
Base database provider class.
"""
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Dict, Any, Generator, Optional


class BaseDatabaseProvider(ABC):
    """Abstract base class for database providers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, env_prefix: str = ''):
        """
        Initialize base database provider.

        Args:
            config: Configuration dictionary
            env_prefix: Prefix for environment variables if config is None
        """
        self.config = config
        self.env_prefix = env_prefix
        self.engine = None
        self._setup()

    @abstractmethod
    def _setup(self) -> None:
        """Set up the database connection engine."""
        pass

    @abstractmethod
    def get_connection(self):
        """Get a new database connection."""
        pass

    @contextmanager
    def connection(self) -> Generator[Any, None, None]:
        """
        Context manager for database connections.

        Yields:
            Database connection

        Raises:
            ConnectionError: If connection fails
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
        finally:
            if conn is not None:
                conn.close()

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a query and return the result.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query result
        """
        with self.connection() as conn:
            if params:
                result = conn.execute(query, params)
            else:
                result = conn.execute(query)
            return result
