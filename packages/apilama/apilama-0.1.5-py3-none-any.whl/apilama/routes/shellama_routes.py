#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SheLLama API Routes

This module provides Flask routes for interacting with the SheLLama service.
It proxies requests to the SheLLama REST API service.
"""

import os
import requests
import json
from flask import Blueprint, request, jsonify, current_app
from apilama.logger import logger

# Create a blueprint for SheLLama routes
shellama_routes = Blueprint('shellama_routes', __name__)

# Get SheLLama service URL from environment variable or use default
SHELLAMA_API_URL = os.environ.get('SHELLAMA_API_URL', 'http://localhost:8002')

# Function to check if SheLLama service is available
def is_shellama_available():
    try:
        response = requests.get(f"{SHELLAMA_API_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error connecting to SheLLama service: {str(e)}")
        return False

# Check if SheLLama service is available
SHELLAMA_AVAILABLE = is_shellama_available()


@shellama_routes.route('/api/shellama/health', methods=['GET'])
def health_check():
    """Health check endpoint for SheLLama service.
    
    Returns:
        JSON response with the status of the SheLLama service
    """
    logger.info('SheLLama health check')
    
    try:
        # Forward the request to the SheLLama service
        response = requests.get(f"{SHELLAMA_API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            # Return the SheLLama service response
            shellama_response = response.json()
            return jsonify({
                'status': 'ok',
                'service': 'shellama',
                'available': True,
                'details': shellama_response
            })
        else:
            # Return error if SheLLama service returns non-200 status code
            return jsonify({
                'status': 'error',
                'service': 'shellama',
                'available': False,
                'message': f"SheLLama service returned status code {response.status_code}"
            }), 502
    except Exception as e:
        # Return error if SheLLama service is unavailable
        logger.error(f"Error connecting to SheLLama service: {str(e)}")
        return jsonify({
            'status': 'error',
            'service': 'shellama',
            'available': False,
            'message': f"Error connecting to SheLLama service: {str(e)}"
        }), 502


@shellama_routes.route('/api/shellama/files', methods=['GET'])
def get_files():
    """Get a list of files from the filesystem.
    
    Returns:
        JSON response with a list of files
    """
    # Check if SheLLama is available
    if not SHELLAMA_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'SheLLama service is not available'
        }), 503
    
    # Get the directory path and pattern from the query parameters
    directory = request.args.get('directory', '.')
    pattern = request.args.get('pattern', '*.*')
    
    logger.info(f'Listing files in directory: {directory} with pattern: {pattern}')
    
    try:
        # Forward the request to the SheLLama service
        response = requests.get(
            f"{SHELLAMA_API_URL}/files",
            params={'directory': directory, 'pattern': pattern},
            timeout=10
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the SheLLama service response
            return jsonify(response.json())
        else:
            # Return error if SheLLama service returns non-200 status code
            error_message = f"SheLLama service returned status code {response.status_code}"
            logger.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 502
    except Exception as e:
        logger.error(f'Error listing files: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shellama_routes.route('/api/shellama/file', methods=['GET'])
def get_file_content():
    """Get the content of a file.
    
    Returns:
        JSON response with the file content
    """
    # Check if SheLLama is available
    if not SHELLAMA_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'SheLLama service is not available'
        }), 503
    
    # Get the filename from the query parameters
    filename = request.args.get('filename')
    
    if not filename:
        logger.error('Invalid request: No filename provided')
        return jsonify({
            'status': 'error',
            'message': 'No filename provided'
        }), 400
    
    logger.info(f'Getting content of file: {filename}')
    
    try:
        # Forward the request to the SheLLama service
        response = requests.get(
            f"{SHELLAMA_API_URL}/file",
            params={'filename': filename},
            timeout=10
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the SheLLama service response with the filename added
            shellama_response = response.json()
            if 'name' not in shellama_response and shellama_response.get('status') == 'success':
                shellama_response['name'] = os.path.basename(filename)
            return jsonify(shellama_response)
        elif response.status_code == 404:
            # File not found
            logger.error(f'File not found: {filename}')
            return jsonify({
                'status': 'error',
                'message': f'File not found: {filename}'
            }), 404
        else:
            # Return error if SheLLama service returns other non-200 status code
            error_message = f"SheLLama service returned status code {response.status_code}"
            logger.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 502
    except Exception as e:
        logger.error(f'Error reading file {filename}: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shellama_routes.route('/api/shellama/file', methods=['POST'])
def create_file():
    """Create or update a file.
    
    Returns:
        JSON response with the result
    """
    # Check if SheLLama is available
    if not SHELLAMA_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'SheLLama service is not available'
        }), 503
    
    data = request.get_json()
    
    # Adapt to both API formats - support both 'path' and 'filename' fields for compatibility
    if not data:
        logger.error('Invalid request: No JSON data provided')
        return jsonify({
            'status': 'error',
            'message': 'No JSON data provided'
        }), 400
    
    # Handle both 'path' and 'filename' for backward compatibility
    filename = data.get('filename') or data.get('path')
    content = data.get('content')
    
    if not filename or content is None:
        logger.error('Invalid request: Missing required fields')
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields (filename/path, content)'
        }), 400
    
    logger.info(f'Creating/updating file: {filename}')
    
    try:
        # Forward the request to the SheLLama service
        response = requests.post(
            f"{SHELLAMA_API_URL}/file",
            json={
                'filename': filename,
                'content': content
            },
            timeout=10
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the SheLLama service response
            shellama_response = response.json()
            # Add path for backward compatibility if not present
            if 'path' not in shellama_response and shellama_response.get('status') == 'success':
                shellama_response['path'] = filename
            return jsonify(shellama_response)
        else:
            # Return error if SheLLama service returns non-200 status code
            error_message = f"SheLLama service returned status code {response.status_code}"
            logger.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 502
    except Exception as e:
        logger.error(f'Error writing file {filename}: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shellama_routes.route('/api/shellama/file', methods=['DELETE'])
def delete_file():
    """Delete a file.
    
    Returns:
        JSON response with the result
    """
    # Check if SheLLama is available
    if not SHELLAMA_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'SheLLama service is not available'
        }), 503
    
    # Get the filename from the query parameters
    filename = request.args.get('filename')
    
    if not filename:
        logger.error('Invalid request: No filename provided')
        return jsonify({
            'status': 'error',
            'message': 'No filename provided'
        }), 400
    
    logger.info(f'Deleting file: {filename}')
    
    try:
        # Forward the request to the SheLLama service
        response = requests.delete(
            f"{SHELLAMA_API_URL}/file",
            params={'filename': filename},
            timeout=10
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the SheLLama service response
            return jsonify(response.json())
        elif response.status_code == 404:
            # File not found
            logger.error(f'File not found: {filename}')
            return jsonify({
                'status': 'error',
                'message': f'File not found: {filename}'
            }), 404
        else:
            # Return error if SheLLama service returns other non-200 status code
            error_message = f"SheLLama service returned status code {response.status_code}"
            logger.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 502
    except Exception as e:
        logger.error(f'Error deleting file {filename}: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shellama_routes.route('/api/shellama/directory', methods=['GET'])
def get_directories():
    """Get a list of directories in a parent directory.
    
    Returns:
        JSON response with a list of directories
    """
    # Check if SheLLama is available
    if not SHELLAMA_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'SheLLama service is not available'
        }), 503
    
    # Get the directory path from the query parameters
    directory = request.args.get('directory', '.')
    
    logger.info(f'Listing directories in: {directory}')
    
    try:
        # Forward the request to the SheLLama service
        response = requests.get(
            f"{SHELLAMA_API_URL}/directories",
            params={'directory': directory},
            timeout=10
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the SheLLama service response
            return jsonify(response.json())
        elif response.status_code == 404:
            # Directory not found
            logger.error(f'Directory not found: {directory}')
            return jsonify({
                'status': 'error',
                'message': f'Directory not found: {directory}'
            }), 404
        else:
            # Return error if SheLLama service returns other non-200 status code
            error_message = f"SheLLama service returned status code {response.status_code}"
            logger.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 502
    except Exception as e:
        logger.error(f'Error listing directories in {directory}: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shellama_routes.route('/api/shellama/directory', methods=['POST'])
def create_directory():
    """Create a directory.
    
    Returns:
        JSON response with the result
    """
    # Check if SheLLama is available
    if not SHELLAMA_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'SheLLama service is not available'
        }), 503
    
    data = request.get_json()
    
    # Handle both 'path' and 'directory' for backward compatibility
    if not data:
        logger.error('Invalid request: No JSON data provided')
        return jsonify({
            'status': 'error',
            'message': 'No JSON data provided'
        }), 400
    
    # Get path from either 'path' or 'directory' field
    path = data.get('path') or data.get('directory')
    
    if not path:
        logger.error('Invalid request: Missing required fields')
        return jsonify({
            'status': 'error',
            'message': 'Missing required field (path or directory)'
        }), 400
    
    logger.info(f'Creating directory: {path}')
    
    try:
        # Forward the request to the SheLLama service
        response = requests.post(
            f"{SHELLAMA_API_URL}/directory",
            json={'directory': path},
            timeout=10
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the SheLLama service response
            shellama_response = response.json()
            # Add path for backward compatibility if not present
            if 'path' not in shellama_response and shellama_response.get('status') == 'success':
                shellama_response['path'] = path
            return jsonify(shellama_response)
        else:
            # Return error if SheLLama service returns non-200 status code
            error_message = f"SheLLama service returned status code {response.status_code}"
            logger.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 502
    except Exception as e:
        logger.error(f'Error creating directory {path}: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shellama_routes.route('/api/shellama/directory', methods=['DELETE'])
def delete_directory():
    """Delete a directory.
    
    Returns:
        JSON response with the result
    """
    # Check if SheLLama is available
    if not SHELLAMA_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'SheLLama service is not available'
        }), 503
    
    # Get the directory path and recursive flag from the query parameters
    directory = request.args.get('directory')
    recursive = request.args.get('recursive', 'false').lower() == 'true'
    
    if not directory:
        logger.error('Invalid request: No directory provided')
        return jsonify({
            'status': 'error',
            'message': 'No directory provided'
        }), 400
    
    logger.info(f'Deleting directory: {directory} (recursive={recursive})')
    
    try:
        # Forward the request to the SheLLama service
        response = requests.delete(
            f"{SHELLAMA_API_URL}/directory",
            params={
                'directory': directory,
                'recursive': str(recursive).lower()
            },
            timeout=10
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the SheLLama service response
            return jsonify(response.json())
        elif response.status_code == 404:
            # Directory not found
            logger.error(f'Directory not found: {directory}')
            return jsonify({
                'status': 'error',
                'message': f'Directory not found: {directory}'
            }), 404
        else:
            # Return error if SheLLama service returns other non-200 status code
            error_message = f"SheLLama service returned status code {response.status_code}"
            logger.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 502
    except Exception as e:
        logger.error(f'Error deleting directory {directory}: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shellama_routes.route('/api/shellama/shell', methods=['POST'])
def execute_shell_command():
    """Execute a shell command.
    
    Returns:
        JSON response with the command execution result
    """
    # Check if SheLLama is available
    if not SHELLAMA_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'SheLLama service is not available'
        }), 503
    
    data = request.get_json()
    
    if not data or 'command' not in data:
        logger.error('Invalid request: Missing required fields')
        return jsonify({
            'status': 'error',
            'message': 'Missing required field (command)'
        }), 400
    
    command = data['command']
    cwd = data.get('cwd')
    timeout = data.get('timeout')
    use_shell = data.get('shell', False)
    
    logger.info(f'Executing shell command: {command}')
    
    try:
        # Forward the request to the SheLLama service
        request_data = {
            'command': command,
            'shell': use_shell
        }
        
        # Add optional parameters if they exist
        if cwd is not None:
            request_data['cwd'] = cwd
        if timeout is not None:
            request_data['timeout'] = timeout
        
        response = requests.post(
            f"{SHELLAMA_API_URL}/shell",
            json=request_data,
            timeout=30  # Longer timeout for shell commands
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the SheLLama service response
            return jsonify(response.json())
        else:
            # Return error if SheLLama service returns non-200 status code
            error_message = f"SheLLama service returned status code {response.status_code}"
            logger.error(error_message)
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 502
    except Exception as e:
        logger.error(f'Error executing shell command {command}: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
