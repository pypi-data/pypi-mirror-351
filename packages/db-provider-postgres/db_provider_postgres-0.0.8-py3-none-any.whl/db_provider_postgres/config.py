# db_provider/config.py
"""
Configuration helpers for database connections.
"""
import os
from typing import Dict, Any, Optional


def get_env_var(var_name: str, default: Any = None, required: bool = False) -> Any:
    """
    Get environment variable with optional default value.

    Args:
        var_name: Name of the environment variable
        default: Default value to return if var_name is not found
        required: If True, raise an error when var_name is not found

    Returns:
        Value of the environment variable or default

    Raises:
        ValueError: If required is True and var_name is not found
    """
    value = os.environ.get(var_name, default)
    if value is None and required:
        raise ValueError(f"Required environment variable {var_name} is not set")
    return value


def get_db_config_from_env(prefix: str = '') -> Dict[str, Any]:
    """
    Get database configuration from environment variables.

    Args:
        prefix: Optional prefix for environment variables

    Returns:
        Dictionary with database configuration
    """
    config = {
        'host': get_env_var(f'{prefix}DB_HOST', required=True),
        'database': get_env_var(f'{prefix}DATABASE_NAME', required=True),
        'user': get_env_var(f'{prefix}DB_USER', required=True),
        'password': get_env_var(f'{prefix}DB_PASSWORD', required=True),
        'port': int(get_env_var(f'{prefix}DB_PORT', 5432)),
    }

    # Optional parameters
    timeout = get_env_var(f'{prefix}DB_TIMEOUT', None)
    if timeout is not None:
        config['timeout'] = int(timeout)

    return config


def get_db_config(config_dict: Optional[Dict[str, Any]] = None,
                  env_prefix: str = '') -> Dict[str, Any]:
    """
    Get database configuration from dict or environment variables.

    Args:
        config_dict: Optional configuration dictionary
        env_prefix: Optional prefix for environment variables if using env vars

    Returns:
        Dictionary with database configuration
    """
    if config_dict is not None:
        return config_dict
    return get_db_config_from_env(env_prefix)