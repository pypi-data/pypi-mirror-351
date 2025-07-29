#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Directory Operations Module

This module provides functions for directory operations such as creating, listing, and navigating directories.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from shellama.logger import logger


def create_directory(directory_path: str) -> bool:
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path (str): Path to the directory to create
        
    Returns:
        bool: True if the directory was created or already exists, False otherwise
        
    Raises:
        IOError: If there is an error creating the directory
    """
    logger.info(f"Creating directory: {directory_path}")
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except IOError as e:
        logger.error(f"Error creating directory {directory_path}: {str(e)}")
        raise


def delete_directory(directory_path: str, recursive: bool = False) -> bool:
    """
    Delete a directory.
    
    Args:
        directory_path (str): Path to the directory to delete
        recursive (bool, optional): Whether to delete the directory recursively. Defaults to False.
        
    Returns:
        bool: True if the directory was deleted successfully, False otherwise
        
    Raises:
        FileNotFoundError: If the directory does not exist
        IOError: If there is an error deleting the directory
    """
    logger.info(f"Deleting directory: {directory_path} (recursive={recursive})")
    
    try:
        if recursive:
            shutil.rmtree(directory_path)
        else:
            os.rmdir(directory_path)
        return True
    except FileNotFoundError:
        logger.error(f"Directory not found: {directory_path}")
        raise
    except IOError as e:
        logger.error(f"Error deleting directory {directory_path}: {str(e)}")
        raise


def list_directories(parent_directory: str) -> List[Dict[str, Any]]:
    """
    List all directories in a parent directory.
    
    Args:
        parent_directory (str): Path to the parent directory
        
    Returns:
        List[Dict[str, Any]]: List of directory information dictionaries
        
    Raises:
        FileNotFoundError: If the parent directory does not exist
    """
    logger.info(f"Listing directories in: {parent_directory}")
    
    try:
        # Get all directories
        directories = []
        for item in Path(parent_directory).iterdir():
            if item.is_dir():
                # Get directory stats
                stats = item.stat()
                
                # Add directory info to the list
                directories.append({
                    'name': item.name,
                    'path': str(item),
                    'modified': stats.st_mtime,
                    'created': stats.st_ctime
                })
        
        # Sort directories by name
        directories.sort(key=lambda x: x['name'])
        
        return directories
    except FileNotFoundError:
        logger.error(f"Parent directory not found: {parent_directory}")
        raise


def directory_exists(directory_path: str) -> bool:
    """
    Check if a directory exists.
    
    Args:
        directory_path (str): Path to the directory to check
        
    Returns:
        bool: True if the directory exists, False otherwise
    """
    return os.path.isdir(directory_path)


def get_directory_size(directory_path: str) -> int:
    """
    Get the total size of a directory in bytes.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        int: Total size of the directory in bytes
        
    Raises:
        FileNotFoundError: If the directory does not exist
    """
    logger.info(f"Getting directory size: {directory_path}")
    
    # Check if the directory exists first
    if not os.path.isdir(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size
    except Exception as e:
        logger.error(f"Error getting directory size for {directory_path}: {str(e)}")
        raise


def copy_directory(source_path: str, destination_path: str) -> bool:
    """
    Copy a directory and its contents to a new location.
    
    Args:
        source_path (str): Path to the source directory
        destination_path (str): Path to the destination directory
        
    Returns:
        bool: True if the directory was copied successfully, False otherwise
        
    Raises:
        FileNotFoundError: If the source directory does not exist
        IOError: If there is an error copying the directory
    """
    logger.info(f"Copying directory from {source_path} to {destination_path}")
    
    try:
        shutil.copytree(source_path, destination_path)
        return True
    except FileNotFoundError:
        logger.error(f"Source directory not found: {source_path}")
        raise
    except IOError as e:
        logger.error(f"Error copying directory from {source_path} to {destination_path}: {str(e)}")
        raise
