#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SheLLama Debug Window Integration

This module provides a debug window integration for the SheLLama service.
It captures detailed debugging information and provides endpoints for viewing it.
"""

import os
import sys
import time
import json
import logging
import threading
import traceback
from typing import Dict, Any, List, Optional, Union
from collections import deque
from datetime import datetime
from enum import Enum

# Configure logger
logger = logging.getLogger('shellama.debug')

class DebugLevel(Enum):
    """Debug level enum"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DebugCategory(Enum):
    """Debug category enum"""
    SYSTEM = "system"
    FILE_OPERATIONS = "file_operations"
    GIT_OPERATIONS = "git_operations"
    SHELL_COMMANDS = "shell_commands"
    API = "api"
    NETWORK = "network"
    PERFORMANCE = "performance"
    SECURITY = "security"

class DebugEntry:
    """Class representing a debug entry"""
    def __init__(self, 
                 message: str, 
                 level: DebugLevel = DebugLevel.INFO, 
                 category: DebugCategory = DebugCategory.SYSTEM,
                 details: Optional[Dict[str, Any]] = None,
                 source: str = None,
                 exception: Exception = None):
        self.timestamp = datetime.now().isoformat()
        self.message = message
        self.level = level
        self.category = category
        self.details = details or {}
        self.source = source or "shellama"
        
        # Add exception details if provided
        if exception:
            self.details["exception"] = {
                "type": exception.__class__.__name__,
                "message": str(exception),
                "traceback": traceback.format_exception(type(exception), exception, exception.__traceback__)
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the debug entry to a dictionary"""
        return {
            "timestamp": self.timestamp,
            "message": self.message,
            "level": self.level.value,
            "category": self.category.value,
            "details": self.details,
            "source": self.source
        }

class DebugWindow:
    """Debug window class for capturing and managing debug entries"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure only one debug window instance"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DebugWindow, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the debug window"""
        if self._initialized:
            return
            
        self._entries = deque(maxlen=1000)  # Store up to 1000 entries
        self._listeners = []
        self._enabled = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
        self._initialized = True
        
        # Log initialization
        logger.info(f"Debug window initialized. Enabled: {self._enabled}")
        
        # Add initial system entry
        self.add_entry(
            message="Debug window initialized",
            level=DebugLevel.INFO,
            category=DebugCategory.SYSTEM,
            details={
                "enabled": self._enabled,
                "max_entries": self._entries.maxlen,
                "python_version": sys.version,
                "platform": sys.platform
            }
        )
    
    def add_entry(self, 
                  message: str, 
                  level: DebugLevel = DebugLevel.INFO, 
                  category: DebugCategory = DebugCategory.SYSTEM,
                  details: Optional[Dict[str, Any]] = None,
                  source: str = None,
                  exception: Exception = None) -> None:
        """Add a debug entry to the window"""
        if not self._enabled:
            return
            
        entry = DebugEntry(
            message=message,
            level=level,
            category=category,
            details=details,
            source=source,
            exception=exception
        )
        
        self._entries.append(entry)
        
        # Log the entry
        log_message = f"[{category.value}] {message}"
        if level == DebugLevel.DEBUG:
            logger.debug(log_message)
        elif level == DebugLevel.INFO:
            logger.info(log_message)
        elif level == DebugLevel.WARNING:
            logger.warning(log_message)
        elif level == DebugLevel.ERROR:
            logger.error(log_message)
        elif level == DebugLevel.CRITICAL:
            logger.critical(log_message)
        
        # Notify listeners
        for listener in self._listeners:
            try:
                listener(entry)
            except Exception as e:
                logger.error(f"Error notifying debug listener: {str(e)}")
    
    def get_entries(self, 
                    limit: int = 100, 
                    level: Optional[Union[DebugLevel, str]] = None,
                    category: Optional[Union[DebugCategory, str]] = None,
                    source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get debug entries with optional filtering"""
        if not self._enabled:
            return []
            
        # Convert string level/category to enum if needed
        if isinstance(level, str):
            try:
                level = DebugLevel(level)
            except ValueError:
                level = None
                
        if isinstance(category, str):
            try:
                category = DebugCategory(category)
            except ValueError:
                category = None
        
        # Filter entries
        filtered_entries = list(self._entries)
        
        if level:
            filtered_entries = [e for e in filtered_entries if e.level == level]
            
        if category:
            filtered_entries = [e for e in filtered_entries if e.category == category]
            
        if source:
            filtered_entries = [e for e in filtered_entries if e.source == source]
        
        # Limit entries and convert to dict
        return [entry.to_dict() for entry in filtered_entries[-limit:]]
    
    def clear_entries(self) -> None:
        """Clear all debug entries"""
        if not self._enabled:
            return
            
        self._entries.clear()
        
        # Log the clear operation
        logger.info("Debug entries cleared")
        
        # Add system entry for the clear operation
        self.add_entry(
            message="Debug entries cleared",
            level=DebugLevel.INFO,
            category=DebugCategory.SYSTEM
        )
    
    def add_listener(self, listener) -> None:
        """Add a listener function that will be called for each new entry"""
        if callable(listener) and listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener) -> None:
        """Remove a listener function"""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def enable(self) -> None:
        """Enable the debug window"""
        self._enabled = True
        logger.info("Debug window enabled")
        
        # Add system entry for enabling
        self.add_entry(
            message="Debug window enabled",
            level=DebugLevel.INFO,
            category=DebugCategory.SYSTEM
        )
    
    def disable(self) -> None:
        """Disable the debug window"""
        # Add system entry for disabling (before we actually disable)
        self.add_entry(
            message="Debug window disabled",
            level=DebugLevel.INFO,
            category=DebugCategory.SYSTEM
        )
        
        self._enabled = False
        logger.info("Debug window disabled")
    
    def is_enabled(self) -> bool:
        """Check if the debug window is enabled"""
        return self._enabled
    
    def to_json(self, limit: int = 100) -> str:
        """Convert debug entries to JSON string"""
        return json.dumps(self.get_entries(limit=limit))

# Create a global instance
debug_window = DebugWindow()

# Convenience functions
def add_debug_entry(message: str, level: DebugLevel = DebugLevel.DEBUG, category: DebugCategory = DebugCategory.SYSTEM, details: Optional[Dict[str, Any]] = None, source: str = None, exception: Exception = None) -> None:
    """Add a debug entry with DEBUG level"""
    debug_window.add_entry(message, level, category, details, source, exception)

def add_info_entry(message: str, category: DebugCategory = DebugCategory.SYSTEM, details: Optional[Dict[str, Any]] = None, source: str = None) -> None:
    """Add a debug entry with INFO level"""
    debug_window.add_entry(message, DebugLevel.INFO, category, details, source)

def add_warning_entry(message: str, category: DebugCategory = DebugCategory.SYSTEM, details: Optional[Dict[str, Any]] = None, source: str = None) -> None:
    """Add a debug entry with WARNING level"""
    debug_window.add_entry(message, DebugLevel.WARNING, category, details, source)

def add_error_entry(message: str, category: DebugCategory = DebugCategory.SYSTEM, details: Optional[Dict[str, Any]] = None, source: str = None, exception: Exception = None) -> None:
    """Add a debug entry with ERROR level"""
    debug_window.add_entry(message, DebugLevel.ERROR, category, details, source, exception)

def add_critical_entry(message: str, category: DebugCategory = DebugCategory.SYSTEM, details: Optional[Dict[str, Any]] = None, source: str = None, exception: Exception = None) -> None:
    """Add a debug entry with CRITICAL level"""
    debug_window.add_entry(message, DebugLevel.CRITICAL, category, details, source, exception)

def get_debug_entries(limit: int = 100, level: Optional[Union[DebugLevel, str]] = None, category: Optional[Union[DebugCategory, str]] = None, source: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get filtered debug entries"""
    return debug_window.get_entries(limit, level, category, source)

def clear_debug_entries() -> None:
    """Clear all debug entries"""
    debug_window.clear_entries()

def enable_debug_window() -> None:
    """Enable the debug window"""
    debug_window.enable()

def disable_debug_window() -> None:
    """Disable the debug window"""
    debug_window.disable()

def is_debug_enabled() -> bool:
    """Check if debug is enabled"""
    return debug_window.is_enabled()
