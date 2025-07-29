from flask import Blueprint, jsonify, request, current_app
import os
import glob
from pathlib import Path

# Import LogLama utilities
from apilama.logging_config import get_logger, log_file_operation, log_request_context, LogContext

file_routes = Blueprint('file_routes', __name__)

# Get a logger for file operations
logger = get_logger('apilama.files')


def get_markdown_dir():
    """Get the markdown directory from environment or use default, with proper path expansion."""
    markdown_dir = os.environ.get('MARKDOWN_DIR', '~/github/py-lama/weblama/markdown')
    # Expand the tilde to the home directory
    markdown_dir = os.path.expanduser(markdown_dir)
    logger.info(f"Using markdown directory: {markdown_dir}", extra={
        'context': {'markdown_dir': markdown_dir}
    })
    return markdown_dir


@file_routes.route('/api/files', methods=['GET'])
@log_request_context
def get_files():
    """List all markdown files in the markdown directory."""
    try:
        with LogContext(operation='list_files'):
            markdown_dir = get_markdown_dir()
            
            if not os.path.exists(markdown_dir):
                logger.info(f"Creating markdown directory: {markdown_dir}")
                os.makedirs(markdown_dir, exist_ok=True)
                
            # Get all markdown files
            markdown_files = []
            for file_path in glob.glob(os.path.join(markdown_dir, '*.md')):
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                last_modified = os.path.getmtime(file_path)
                markdown_files.append({
                    'name': file_name,
                    'path': file_path,
                    'size': file_size,
                    'last_modified': last_modified
                })
            
            # Log the operation
            log_file_operation('list', 'all_markdown_files', True)
            logger.info(f"Listed {len(markdown_files)} markdown files", extra={
                'context': {'file_count': len(markdown_files)}
            })
            
            return jsonify({
                'status': 'success',
                'files': markdown_files
            })
    except Exception as e:
        log_file_operation('list', 'all_markdown_files', False, str(e))
        logger.error(f"Error listing files: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@file_routes.route('/api/file', methods=['GET'])
@log_request_context
def get_file():
    """Get the content of a markdown file."""
    try:
        filename = request.args.get('filename')
        if not filename:
            logger.warning("Get file request missing filename parameter")
            return jsonify({
                'status': 'error',
                'message': 'Filename is required'
            }), 400
        
        with LogContext(operation='read_file', filename=filename):
            markdown_dir = get_markdown_dir()
            file_path = os.path.join(markdown_dir, filename)
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {filename}", extra={
                    'context': {'file_path': file_path}
                })
                return jsonify({
                    'status': 'error',
                    'message': f'File {filename} not found'
                }), 404
                
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Log the operation
            log_file_operation('read', filename, True)
            file_size = os.path.getsize(file_path)
            logger.info(f"Read file {filename}", extra={
                'context': {'file_size': file_size, 'file_path': file_path}
            })
            
            return jsonify({
                'status': 'success',
                'content': content
            })
    except Exception as e:
        log_file_operation('read', filename, False, str(e))
        logger.error(f"Error reading file: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@file_routes.route('/api/file', methods=['POST'])
@log_request_context
def save_file():
    """Save content to a markdown file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        content = data.get('content')
        
        if not filename or content is None:
            logger.warning("Save file request missing required parameters")
            return jsonify({
                'status': 'error',
                'message': 'Filename and content are required'
            }), 400
        
        with LogContext(operation='write_file', filename=filename):
            markdown_dir = get_markdown_dir()
            if not os.path.exists(markdown_dir):
                logger.info(f"Creating markdown directory: {markdown_dir}")
                os.makedirs(markdown_dir, exist_ok=True)
                
            file_path = os.path.join(markdown_dir, filename)
            is_new = not os.path.exists(file_path)
            
            with open(file_path, 'w') as f:
                f.write(content)
                
            # Log the operation
            operation = 'create' if is_new else 'update'
            log_file_operation(operation, filename, True)
            content_size = len(content)
            logger.info(f"{operation.capitalize()}d file {filename}", extra={
                'context': {
                    'file_path': file_path,
                    'content_size': content_size,
                    'is_new_file': is_new
                }
            })
            
            return jsonify({
                'status': 'success',
                'message': f'File {filename} saved successfully'
            })
    except Exception as e:
        log_file_operation('write', filename, False, str(e))
        logger.error(f"Error saving file: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@file_routes.route('/api/file', methods=['DELETE'])
@log_request_context
def delete_file():
    """Delete a markdown file."""
    try:
        filename = request.args.get('filename')
        if not filename:
            logger.warning("Delete file request missing filename parameter")
            return jsonify({
                'status': 'error',
                'message': 'Filename is required'
            }), 400
        
        with LogContext(operation='delete_file', filename=filename):
            markdown_dir = get_markdown_dir()
            file_path = os.path.join(markdown_dir, filename)
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found for deletion: {filename}", extra={
                    'context': {'file_path': file_path}
                })
                return jsonify({
                    'status': 'error',
                    'message': f'File {filename} not found'
                }), 404
            
            # Get file info before deletion for logging
            file_size = os.path.getsize(file_path)
            file_mtime = os.path.getmtime(file_path)
            
            os.remove(file_path)
            
            # Log the operation
            log_file_operation('delete', filename, True)
            logger.info(f"Deleted file {filename}", extra={
                'context': {
                    'file_path': file_path,
                    'file_size': file_size,
                    'last_modified': file_mtime
                }
            })
            
            return jsonify({
                'status': 'success',
                'message': f'File {filename} deleted successfully'
            })
    except Exception as e:
        log_file_operation('delete', filename, False, str(e))
        logger.error(f"Error deleting file: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
