#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shell Command Execution Module

This module provides functions for executing shell commands and managing processes.
"""

import os
import subprocess
from typing import Dict, Any, List, Optional, Tuple, Union
import shlex
import signal
import time

from shellama.logger import logger


def execute_command(command: str, cwd: Optional[str] = None, timeout: Optional[int] = None, 
                   shell: bool = False, env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Execute a shell command and return the result.
    
    Args:
        command (str): The command to execute
        cwd (str, optional): The working directory to execute the command in. Defaults to None.
        timeout (int, optional): Timeout in seconds. Defaults to None.
        shell (bool, optional): Whether to use shell execution. Defaults to False.
        env (Dict[str, str], optional): Environment variables to set. Defaults to None.
        
    Returns:
        Dict[str, Any]: Dictionary with command execution results
        
    Raises:
        subprocess.TimeoutExpired: If the command times out
        subprocess.CalledProcessError: If the command returns a non-zero exit code
    """
    logger.info(f"Executing command: {command}")
    
    start_time = time.time()
    
    try:
        # Split the command into arguments if not using shell
        args = command if shell else shlex.split(command)
        
        # Execute the command
        process = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            cwd=cwd,
            timeout=timeout,
            shell=shell,
            env=env
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return {
            'success': True,
            'exit_code': process.returncode,
            'stdout': process.stdout,
            'stderr': process.stderr,
            'execution_time': execution_time
        }
    
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout} seconds: {command}")
        return {
            'success': False,
            'exit_code': None,
            'stdout': e.stdout if hasattr(e, 'stdout') and e.stdout else '',
            'stderr': e.stderr if hasattr(e, 'stderr') and e.stderr else '',
            'error': f"Command timed out after {timeout} seconds",
            'execution_time': time.time() - start_time
        }
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {command}")
        return {
            'success': False,
            'exit_code': e.returncode,
            'stdout': e.stdout,
            'stderr': e.stderr,
            'error': f"Command failed with exit code {e.returncode}",
            'execution_time': time.time() - start_time
        }
    
    except Exception as e:
        logger.error(f"Error executing command {command}: {str(e)}")
        return {
            'success': False,
            'exit_code': None,
            'stdout': '',
            'stderr': '',
            'error': str(e),
            'execution_time': time.time() - start_time
        }


class BackgroundProcess:
    """Class for managing background processes."""
    
    def __init__(self, command: str, cwd: Optional[str] = None, 
                shell: bool = False, env: Optional[Dict[str, str]] = None):
        """
        Initialize a background process.
        
        Args:
            command (str): The command to execute
            cwd (str, optional): The working directory to execute the command in. Defaults to None.
            shell (bool, optional): Whether to use shell execution. Defaults to False.
            env (Dict[str, str], optional): Environment variables to set. Defaults to None.
        """
        self.command = command
        self.cwd = cwd
        self.shell = shell
        self.env = env
        self.process = None
        self.start_time = None
        self.stdout = []
        self.stderr = []
    
    def start(self) -> bool:
        """
        Start the background process.
        
        Returns:
            bool: True if the process was started successfully, False otherwise
        """
        logger.info(f"Starting background process: {self.command}")
        
        try:
            # Split the command into arguments if not using shell
            args = self.command if self.shell else shlex.split(self.command)
            
            # Start the process
            self.process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd,
                shell=self.shell,
                env=self.env
            )
            
            self.start_time = time.time()
            return True
        
        except Exception as e:
            logger.error(f"Error starting background process {self.command}: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the background process.
        
        Returns:
            bool: True if the process was stopped successfully, False otherwise
        """
        if not self.process:
            logger.warning("No process to stop")
            return False
        
        logger.info(f"Stopping background process: {self.command}")
        
        try:
            self.process.terminate()
            
            # Wait for the process to terminate
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # If the process doesn't terminate within the timeout, kill it
                logger.warning(f"Process did not terminate, killing it: {self.command}")
                self.process.kill()
            
            return True
        
        except Exception as e:
            logger.error(f"Error stopping background process {self.command}: {str(e)}")
            return False
    
    def is_running(self) -> bool:
        """
        Check if the process is running.
        
        Returns:
            bool: True if the process is running, False otherwise
        """
        if not self.process:
            return False
        
        return self.process.poll() is None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the process.
        
        Returns:
            Dict[str, Any]: Dictionary with process status information
        """
        if not self.process:
            return {
                'running': False,
                'exit_code': None,
                'stdout': '',
                'stderr': '',
                'execution_time': 0
            }
        
        # Check if the process has terminated
        exit_code = self.process.poll()
        running = exit_code is None
        
        # Get the stdout and stderr output
        stdout = ''
        stderr = ''
        
        if self.process.stdout:
            stdout_data = self.process.stdout.read()
            if stdout_data:
                self.stdout.append(stdout_data)
        
        if self.process.stderr:
            stderr_data = self.process.stderr.read()
            if stderr_data:
                self.stderr.append(stderr_data)
        
        stdout = ''.join(self.stdout)
        stderr = ''.join(self.stderr)
        
        # Calculate execution time
        execution_time = time.time() - self.start_time if self.start_time else 0
        
        return {
            'running': running,
            'exit_code': exit_code,
            'stdout': stdout,
            'stderr': stderr,
            'execution_time': execution_time
        }
