#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebLama Routes - API endpoints for WebLama frontend

This module provides the API endpoints that the WebLama frontend
will use to communicate with the backend services.
"""

import os
import logging
from flask import Blueprint, jsonify, request, current_app
from apilama.logger import log_file_operation, log_api_call

# Create Blueprint
weblama_routes = Blueprint('weblama', __name__)


@weblama_routes.route('/api/weblama/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for WebLama.
    
    Returns:
        JSON response with status information.
    """
    log_api_call('health_check', 'weblama')
    return jsonify({
        'status': 'success',
        'message': 'WebLama API is healthy',
        'service': 'weblama'
    })


@weblama_routes.route('/api/weblama/markdown', methods=['GET'])
def get_markdown_files():
    """
    Get a list of all markdown files.
    
    Returns:
        JSON response with the list of markdown files.
    """
    log_api_call('get_markdown_files', 'weblama')
    
    # This endpoint will now delegate to the SheLLama service
    # via the shellama_routes module
    from apilama.routes.shellama_routes import get_files
    return get_files()


@weblama_routes.route('/api/weblama/markdown/<path:filename>', methods=['GET'])
def get_markdown_content(filename):
    """
    Get the content of a markdown file.
    
    Args:
        filename: The name of the markdown file.
        
    Returns:
        JSON response with the content of the markdown file.
    """
    log_api_call('get_markdown_content', filename)
    
    # This endpoint will now delegate to the SheLLama service
    # via the shellama_routes module
    from apilama.routes.shellama_routes import get_file_content
    return get_file_content(filename)


@weblama_routes.route('/api/weblama/markdown/<path:filename>', methods=['POST'])
def save_markdown_content(filename):
    """
    Save the content of a markdown file.
    
    Args:
        filename: The name of the markdown file.
        
    Returns:
        JSON response with the status of the operation.
    """
    log_api_call('save_markdown_content', filename)
    
    # This endpoint will now delegate to the SheLLama service
    # via the shellama_routes module
    from apilama.routes.shellama_routes import create_file
    return create_file()


@weblama_routes.route('/api/weblama/markdown/<path:filename>', methods=['DELETE'])
def delete_markdown_file(filename):
    """
    Delete a markdown file.
    
    Args:
        filename: The name of the markdown file.
        
    Returns:
        JSON response with the status of the operation.
    """
    log_api_call('delete_markdown_file', filename)
    
    # This endpoint will now delegate to the SheLLama service
    # via the shellama_routes module
    from apilama.routes.shellama_routes import delete_file
    return delete_file()
