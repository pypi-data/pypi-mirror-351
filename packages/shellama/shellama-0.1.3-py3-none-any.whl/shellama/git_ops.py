#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git Operations Module

This module provides functions for Git version control operations.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import git
from git import Repo

from shellama.logger import logger


def init_repo(directory_path: str) -> bool:
    """
    Initialize a Git repository in the specified directory.
    
    Args:
        directory_path (str): Path to the directory to initialize as a Git repository
        
    Returns:
        bool: True if the repository was initialized successfully, False otherwise
        
    Raises:
        git.GitCommandError: If there is an error initializing the repository
    """
    logger.info(f"Initializing Git repository in: {directory_path}")
    
    try:
        # Create the directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=True)
        
        # Initialize the repository
        Repo.init(directory_path)
        return True
    except git.GitCommandError as e:
        logger.error(f"Error initializing Git repository in {directory_path}: {str(e)}")
        raise


def clone_repo(repo_url: str, target_directory: str, branch: Optional[str] = None) -> bool:
    """
    Clone a Git repository to the specified directory.
    
    Args:
        repo_url (str): URL of the repository to clone
        target_directory (str): Path to the directory to clone the repository to
        branch (str, optional): Branch to checkout after cloning. Defaults to None.
        
    Returns:
        bool: True if the repository was cloned successfully, False otherwise
        
    Raises:
        git.GitCommandError: If there is an error cloning the repository
    """
    logger.info(f"Cloning Git repository from {repo_url} to {target_directory}")
    
    try:
        # Clone the repository
        repo = Repo.clone_from(repo_url, target_directory)
        
        # Checkout the specified branch if provided
        if branch:
            repo.git.checkout(branch)
        
        return True
    except git.GitCommandError as e:
        logger.error(f"Error cloning Git repository from {repo_url} to {target_directory}: {str(e)}")
        raise


def get_repo(directory_path: str) -> Repo:
    """
    Get a Git repository object for the specified directory.
    
    Args:
        directory_path (str): Path to the Git repository
        
    Returns:
        Repo: Git repository object
        
    Raises:
        git.InvalidGitRepositoryError: If the directory is not a Git repository
    """
    try:
        return Repo(directory_path)
    except git.InvalidGitRepositoryError:
        logger.error(f"Directory {directory_path} is not a Git repository")
        raise


def add_files(repo_path: str, files: List[str] = None) -> bool:
    """
    Add files to the Git index.
    
    Args:
        repo_path (str): Path to the Git repository
        files (List[str], optional): List of files to add. Defaults to None (add all files).
        
    Returns:
        bool: True if the files were added successfully, False otherwise
        
    Raises:
        git.GitCommandError: If there is an error adding the files
    """
    logger.info(f"Adding files to Git index in {repo_path}: {files if files else 'all'}")
    
    try:
        repo = get_repo(repo_path)
        
        if files:
            for file in files:
                repo.git.add(file)
        else:
            repo.git.add(A=True)
        
        return True
    except git.GitCommandError as e:
        logger.error(f"Error adding files to Git index in {repo_path}: {str(e)}")
        raise


def commit(repo_path: str, message: str, author_name: Optional[str] = None, author_email: Optional[str] = None) -> bool:
    """
    Commit changes to the Git repository.
    
    Args:
        repo_path (str): Path to the Git repository
        message (str): Commit message
        author_name (str, optional): Author name for the commit. Defaults to None.
        author_email (str, optional): Author email for the commit. Defaults to None.
        
    Returns:
        bool: True if the changes were committed successfully, False otherwise
        
    Raises:
        git.GitCommandError: If there is an error committing the changes
    """
    logger.info(f"Committing changes to Git repository in {repo_path} with message: {message}")
    
    try:
        repo = get_repo(repo_path)
        
        # Set the author if provided
        if author_name and author_email:
            repo.git.config('user.name', author_name)
            repo.git.config('user.email', author_email)
        
        # Commit the changes
        repo.git.commit(m=message)
        
        return True
    except git.GitCommandError as e:
        logger.error(f"Error committing changes to Git repository in {repo_path}: {str(e)}")
        raise


def push(repo_path: str, remote: str = 'origin', branch: str = 'main') -> bool:
    """
    Push changes to a remote repository.
    
    Args:
        repo_path (str): Path to the Git repository
        remote (str, optional): Remote name. Defaults to 'origin'.
        branch (str, optional): Branch name. Defaults to 'main'.
        
    Returns:
        bool: True if the changes were pushed successfully, False otherwise
        
    Raises:
        git.GitCommandError: If there is an error pushing the changes
    """
    logger.info(f"Pushing changes to remote {remote}/{branch} from Git repository in {repo_path}")
    
    try:
        repo = get_repo(repo_path)
        repo.git.push(remote, branch)
        return True
    except git.GitCommandError as e:
        logger.error(f"Error pushing changes to remote {remote}/{branch} from Git repository in {repo_path}: {str(e)}")
        raise


def pull(repo_path: str, remote: str = 'origin', branch: str = 'main') -> bool:
    """
    Pull changes from a remote repository.
    
    Args:
        repo_path (str): Path to the Git repository
        remote (str, optional): Remote name. Defaults to 'origin'.
        branch (str, optional): Branch name. Defaults to 'main'.
        
    Returns:
        bool: True if the changes were pulled successfully, False otherwise
        
    Raises:
        git.GitCommandError: If there is an error pulling the changes
    """
    logger.info(f"Pulling changes from remote {remote}/{branch} to Git repository in {repo_path}")
    
    try:
        repo = get_repo(repo_path)
        repo.git.pull(remote, branch)
        return True
    except git.GitCommandError as e:
        logger.error(f"Error pulling changes from remote {remote}/{branch} to Git repository in {repo_path}: {str(e)}")
        raise


def get_status(repo_path: str) -> Dict[str, List[str]]:
    """
    Get the status of the Git repository.
    
    Args:
        repo_path (str): Path to the Git repository
        
    Returns:
        Dict[str, List[str]]: Dictionary with repository status information
        
    Raises:
        git.GitCommandError: If there is an error getting the repository status
    """
    logger.info(f"Getting status of Git repository in {repo_path}")
    
    try:
        repo = get_repo(repo_path)
        
        # Get the repository status
        status = {
            'modified': [],
            'added': [],
            'deleted': [],
            'untracked': []
        }
        
        # Get the repository status
        for item in repo.index.diff(None):
            if item.change_type == 'M':
                status['modified'].append(item.a_path)
            elif item.change_type == 'A':
                status['added'].append(item.a_path)
            elif item.change_type == 'D':
                status['deleted'].append(item.a_path)
        
        # Get untracked files
        status['untracked'] = repo.untracked_files
        
        return status
    except git.GitCommandError as e:
        logger.error(f"Error getting status of Git repository in {repo_path}: {str(e)}")
        raise


def get_commit_history(repo_path: str, max_count: int = 10) -> List[Dict[str, Any]]:
    """
    Get the commit history of the Git repository.
    
    Args:
        repo_path (str): Path to the Git repository
        max_count (int, optional): Maximum number of commits to retrieve. Defaults to 10.
        
    Returns:
        List[Dict[str, Any]]: List of commit information dictionaries
        
    Raises:
        git.GitCommandError: If there is an error getting the commit history
    """
    logger.info(f"Getting commit history of Git repository in {repo_path} (max_count={max_count})")
    
    try:
        repo = get_repo(repo_path)
        
        # Get the commit history
        commits = []
        for commit in repo.iter_commits(max_count=max_count):
            commits.append({
                'hash': commit.hexsha,
                'author': commit.author.name,
                'email': commit.author.email,
                'date': commit.committed_datetime,
                'message': commit.message.strip()
            })
        
        return commits
    except git.GitCommandError as e:
        logger.error(f"Error getting commit history of Git repository in {repo_path}: {str(e)}")
        raise
