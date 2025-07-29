#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APILama Logger

This module provides logging functionality for the APILama service.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import request, has_request_context

# Create a custom formatter that includes request information when available
class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = 'No URL'
            record.remote_addr = 'No IP'
            record.method = 'No Method'
        return super().format(record)

# Create a logger
logger = logging.getLogger('apilama')
logger.setLevel(logging.INFO)

# Create a formatter
formatter = RequestFormatter(
    '[%(asctime)s] [%(levelname)s] [%(remote_addr)s] [%(method)s] [%(url)s] - %(message)s'
)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'apilama.log'),
    maxBytes=10485760,  # 10 MB
    backupCount=10
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def init_app(app):
    """Initialize the logger for a Flask application.
    
    Args:
        app (Flask): The Flask application to initialize the logger for.
    """
    # Set the Flask app logger to use our logger
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    
    # Log when the app is initialized
    logger.info('APILama logger initialized')


def log_api_call(endpoint, success=True, error=None):
    """Log an API call.
    
    Args:
        endpoint (str): The API endpoint that was called.
        success (bool, optional): Whether the API call was successful. Defaults to True.
        error (str, optional): The error message if the API call failed. Defaults to None.
    """
    if success:
        logger.info(f'API call to {endpoint} successful')
    else:
        logger.error(f'API call to {endpoint} failed: {error}')


def log_file_operation(operation, filename=None, success=True, error=None):
    """Log a file operation.
    
    Args:
        operation (str): The file operation that was performed (e.g., 'read', 'write', 'list').
        filename (str, optional): The name of the file that was operated on. Defaults to None.
        success (bool, optional): Whether the file operation was successful. Defaults to True.
        error (str, optional): The error message if the file operation failed. Defaults to None.
    """
    # Handle case where only operation is provided
    if filename is None:
        filename = 'all_files'
        logger.info(f"File {operation} (using default parameters)")
    elif success:
        logger.info(f"File {operation}: {filename}")
    else:
        logger.error(f"File {operation} failed: {filename} - {error}")
