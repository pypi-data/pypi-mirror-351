#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APILama - Main application module

This module provides the Flask application for the APILama service.
"""

# Initialize logging FIRST, before any other imports
# This ensures environment variables are loaded before other libraries
from apilama.logging_config import init_logging, get_logger

# Initialize logging with LogLama
init_logging()

# Now import other standard libraries
import os
import sys
import argparse
from pathlib import Path

# Flask imports
from flask import Flask, jsonify, request
from flask_cors import CORS

# Get the logger
logger = get_logger('apilama')

# Add the parent directory to sys.path to import devlama modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import blueprints
from apilama.routes.devlama_routes import devlama_routes
from apilama.routes.bexy_routes import bexy_routes
from apilama.routes.getllm_routes import getllm_routes
from apilama.routes.shellama_routes import shellama_routes
from apilama.routes.file_routes import file_routes
from apilama.routes.git_routes import git_routes
from apilama.routes.weblama_routes import weblama_routes


def create_app(test_config=None):
    """Create and configure the Flask application.
    
    Args:
        test_config (dict, optional): Test configuration to override default config.
        
    Returns:
        Flask: The configured Flask application.
    """
    # Create and configure the app
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DEBUG=os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't'),
    )
    
    # Override with test config if provided
    if test_config is not None:
        app.config.update(test_config)
    
    # Add request logging middleware
    @app.before_request
    def log_request_info():
        logger.debug(f"Request: {request.method} {request.url} from {request.remote_addr}")
        
    @app.after_request
    def log_response_info(response):
        logger.debug(f"Response: {response.status_code}")
        return response
    
    # Register blueprints
    app.register_blueprint(devlama_routes)
    app.register_blueprint(bexy_routes)
    app.register_blueprint(getllm_routes)
    app.register_blueprint(shellama_routes)
    app.register_blueprint(file_routes)
    app.register_blueprint(git_routes)
    app.register_blueprint(weblama_routes)
    
    # Add a health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok', 'service': 'apilama'})
    
    # Log the initialization with structured context
    logger.info("APILama initialized", extra={
        'context': {
            'cors_enabled': True,
            'debug_mode': app.config['DEBUG'],
            'blueprints': [
                'devlama_routes',
                'bexy_routes',
                'getllm_routes',
                'shellama_routes',
                'file_routes',
                'git_routes',
                'weblama_routes'
            ]
        }
    })
    
    return app


def main():
    """Run the Flask application.
    
    This function is the entry point for the application when run directly.
    Supports both environment variables and command-line arguments.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='APILama - Backend API service for the PyLama ecosystem')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8000)),
                        help='Port to run the server on (default: 8000)')
    parser.add_argument('--host', type=str, default=os.environ.get('HOST', '127.0.0.1'),
                        help='Host to run the server on (default: 127.0.0.1)')
    parser.add_argument('--debug', action='store_true', default=None,
                        help='Run in debug mode')
    args = parser.parse_args()
    
    # Set environment variables from arguments
    if args.debug is not None:
        os.environ['DEBUG'] = str(args.debug)
    
    # Create the app
    app = create_app()
    
    # Print startup message
    print(f"Starting APILama on {args.host}:{args.port} (debug={app.config['DEBUG']})")
    
    # Run the app
    app.run(host=args.host, port=args.port, debug=app.config['DEBUG'])


if __name__ == '__main__':
    main()
