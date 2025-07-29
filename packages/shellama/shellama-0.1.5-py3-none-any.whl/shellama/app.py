#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SheLLama - REST API for shell and filesystem operations

This module provides a Flask web application that exposes the SheLLama
functionality as a REST API for use by the APILama gateway.
"""

import os
import sys
import argparse
from pathlib import Path

# Import PyLogs components first to ensure environment variables are loaded
from shellama.logging_config import init_logging, get_logger

# Initialize logging before any other imports
init_logging()

# Get a logger for this module
logger = get_logger('app')

from flask import Flask, jsonify, request
from flask_cors import CORS

# Import SheLLama modules
from shellama import file_ops, dir_ops, shell, git_ops
from shellama.logger import logger as shellama_logger


def init_app(app):
    """
    Initialize the Flask application with additional configurations.
    
    Args:
        app (Flask): The Flask application instance.
    """
    logger.info('Initializing SheLLama application')
    # Configure logging
    if not app.debug:
        # Add production-specific logging configuration if needed
        pass


def create_app(test_config=None):
    """
    Create and configure the Flask application.
    
    Args:
        test_config (dict, optional): Test configuration to override default config.
        
    Returns:
        Flask: The configured Flask application.
    """
    # Create and configure the app
    app = Flask(__name__)
    
    # Enable CORS for all routes and origins
    CORS(app)
    
    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DEBUG=os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't'),
    )
    
    # Override with test config if provided
    if test_config is not None:
        app.config.update(test_config)
    
    # Initialize the logger
    init_app(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'service': 'shellama'})
    
    # File operations endpoints
    @app.route('/files', methods=['GET'])
    def get_files():
        directory = request.args.get('directory', '.')
        pattern = request.args.get('pattern', '*')
        try:
            files = file_ops.list_files(directory, pattern)
            return jsonify({
                'status': 'success',
                'files': files
            })
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/file', methods=['GET'])
    def get_file():
        filename = request.args.get('filename')
        if not filename:
            return jsonify({
                'status': 'error',
                'message': 'Filename is required'
            }), 400
        
        try:
            content = file_ops.read_file(filename)
            return jsonify({
                'status': 'success',
                'content': content
            })
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/file', methods=['POST'])
    def save_file():
        data = request.get_json()
        filename = data.get('filename')
        content = data.get('content')
        
        if not filename or content is None:
            return jsonify({
                'status': 'error',
                'message': 'Filename and content are required'
            }), 400
        
        try:
            file_ops.write_file(filename, content)
            return jsonify({
                'status': 'success',
                'message': f'File {filename} saved successfully'
            })
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/file', methods=['DELETE'])
    def delete_file():
        filename = request.args.get('filename')
        if not filename:
            return jsonify({
                'status': 'error',
                'message': 'Filename is required'
            }), 400
        
        try:
            file_ops.delete_file(filename)
            return jsonify({
                'status': 'success',
                'message': f'File {filename} deleted successfully'
            })
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # Directory operations endpoints
    @app.route('/directory', methods=['GET'])
    def get_directory():
        path = request.args.get('path', '.')
        try:
            directory_info = dir_ops.get_directory_info(path)
            return jsonify({
                'status': 'success',
                'directory': directory_info
            })
        except Exception as e:
            logger.error(f"Error getting directory info: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/directory', methods=['POST'])
    def create_directory():
        data = request.get_json()
        path = data.get('path')
        
        if not path:
            return jsonify({
                'status': 'error',
                'message': 'Path is required'
            }), 400
        
        try:
            dir_ops.create_directory(path)
            return jsonify({
                'status': 'success',
                'message': f'Directory {path} created successfully'
            })
        except Exception as e:
            logger.error(f"Error creating directory: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/directory', methods=['DELETE'])
    def delete_directory():
        path = request.args.get('path')
        if not path:
            return jsonify({
                'status': 'error',
                'message': 'Path is required'
            }), 400
        
        try:
            dir_ops.delete_directory(path)
            return jsonify({
                'status': 'success',
                'message': f'Directory {path} deleted successfully'
            })
        except Exception as e:
            logger.error(f"Error deleting directory: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # Shell command endpoint
    @app.route('/shell', methods=['POST'])
    def execute_shell_command():
        data = request.get_json()
        command = data.get('command')
        cwd = data.get('cwd')
        
        if not command:
            return jsonify({
                'status': 'error',
                'message': 'Command is required'
            }), 400
        
        try:
            result = shell.execute_command(command, cwd=cwd)
            return jsonify({
                'status': 'success',
                'output': result.stdout,
                'error': result.stderr,
                'exit_code': result.returncode
            })
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # Git operations endpoints
    @app.route('/git/status', methods=['GET'])
    def git_status():
        repo_path = request.args.get('path', '.')
        try:
            status = git_ops.get_status(repo_path)
            return jsonify({
                'status': 'success',
                'git_status': status
            })
        except Exception as e:
            logger.error(f"Error getting git status: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/git/init', methods=['POST'])
    def git_init():
        data = request.get_json()
        repo_path = data.get('path', '.')
        
        try:
            result = git_ops.init_repo(repo_path)
            return jsonify({
                'status': 'success',
                'message': result
            })
        except Exception as e:
            logger.error(f"Error initializing git repo: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/git/commit', methods=['POST'])
    def git_commit():
        data = request.get_json()
        repo_path = data.get('path', '.')
        message = data.get('message', 'Update files')
        
        try:
            result = git_ops.commit_changes(repo_path, message)
            return jsonify({
                'status': 'success',
                'message': result
            })
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/git/log', methods=['GET'])
    def git_log():
        repo_path = request.args.get('path', '.')
        try:
            logs = git_ops.get_log(repo_path)
            return jsonify({
                'status': 'success',
                'logs': logs
            })
        except Exception as e:
            logger.error(f"Error getting git log: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    # Log the initialization
    logger.info(f"SheLLama API initialized")
    
    return app


def main():
    """
    Run the Flask application.
    
    This function is the entry point for the application when run directly.
    Supports both environment variables and command-line arguments.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SheLLama API Server')
    parser.add_argument('--port', type=int, help='Port to run the server on')
    parser.add_argument('--host', type=str, help='Host to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    # Get configuration from environment variables or command line arguments
    port = args.port or int(os.environ.get('PORT', 8002))
    host = args.host or os.environ.get('HOST', '127.0.0.1')
    debug = args.debug or os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    
    # Create and run the app
    app = create_app()
    
    # Print startup message
    print(f"Starting SheLLama API server on {host}:{port} (debug={debug})")
    
    # Run the app
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
