#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SheLLama Debug Routes

This module provides Flask routes for the debug window functionality.
"""

import os
import json
from flask import Blueprint, request, jsonify, current_app
from ..debug_window import (
    debug_window, 
    DebugLevel, 
    DebugCategory,
    get_debug_entries,
    clear_debug_entries,
    enable_debug_window,
    disable_debug_window,
    is_debug_enabled
)
from ..error_handler import ValidationError

# Create a blueprint for debug routes
debug_routes = Blueprint('debug_routes', __name__)

@debug_routes.route('/api/debug/status', methods=['GET'])
def debug_status():
    """Get the debug window status"""
    return jsonify({
        'status': 'success',
        'debug_enabled': is_debug_enabled(),
        'debug_mode': os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    })

@debug_routes.route('/api/debug/entries', methods=['GET'])
def get_entries():
    """Get debug entries with optional filtering"""
    # Get query parameters
    limit = request.args.get('limit', 100, type=int)
    level = request.args.get('level')
    category = request.args.get('category')
    source = request.args.get('source')
    
    # Get entries
    entries = get_debug_entries(
        limit=limit,
        level=level,
        category=category,
        source=source
    )
    
    return jsonify({
        'status': 'success',
        'entries': entries,
        'count': len(entries),
        'filters': {
            'limit': limit,
            'level': level,
            'category': category,
            'source': source
        }
    })

@debug_routes.route('/api/debug/clear', methods=['POST'])
def clear_entries():
    """Clear all debug entries"""
    clear_debug_entries()
    
    return jsonify({
        'status': 'success',
        'message': 'Debug entries cleared'
    })

@debug_routes.route('/api/debug/enable', methods=['POST'])
def enable_debug():
    """Enable the debug window"""
    enable_debug_window()
    
    return jsonify({
        'status': 'success',
        'message': 'Debug window enabled',
        'debug_enabled': True
    })

@debug_routes.route('/api/debug/disable', methods=['POST'])
def disable_debug():
    """Disable the debug window"""
    disable_debug_window()
    
    return jsonify({
        'status': 'success',
        'message': 'Debug window disabled',
        'debug_enabled': False
    })

@debug_routes.route('/api/debug/categories', methods=['GET'])
def get_categories():
    """Get all available debug categories"""
    categories = [category.value for category in DebugCategory]
    
    return jsonify({
        'status': 'success',
        'categories': categories
    })

@debug_routes.route('/api/debug/levels', methods=['GET'])
def get_levels():
    """Get all available debug levels"""
    levels = [level.value for level in DebugLevel]
    
    return jsonify({
        'status': 'success',
        'levels': levels
    })

@debug_routes.route('/api/debug/add', methods=['POST'])
def add_entry():
    """Add a debug entry"""
    # Get request data
    data = request.json
    
    if not data:
        raise ValidationError('No data provided')
    
    # Required fields
    if 'message' not in data:
        raise ValidationError('Message is required')
    
    message = data['message']
    
    # Optional fields with defaults
    level_str = data.get('level', 'info')
    category_str = data.get('category', 'system')
    details = data.get('details')
    source = data.get('source', 'api')
    
    # Convert level and category strings to enums
    try:
        level = DebugLevel(level_str)
    except ValueError:
        raise ValidationError(f"Invalid debug level: {level_str}")
    
    try:
        category = DebugCategory(category_str)
    except ValueError:
        raise ValidationError(f"Invalid debug category: {category_str}")
    
    # Add the entry
    debug_window.add_entry(
        message=message,
        level=level,
        category=category,
        details=details,
        source=source
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Debug entry added'
    })
