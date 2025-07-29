#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SheLLama CLI

This module provides a command-line interface for SheLLama.
"""

import os
import sys
import argparse
from typing import List, Optional

from shellama import __version__
from shellama import file_ops
from shellama import dir_ops
from shellama import shell
from shellama.logger import logger


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args (List[str], optional): Command-line arguments. Defaults to None.
        
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='SheLLama - Shell and filesystem operations for the PyLama ecosystem')
    parser.add_argument('--version', action='version', version=f'SheLLama {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # File operations
    file_parser = subparsers.add_parser('file', help='File operations')
    file_subparsers = file_parser.add_subparsers(dest='file_command', help='File command to execute')
    
    # List files
    list_parser = file_subparsers.add_parser('list', help='List files in a directory')
    list_parser.add_argument('directory', help='Directory to list files from')
    list_parser.add_argument('--pattern', default='*.md', help='Glob pattern to match files')
    
    # Read file
    read_parser = file_subparsers.add_parser('read', help='Read a file')
    read_parser.add_argument('file', help='File to read')
    
    # Write file
    write_parser = file_subparsers.add_parser('write', help='Write to a file')
    write_parser.add_argument('file', help='File to write to')
    write_parser.add_argument('content', help='Content to write to the file')
    
    # Delete file
    delete_parser = file_subparsers.add_parser('delete', help='Delete a file')
    delete_parser.add_argument('file', help='File to delete')
    
    # Directory operations
    dir_parser = subparsers.add_parser('dir', help='Directory operations')
    dir_subparsers = dir_parser.add_subparsers(dest='dir_command', help='Directory command to execute')
    
    # Create directory
    create_parser = dir_subparsers.add_parser('create', help='Create a directory')
    create_parser.add_argument('directory', help='Directory to create')
    
    # Delete directory
    delete_dir_parser = dir_subparsers.add_parser('delete', help='Delete a directory')
    delete_dir_parser.add_argument('directory', help='Directory to delete')
    delete_dir_parser.add_argument('--recursive', action='store_true', help='Delete the directory recursively')
    
    # List directories
    list_dir_parser = dir_subparsers.add_parser('list', help='List directories in a parent directory')
    list_dir_parser.add_argument('directory', help='Parent directory to list directories from')
    
    # Shell command execution
    shell_parser = subparsers.add_parser('shell', help='Shell command execution')
    shell_parser.add_argument('command', help='Command to execute')
    shell_parser.add_argument('--cwd', help='Working directory to execute the command in')
    shell_parser.add_argument('--timeout', type=int, help='Timeout in seconds')
    shell_parser.add_argument('--shell', action='store_true', help='Use shell execution')
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args (List[str], optional): Command-line arguments. Defaults to None.
        
    Returns:
        int: Exit code
    """
    parsed_args = parse_args(args)
    
    if parsed_args.command is None:
        print("Error: No command specified. Use --help for usage information.")
        return 1
    
    try:
        # File operations
        if parsed_args.command == 'file':
            if parsed_args.file_command is None:
                print("Error: No file command specified. Use --help for usage information.")
                return 1
            
            # List files
            if parsed_args.file_command == 'list':
                files = file_ops.list_files(parsed_args.directory, parsed_args.pattern)
                for file in files:
                    print(f"{file['name']} - {file['size']} bytes")
            
            # Read file
            elif parsed_args.file_command == 'read':
                content = file_ops.read_file(parsed_args.file)
                print(content)
            
            # Write file
            elif parsed_args.file_command == 'write':
                success = file_ops.write_file(parsed_args.file, parsed_args.content)
                if success:
                    print(f"File {parsed_args.file} written successfully")
            
            # Delete file
            elif parsed_args.file_command == 'delete':
                success = file_ops.delete_file(parsed_args.file)
                if success:
                    print(f"File {parsed_args.file} deleted successfully")
        
        # Directory operations
        elif parsed_args.command == 'dir':
            if parsed_args.dir_command is None:
                print("Error: No directory command specified. Use --help for usage information.")
                return 1
            
            # Create directory
            if parsed_args.dir_command == 'create':
                success = dir_ops.create_directory(parsed_args.directory)
                if success:
                    print(f"Directory {parsed_args.directory} created successfully")
            
            # Delete directory
            elif parsed_args.dir_command == 'delete':
                success = dir_ops.delete_directory(parsed_args.directory, parsed_args.recursive)
                if success:
                    print(f"Directory {parsed_args.directory} deleted successfully")
            
            # List directories
            elif parsed_args.dir_command == 'list':
                directories = dir_ops.list_directories(parsed_args.directory)
                for directory in directories:
                    print(f"{directory['name']}")
        
        # Shell command execution
        elif parsed_args.command == 'shell':
            result = shell.execute_command(
                parsed_args.command,
                cwd=parsed_args.cwd,
                timeout=parsed_args.timeout,
                shell=parsed_args.shell
            )
            
            print(f"Exit code: {result['exit_code']}")
            print(f"Stdout:\n{result['stdout']}")
            
            if result['stderr']:
                print(f"Stderr:\n{result['stderr']}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
