#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Operations Module

This module provides functions for file operations such as reading, writing, and listing files.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from shellama.logger import logger


def list_files(directory: str, pattern: str = "*.md") -> List[Dict[str, Any]]:
    """
    List files in a directory matching a pattern.
    
    Args:
        directory (str): Directory path to list files from
        pattern (str, optional): Glob pattern to match files. Defaults to "*.md".
        
    Returns:
        List[Dict[str, Any]]: List of file information dictionaries
    """
    logger.info(f"Listing files in {directory} with pattern {pattern}")
    
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Get all files matching the pattern
    files = []
    for file_path in Path(directory).glob(pattern):
        # Get file stats
        stats = file_path.stat()
        
        # Add file info to the list
        files.append({
            'name': file_path.name,
            'path': str(file_path),
            'size': stats.st_size,
            'modified': stats.st_mtime
        })
    
    # Sort files by modification time (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)
    
    return files


def read_file(file_path: str) -> str:
    """
    Read the content of a file.
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        str: Content of the file
        
    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there is an error reading the file
    """
    logger.info(f"Reading file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise


def write_file(file_path: str, content: str) -> bool:
    """
    Write content to a file.
    
    Args:
        file_path (str): Path to the file to write
        content (str): Content to write to the file
        
    Returns:
        bool: True if the file was written successfully, False otherwise
        
    Raises:
        IOError: If there is an error writing the file
    """
    logger.info(f"Writing to file: {file_path}")
    
    # Create the directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {str(e)}")
        raise


def delete_file(file_path: str) -> bool:
    """
    Delete a file.
    
    Args:
        file_path (str): Path to the file to delete
        
    Returns:
        bool: True if the file was deleted successfully, False otherwise
        
    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there is an error deleting the file
    """
    logger.info(f"Deleting file: {file_path}")
    
    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        raise


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if the file exists, False otherwise
    """
    return os.path.isfile(file_path)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Args:
        file_path (str): Path to the file to get information about
        
    Returns:
        Dict[str, Any]: Dictionary with file information
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    logger.info(f"Getting file info: {file_path}")
    
    try:
        path = Path(file_path)
        stats = path.stat()
        
        return {
            'name': path.name,
            'path': str(path),
            'size': stats.st_size,
            'modified': stats.st_mtime,
            'created': stats.st_ctime,
            'extension': path.suffix,
            'is_file': path.is_file(),
            'is_dir': path.is_dir()
        }
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
