#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APILama Logging Configuration

This module configures logging for APILama using the PyLogs package.
It ensures that environment variables are loaded before any other libraries.
"""

import os
import sys
from pathlib import Path

# Add the loglama package to the path if it's not already installed
# The correct path should be: /home/tom/github/py-lama/loglama
loglama_path = Path(__file__).parent.parent.parent / 'loglama'
if loglama_path.exists() and str(loglama_path) not in sys.path:
    sys.path.insert(0, str(loglama_path))
    print(f"Added PyLogs path: {loglama_path}")
else:
    # Try an alternative path calculation
    alt_loglama_path = Path('/home/tom/github/py-lama/loglama')
    if alt_loglama_path.exists() and str(alt_loglama_path) not in sys.path:
        sys.path.insert(0, str(alt_loglama_path))
        print(f"Added alternative PyLogs path: {alt_loglama_path}")

# Import PyLogs components
try:
    from loglama.config.env_loader import load_env, get_env
    from loglama.utils import configure_logging
    from loglama.utils.context import LogContext, capture_context
    from loglama.formatters import ColoredFormatter, JSONFormatter
    from loglama.handlers import SQLiteHandler, EnhancedRotatingFileHandler
    LOGLAMA_AVAILABLE = True
except ImportError as e:
    print(f"PyLogs import error: {e}")
    LOGLAMA_AVAILABLE = False


def init_logging():
    """
    Initialize logging for APILama using PyLogs.
    
    This function should be called at the very beginning of the application
    before any other imports or configurations are done.
    """
    if not LOGLAMA_AVAILABLE:
        print("PyLogs package not available. Using default logging configuration.")
        return False
    
    # Load environment variables from .env files
    load_env(verbose=True)
    
    # Get logging configuration from environment variables
    log_level = get_env('APILAMA_LOG_LEVEL', 'INFO')
    log_dir = get_env('APILAMA_LOG_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'))
    db_enabled = get_env('APILAMA_DB_LOGGING', 'true').lower() in ('true', 'yes', '1')
    db_path = get_env('APILAMA_DB_PATH', os.path.join(log_dir, 'apilama.db'))
    json_format = get_env('APILAMA_JSON_LOGS', 'true').lower() in ('true', 'yes', '1')  # Default to JSON format for better integration
    structured_logging = get_env('APILAMA_STRUCTURED_LOGGING', 'true').lower() in ('true', 'yes', '1')
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Check if the database exists and handle schema changes
    if db_enabled and os.path.exists(db_path):
        try:
            # Try to connect to the database to check if it has the correct schema
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info(logs)")
            columns = [column[1] for column in cursor.fetchall()]
            conn.close()
            
            # Check if the required columns exist
            required_columns = ['level', 'level_no', 'logger_name', 'message']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"Database schema outdated. Missing columns: {missing_columns}")
                print(f"Recreating database at {db_path}")
                os.remove(db_path)
                print("Old database removed. A new one will be created automatically.")
        except Exception as e:
            print(f"Error checking database schema: {e}")
            print(f"Recreating database at {db_path}")
            os.remove(db_path)
            print("Old database removed. A new one will be created automatically.")
    
    # Configure logging
    logger = configure_logging(
        name='apilama',
        level=log_level,
        console=True,
        file=True,
        file_path=os.path.join(log_dir, 'apilama.log'),
        database=db_enabled,
        db_path=db_path,
        json=json_format,  # Use JSON format for better integration with LogLama
        context_filter=True,
        structured=structured_logging  # Use structured logging for better integration
    )
    
    # Add standard context information that will be included in all logs
    LogContext.set_context(
        component='apilama',
        service='apilama',
        version=get_env('APILAMA_VERSION', '1.0.0')
    )
    
    # Log initialization
    logger.info('APILama logging initialized with PyLogs')
    return True


def get_logger(name=None):
    """
    Get a logger instance.
    
    Args:
        name (str, optional): Name of the logger. Defaults to 'apilama'.
        
    Returns:
        Logger: A configured logger instance.
    """
    if not name:
        name = 'apilama'
    
    if LOGLAMA_AVAILABLE:
        from loglama import get_logger as loglama_get_logger
        return loglama_get_logger(name)
    else:
        import logging
        return logging.getLogger(name)


def log_request_context(func):
    """
    Decorator to add request context to logs.
    
    Args:
        func: The function to decorate.
        
    Returns:
        The decorated function.
    """
    from functools import wraps
    from flask import request
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        if LOGLAMA_AVAILABLE and hasattr(request, 'remote_addr'):
            context = {
                'ip': request.remote_addr,
                'method': request.method,
                'url': request.url,
                'endpoint': request.endpoint,
                'user_agent': request.user_agent.string if request.user_agent else 'Unknown'
            }
            with LogContext(**context):
                return func(*args, **kwargs)
        return func(*args, **kwargs)
    
    return wrapper


def log_api_call(endpoint, success=True, error=None):
    """
    Log an API call.
    
    Args:
        endpoint (str): The API endpoint that was called.
        success (bool, optional): Whether the API call was successful. Defaults to True.
        error (str, optional): The error message if the API call failed. Defaults to None.
    """
    logger = get_logger('apilama.api')
    
    if success:
        logger.info(f'API call to {endpoint} successful')
    else:
        logger.error(f'API call to {endpoint} failed: {error}')


def log_file_operation(operation, filename=None, success=True, error=None):
    """
    Log a file operation.
    
    Args:
        operation (str): The file operation that was performed (e.g., 'read', 'write', 'list').
        filename (str, optional): The name of the file that was operated on. Defaults to None.
        success (bool, optional): Whether the file operation was successful. Defaults to True.
        error (str, optional): The error message if the file operation failed. Defaults to None.
    """
    logger = get_logger('apilama.files')
    
    # Handle case where only operation is provided
    if filename is None:
        filename = 'all_files'
        logger.info(f"File {operation} (using default parameters)")
    elif success:
        logger.info(f"File {operation}: {filename}")
    else:
        logger.error(f"File {operation} failed: {filename} - {error}", extra={
            'context': {
                'operation': operation,
                'filename': filename,
                'error': error
            }
        })


# Export LogContext for backward compatibility
if LOGLAMA_AVAILABLE:
    from loglama.utils.context import LogContext
else:
    # Define a simple LogContext class for backward compatibility
    class LogContext:
        @staticmethod
        def set_context(**kwargs):
            pass
            
        def __init__(self, **kwargs):
            self.context = kwargs
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
