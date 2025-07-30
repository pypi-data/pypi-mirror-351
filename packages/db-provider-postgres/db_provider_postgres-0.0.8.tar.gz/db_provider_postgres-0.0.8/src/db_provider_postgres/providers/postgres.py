import contextlib
from typing import Dict, Any, Optional

import sqlalchemy as sa
from sqlalchemy.engine import URL, Connection
from sqlalchemy.exc import SQLAlchemyError

from ..config import get_db_config
from ..exceptions import ConfigurationError
from .base import BaseDatabaseProvider


class PostgresDatabaseProvider(BaseDatabaseProvider):
    """PostgreSQL database provider."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, env_prefix: str = '',
                 isolation_level: str = "AUTOCOMMIT", pool_size: int = 5,
                 max_overflow: int = 10, pool_timeout: int = 30,
                 pool_recycle: int = 1800):
        """
        Initialize PostgreSQL database provider.

        Args:
            config: Configuration dictionary with host, database, user, password, port
            env_prefix: Prefix for environment variables if config is None
            isolation_level: Transaction isolation level
            pool_size: SQLAlchemy connection pool size
            max_overflow: Maximum number of connections to allow above pool_size
            pool_timeout: Number of seconds to wait before giving up on getting a connection
            pool_recycle: Number of seconds after which a connection is recycled
        """
        self.isolation_level = isolation_level
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        super().__init__(config, env_prefix)

    def _setup(self) -> None:
        """Set up the PostgreSQL connection engine."""
        try:
            # Get configuration from either dict or environment variables
            self.db_config = get_db_config(self.config, self.env_prefix)

            # Create SQLAlchemy URL object
            url_object = self._create_url_object()

            # Get connection arguments
            connect_args = self._get_connect_args()

            # Create SQLAlchemy engine
            self.engine = sa.create_engine(
                url_object,
                isolation_level=self.isolation_level,
                connect_args=connect_args,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle
            )
        except (ValueError, KeyError) as e:
            raise ConfigurationError(f"Database configuration error: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to create database engine: {e}")

    def _create_url_object(self) -> URL:
        """
        Create SQLAlchemy URL object from configuration.

        Returns:
            SQLAlchemy URL object
        """
        return URL.create(
            "postgresql+psycopg",
            username=self.db_config["user"],
            password=self.db_config["password"],
            host=self.db_config["host"],
            port=self.db_config["port"],
            database=self.db_config["database"],
        )

    def _get_connect_args(self) -> Dict[str, Any]:
        """
        Get connection arguments.

        Returns:
            Dictionary with connection arguments
        """
        connect_args = {'connect_timeout': self.db_config.get('timeout', 10)}
        return connect_args

    def get_connection(self) -> Connection:
        """
        Get a new database connection.

        Returns:
            SQLAlchemy connection object

        Raises:
            ConnectionError: If connection fails
        """
        try:
            return self.engine.connect()
        except SQLAlchemyError as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    @contextlib.contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Yields:
            SQLAlchemy connection object with transaction

        Raises:
            ConnectionError: If transaction fails
        """
        connection = None
        try:
            connection = self.get_connection()
            with connection.begin():
                yield connection
        except SQLAlchemyError as e:
            if connection:
                connection.close()
            raise ConnectionError(f"Transaction failed: {e}")
        finally:
            if connection:
                connection.close()

    def execute_query_with_result(self, query: str, params: Optional[Dict[str, Any]] = None) -> list:
        """
        Execute a query and return the result as a list of dictionaries.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries with query results
        """
        with self.connection() as conn:
            if params:
                result = conn.execute(sa.text(query), params)
            else:
                result = conn.execute(sa.text(query))

            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
