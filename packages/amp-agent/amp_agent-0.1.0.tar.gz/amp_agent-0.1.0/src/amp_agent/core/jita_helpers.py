"""
Jita helpers for AMP agents.
This module provides utilities for working with Jita components.
"""
import json
from typing import Dict, Any, List, Optional


def build_jita_map(map_data: Dict[str, Any]) -> str:
    """
    Build a Jita map component in the correct markdown format.
    
    Args:
        map_data: Dictionary containing map data (center, markers, etc.)
        
    Returns:
        Markdown code block for the map JITA component
    """
    # Extract the essential data for the map component
    map_component = {
        "center": map_data.get("center", {"lat": 0, "lng": 0}),
        "zoom": map_data.get("zoom", 12),
        "markers": map_data.get("markers", [])
    }
    
    return f'```map:{json.dumps(map_component, separators=(",", ":"))}```'


def build_jita_calendar(params: Dict[str, Any]) -> str:
    """
    Build a Jita calendar component in the correct markdown format.
    
    Args:
        params: Dictionary containing calendar parameters (mode, title, dates, etc.)
        
    Returns:
        Markdown code block for the calendar JITA component
    """
    # Build the calendar component data
    calendar_data = {
        "mode": params.get("mode", "single"),
        "title": params.get("title", "Select Date"),
    }
    
    # Add optional parameters if they exist
    if "description" in params:
        calendar_data["description"] = params["description"]
    if "minDate" in params:
        calendar_data["minDate"] = params["minDate"]
    if "maxDate" in params:
        calendar_data["maxDate"] = params["maxDate"]
    if "defaultDate" in params:
        calendar_data["defaultDate"] = params["defaultDate"]
    if "defaultRange" in params:
        calendar_data["defaultRange"] = params["defaultRange"]
    if "unavailableDates" in params:
        calendar_data["unavailableDates"] = params["unavailableDates"]
    
    return f'```calendar:{json.dumps(calendar_data, separators=(",", ":"))}```'


def build_jita_selector(params: Dict[str, Any]) -> str:
    """
    Build a Jita selector component.
    
    Args:
        params: Dictionary of selector parameters including type, options, title, description
        
    Returns:
        Markdown code block for the selector JITA component
    """
    return f'```selector:{json.dumps(params, separators=(",", ":"))}```'


def format_jita_response(message: str, component: str) -> str:
    """
    Format a response with a Jita component.
    
    Args:
        message: The response message
        component: The Jita component JSON string
        
    Returns:
        Formatted response with embedded component
    """
    return f"{message}\n\n```jita\n{component}\n```" 