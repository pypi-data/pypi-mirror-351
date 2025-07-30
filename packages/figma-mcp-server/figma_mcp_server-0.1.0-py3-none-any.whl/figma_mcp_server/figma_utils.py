"""
Utility functions for working with Figma data.
"""
from typing import Dict, Optional, Union, Tuple


def is_visible(node_data: Dict) -> bool:
    """
    Determine if a node is visible.
    
    Args:
        node_data: Raw node data from Figma API
        
    Returns:
        True if the node is visible, False otherwise
    """
    return node_data.get("visible", True) is not False


def format_rgba_color(color: Dict, opacity: Optional[float] = None) -> str:
    """
    Format an RGBA color as a CSS rgba() string.
    
    Args:
        color: Color object with r, g, b values (0-1 scale)
        opacity: Optional opacity override (0-1 scale)
        
    Returns:
        CSS rgba() string
    """
    r = int(color.get("r", 0) * 255)
    g = int(color.get("g", 0) * 255)
    b = int(color.get("b", 0) * 255)
    a = opacity if opacity is not None else color.get("a", 1)
    
    return f"rgba({r}, {g}, {b}, {a})"


def convert_figma_color_to_hex_opacity(
    color: Dict, 
    opacity: Optional[float] = None
) -> Tuple[str, float]:
    """
    Convert a Figma color to a hex string and opacity value.
    
    Args:
        color: Color object with r, g, b values (0-1 scale)
        opacity: Optional opacity override (0-1 scale)
        
    Returns:
        Tuple of (hex color string, opacity)
    """
    r = int(color.get("r", 0) * 255)
    g = int(color.get("g", 0) * 255)
    b = int(color.get("b", 0) * 255)
    a = opacity if opacity is not None else color.get("a", 1)
    
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    return hex_color, a


def generate_var_id(prefix: str, unique_part: str) -> str:
    """
    Generate a variable ID for de-duplicated styles.
    
    Args:
        prefix: Type of variable (fill, stroke, etc.)
        unique_part: Unique identifier (can be a hash, counter, etc.)
        
    Returns:
        Style variable ID in the format "prefix_unique_part"
    """
    return f"{prefix}_{unique_part}"


def generate_css_shorthand(
    top: Union[float, None], 
    right: Union[float, None], 
    bottom: Union[float, None], 
    left: Union[float, None]
) -> str:
    """
    Generate CSS shorthand for values like padding or margin.
    
    Args:
        top: Top value
        right: Right value
        bottom: Bottom value
        left: Left value
        
    Returns:
        CSS shorthand string
    """
    # If all values are the same
    if top == right == bottom == left and top is not None:
        return f"{top}px"
    
    # If vertical values match and horizontal values match
    if top == bottom and right == left and top is not None and right is not None:
        return f"{top}px {right}px"
    
    # If only left/right differ
    if top == bottom and top is not None:
        right_val = f"{right}px" if right is not None else "0"
        left_val = f"{left}px" if left is not None else "0"
        if right == left:
            return f"{top}px {right_val}"
        return f"{top}px {right_val} {top}px {left_val}"
    
    # Full shorthand
    top_val = f"{top}px" if top is not None else "0"
    right_val = f"{right}px" if right is not None else "0"
    bottom_val = f"{bottom}px" if bottom is not None else "0"
    left_val = f"{left}px" if left is not None else "0"
    
    return f"{top_val} {right_val} {bottom_val} {left_val}"


def sanitize_name(name: str) -> str:
    """
    Sanitize a name for use as an identifier.
    
    Args:
        name: The input name
        
    Returns:
        Sanitized name for use as an identifier
    """
    # Replace spaces and special characters with underscores
    sanitized = "".join(c if c.isalnum() else "_" for c in name)
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    
    return sanitized


def is_component_instance(node_data: Dict) -> bool:
    """
    Check if a node is a component instance.
    
    Args:
        node_data: Raw node data from Figma API
        
    Returns:
        True if the node is a component instance
    """
    return node_data.get("type") == "INSTANCE" and "componentId" in node_data


def get_variable_name_from_id(variable_id: str, variables_data: Dict) -> Optional[str]:
    """
    Get the name of a variable from its ID.
    
    Args:
        variable_id: The ID of the variable
        variables_data: The variables data from the Figma API
        
    Returns:
        The variable name or None if not found
    """
    if "meta" in variables_data and "variables" in variables_data["meta"]:
        variable = variables_data["meta"]["variables"].get(variable_id)
        if variable:
            return variable.get("name")
    
    return None


def get_collection_name(collection_id: str, variables_data: Dict) -> Optional[str]:
    """
    Get the name of a variable collection from its ID.
    
    Args:
        collection_id: The ID of the collection
        variables_data: The variables data from the Figma API
        
    Returns:
        The collection name or None if not found
    """
    if "meta" in variables_data and "variableCollections" in variables_data["meta"]:
        collection = variables_data["meta"]["variableCollections"].get(collection_id)
        if collection:
            return collection.get("name")
    
    return None


def get_default_mode_id(collection_id: str, variables_data: Dict) -> Optional[str]:
    """
    Get the ID of the default mode for a variable collection.
    
    Args:
        collection_id: The ID of the collection
        variables_data: The variables data from the Figma API
        
    Returns:
        The default mode ID or None if not found
    """
    if "meta" in variables_data and "variableCollections" in variables_data["meta"]:
        collection = variables_data["meta"]["variableCollections"].get(collection_id)
        if collection:
            return collection.get("defaultModeId")
    
    return None


def get_resolved_variable_value(
    variable_id: str, 
    variables_data: Dict,
    mode_id: Optional[str] = None
) -> Optional[any]:
    """
    Get the resolved value of a variable for a specific mode.
    
    Args:
        variable_id: The ID of the variable
        variables_data: The variables data from the Figma API
        mode_id: Optional mode ID (will use default mode if not specified)
        
    Returns:
        The resolved value of the variable or None if not found
    """
    if "meta" not in variables_data or "variables" not in variables_data["meta"]:
        return None
    
    variable = variables_data["meta"]["variables"].get(variable_id)
    if not variable or "valuesByMode" not in variable:
        return None
    
    # If mode_id is not specified, use default mode for the collection
    if mode_id is None and "variableCollectionId" in variable:
        collection_id = variable["variableCollectionId"]
        mode_id = get_default_mode_id(collection_id, variables_data)
        
    if mode_id is None or mode_id not in variable["valuesByMode"]:
        # If we still don't have a mode_id or it's not valid, try to get the first available mode
        if variable["valuesByMode"]:
            mode_id = next(iter(variable["valuesByMode"]))
        else:
            return None
    
    return variable["valuesByMode"].get(mode_id) 