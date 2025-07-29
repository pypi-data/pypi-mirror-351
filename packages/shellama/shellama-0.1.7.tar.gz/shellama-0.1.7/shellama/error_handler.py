#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SheLLama Error Handler Module

This module provides standardized error handling for the SheLLama service.
It includes custom exceptions, error response formatting, and logging integration.
"""

import os
import sys
import traceback
import logging
import json
from typing import Dict, Any, Optional, Union, List, Tuple
from enum import Enum

# Configure logger
logger = logging.getLogger('shellama.error_handler')

class ErrorSeverity(Enum):
    """Enum for error severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Enum for error categories"""
    VALIDATION = "validation_error"
    PERMISSION = "permission_error"
    FILE_SYSTEM = "file_system_error"
    GIT = "git_error"
    SHELL = "shell_error"
    NETWORK = "network_error"
    CONFIGURATION = "configuration_error"
    AUTHENTICATION = "authentication_error"
    AUTHORIZATION = "authorization_error"
    INTERNAL = "internal_error"
    EXTERNAL = "external_service_error"

class ShellamaError(Exception):
    """Base exception class for SheLLama service"""
    def __init__(self, 
                 message: str, 
                 category: ErrorCategory = ErrorCategory.INTERNAL, 
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 details: Optional[Dict[str, Any]] = None,
                 status_code: int = 500,
                 original_exception: Optional[Exception] = None):
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.status_code = status_code
        self.original_exception = original_exception
        
        # Add traceback information if in debug mode
        if os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't'):
            self.details['traceback'] = traceback.format_exc()
            
        # Log the error
        self._log_error()
        
        super().__init__(self.message)
    
    def _log_error(self) -> None:
        """Log the error with appropriate severity"""
        log_message = f"{self.category.value}: {self.message}"
        
        if self.original_exception:
            log_message += f" (Original exception: {str(self.original_exception)})"
        
        if self.severity == ErrorSeverity.DEBUG:
            logger.debug(log_message, exc_info=True)
        elif self.severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif self.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif self.severity == ErrorSeverity.ERROR:
            logger.error(log_message, exc_info=True)
        elif self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for JSON response"""
        error_dict = {
            "status": "error",
            "error": {
                "message": self.message,
                "category": self.category.value,
                "severity": self.severity.value,
                "code": self.status_code
            }
        }
        
        # Include details if they exist and we're in debug mode or they're safe to expose
        if self.details:
            # Filter out sensitive information like tracebacks in production
            safe_details = {k: v for k, v in self.details.items() 
                           if k != 'traceback' or os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')}
            if safe_details:
                error_dict["error"]["details"] = safe_details
        
        return error_dict
    
    def to_json(self) -> str:
        """Convert the error to a JSON string"""
        return json.dumps(self.to_dict())
    
    def to_response(self) -> Tuple[Dict[str, Any], int]:
        """Convert the error to a Flask response tuple"""
        return self.to_dict(), self.status_code

# Specific error classes
class ValidationError(ShellamaError):
    """Exception raised for validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            details=details,
            status_code=400,
            **kwargs
        )

class PermissionError(ShellamaError):
    """Exception raised for permission errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.ERROR,
            details=details,
            status_code=403,
            **kwargs
        )

class FileSystemError(ShellamaError):
    """Exception raised for file system errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.ERROR,
            details=details,
            status_code=500,
            **kwargs
        )

class FileNotFoundError(FileSystemError):
    """Exception raised when a file is not found"""
    def __init__(self, filename: str, **kwargs):
        super().__init__(
            message=f"File not found: {filename}",
            details={"filename": filename},
            status_code=404,
            **kwargs
        )

class GitError(ShellamaError):
    """Exception raised for Git operation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.GIT,
            severity=ErrorSeverity.ERROR,
            details=details,
            status_code=500,
            **kwargs
        )

class ShellError(ShellamaError):
    """Exception raised for shell command execution errors"""
    def __init__(self, 
                 message: str, 
                 command: str, 
                 exit_code: int, 
                 stdout: str = "", 
                 stderr: str = "", 
                 **kwargs):
        details = {
            "command": command,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr
        }
        super().__init__(
            message=message,
            category=ErrorCategory.SHELL,
            severity=ErrorSeverity.ERROR,
            details=details,
            status_code=500,
            **kwargs
        )

class ConfigurationError(ShellamaError):
    """Exception raised for configuration errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.ERROR,
            details=details,
            status_code=500,
            **kwargs
        )

class ExternalServiceError(ShellamaError):
    """Exception raised for errors in external services"""
    def __init__(self, 
                 message: str, 
                 service_name: str, 
                 details: Optional[Dict[str, Any]] = None, 
                 **kwargs):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL,
            severity=ErrorSeverity.ERROR,
            details=details,
            status_code=502,
            **kwargs
        )

# Error handler function for Flask
def handle_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Convert any exception to a standardized API response"""
    if isinstance(error, ShellamaError):
        return error.to_response()
    
    # Convert standard exceptions to ShellamaError
    if isinstance(error, ValueError):
        return ValidationError(str(error), original_exception=error).to_response()
    elif isinstance(error, PermissionError):
        return PermissionError(str(error), original_exception=error).to_response()
    elif isinstance(error, FileNotFoundError):
        return FileNotFoundError(str(error), original_exception=error).to_response()
    else:
        # Generic error handling
        return ShellamaError(
            message="An unexpected error occurred",
            severity=ErrorSeverity.ERROR,
            details={"error_type": error.__class__.__name__},
            original_exception=error
        ).to_response()
