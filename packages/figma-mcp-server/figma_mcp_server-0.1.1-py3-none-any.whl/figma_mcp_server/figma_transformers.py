"""
Transformer functions to convert raw Figma API data into simplified model structures.
"""
from typing import Dict, List, Optional, Any, Union, Tuple, TypeVar, Generic, Callable
import hashlib
import json

from .models import (
    BoundingBox,
    SimplifiedFill,
    SimplifiedStroke,
    SimplifiedEffect,
    SimplifiedTextStyle,
    SimplifiedLayout,
    StyleReference
)
from .figma_utils import (
    convert_figma_color_to_hex_opacity,
    format_rgba_color,
    generate_var_id
)


T = TypeVar('T')


def get_or_create_style_definition(
    style_type: str, 
    style_properties: Dict[str, Any], 
    global_vars: Dict
) -> str:
    """
    Common function to get or create a style definition and return its ID.
    
    Args:
        style_type: Type of style (fills, strokes, effects, textStyles, layouts)
        style_properties: Dictionary of style properties
        global_vars: Global variables dictionary for de-duplication
        
    Returns:
        Style ID referencing the definition in globalVars.definitions
    """
    # Generate a unique key for this style
    style_key = json.dumps(style_properties, sort_keys=True)
    
    # Ensure definitions structure exists
    if "definitions" not in global_vars:
        global_vars["definitions"] = {}
    
    if style_type not in global_vars["definitions"]:
        global_vars["definitions"][style_type] = {}
    
    # Check if we already have this style defined by comparing properties
    style_id = None
    for existing_id, existing_def in global_vars["definitions"][style_type].items():
        is_match = True
        
        # Compare all properties
        for key, value in style_properties.items():
            if key not in existing_def or existing_def[key] != value:
                is_match = False
                break
        
        if is_match:
            style_id = existing_id
            break
    
    if not style_id:
        # Generate a new style ID
        hash_obj = hashlib.md5(style_key.encode())
        unique_id = hash_obj.hexdigest()[:8]
        prefix = style_type.rstrip('s')  # Remove trailing 's' for singular form
        style_id = generate_var_id(prefix, unique_id)
        
        # Store the actual style definition
        global_vars["definitions"][style_type][style_id] = style_properties
    
    return style_id


def build_bounding_box(node_data: Dict) -> Optional[BoundingBox]:
    """
    Extract and build a BoundingBox from node data.
    
    Args:
        node_data: Raw node data from Figma API
        
    Returns:
        BoundingBox object or None if not available
    """
    if "absoluteBoundingBox" not in node_data:
        return None
    
    box = node_data["absoluteBoundingBox"]
    return BoundingBox(
        x=box.get("x", 0),
        y=box.get("y", 0),
        width=box.get("width", 0),
        height=box.get("height", 0)
    )


def extract_variable_reference(
    node_data: Dict,
    property_path: List[str],
    variables_data: Dict,
    global_vars: Dict
) -> Optional[StyleReference]:
    """
    Extract a variable reference for a property if it exists.
    
    Args:
        node_data: Raw node data from Figma API
        property_path: Path to the property (e.g., ["fills", 0, "color"])
        variables_data: Figma variables data
        global_vars: Global variables dictionary for de-duplication
        
    Returns:
        StyleReference object or None if no variable binding exists
    """
    if "boundVariables" not in node_data:
        return None
    
    # Navigate to the bound variable info
    bound_vars = node_data["boundVariables"]
    
    # Convert property path to the format used in boundVariables
    # e.g., ["fills", 0, "color"] -> "fills[0].color"
    bound_var_key = ""
    for i, part in enumerate(property_path):
        if isinstance(part, int):
            # Array index
            bound_var_key += f"[{part}]"
        else:
            # Object property
            if i > 0:
                bound_var_key += "."
            bound_var_key += part
    
    # Check if this property is bound to a variable
    if bound_var_key in bound_vars and "id" in bound_vars[bound_var_key]:
        variable_id = bound_vars[bound_var_key]["id"]
        
        # Get variable info from variables_data
        if "meta" in variables_data and "variables" in variables_data["meta"]:
            variable = variables_data["meta"]["variables"].get(variable_id)
            if variable and "name" in variable:
                variable_name = variable["name"]
                return StyleReference(
                    type="variable",
                    id=f"variable:{variable_name}"
                )
    
    return None


def build_fills(
    node_data: Dict,
    variables_data: Dict,
    global_vars: Dict
) -> List[SimplifiedFill]:
    """
    Build simplified fills from node data.
    
    Args:
        node_data: Raw node data from Figma API
        variables_data: Figma variables data
        global_vars: Global variables dictionary for de-duplication
        
    Returns:
        List of SimplifiedFill objects with references to globalVars
    """
    if "fills" not in node_data or not node_data["fills"]:
        return []
    
    result = []
    
    for i, fill in enumerate(node_data["fills"]):
        if fill.get("visible", True) is False or fill.get("type") == "IMAGE":
            # Skip invisible fills or handle image fills separately
            continue
            
        if fill.get("type") == "SOLID":
            # Check if this fill is bound to a variable
            variable_ref = extract_variable_reference(
                node_data, 
                ["fills", i, "color"], 
                variables_data,
                global_vars
            )
            
            if variable_ref:
                # This fill is bound to a variable
                result.append(SimplifiedFill(
                    reference=variable_ref
                ))
            else:
                # This is a direct color value
                color = fill.get("color", {})
                opacity = fill.get("opacity", 1.0)
                
                # Convert to hex
                hex_color, alpha = convert_figma_color_to_hex_opacity(color, opacity)
                
                # Create fill properties
                fill_properties = {
                    "color": hex_color,
                    "opacity": alpha
                }
                
                # Get or create style reference
                style_id = get_or_create_style_definition("fills", fill_properties, global_vars)
                
                # Create the fill with a reference to the global style
                result.append(SimplifiedFill(
                    reference=StyleReference(
                        type="style",
                        id=style_id
                    )
                ))
                
        # Add handling for other fill types (GRADIENT_LINEAR, etc.) as needed
    
    return result


def build_strokes(
    node_data: Dict,
    variables_data: Dict,
    global_vars: Dict
) -> List[SimplifiedStroke]:
    """
    Build simplified strokes from node data.
    
    Args:
        node_data: Raw node data from Figma API
        variables_data: Figma variables data
        global_vars: Global variables dictionary for de-duplication
        
    Returns:
        List of SimplifiedStroke objects with references to globalVars
    """
    if "strokes" not in node_data or not node_data["strokes"]:
        return []
    
    result = []
    
    for i, stroke in enumerate(node_data["strokes"]):
        if stroke.get("visible", True) is False:
            continue
            
        if stroke.get("type") == "SOLID":
            # Check if this stroke is bound to a variable
            variable_ref = extract_variable_reference(
                node_data, 
                ["strokes", i, "color"], 
                variables_data,
                global_vars
            )
            
            # Get stroke properties
            color = stroke.get("color", {})
            opacity = stroke.get("opacity", 1.0)
            weight = node_data.get("strokeWeight", 1.0)
            align = node_data.get("strokeAlign", "CENTER")
            
            # Check if stroke weight is bound to a variable
            weight_variable_ref = extract_variable_reference(
                node_data, 
                ["strokeWeight"], 
                variables_data,
                global_vars
            )
            
            if variable_ref:
                # This stroke color is bound to a variable
                result.append(SimplifiedStroke(
                    reference=variable_ref
                ))
            else:
                # This is a direct color value
                hex_color, alpha = convert_figma_color_to_hex_opacity(color, opacity)
                
                # Create stroke properties
                stroke_properties = {
                    "color": hex_color,
                    "opacity": alpha,
                    "weight": weight,
                    "align": align
                }
                
                # Get or create style reference
                style_id = get_or_create_style_definition("strokes", stroke_properties, global_vars)
                
                # Create the stroke with a reference to the global style
                result.append(SimplifiedStroke(
                    reference=StyleReference(
                        type="style",
                        id=style_id
                    )
                ))
    
    return result


def build_effects(
    node_data: Dict,
    variables_data: Dict,
    global_vars: Dict
) -> List[SimplifiedEffect]:
    """
    Build simplified effects from node data.
    
    Args:
        node_data: Raw node data from Figma API
        variables_data: Figma variables data
        global_vars: Global variables dictionary for de-duplication
        
    Returns:
        List of SimplifiedEffect objects with references to globalVars
    """
    if "effects" not in node_data or not node_data["effects"]:
        return []
    
    result = []
    
    for i, effect in enumerate(node_data["effects"]):
        if effect.get("visible", True) is False:
            continue
        
        effect_type = effect.get("type", "")
        
        if effect_type == "DROP_SHADOW" or effect_type == "INNER_SHADOW":
            # Check if the effect color is bound to a variable
            variable_ref = extract_variable_reference(
                node_data, 
                ["effects", i, "color"], 
                variables_data,
                global_vars
            )
            
            # Extract effect properties
            color = effect.get("color", {})
            opacity = effect.get("opacity", 1.0)
            radius = effect.get("radius", 0)
            offset = {
                "x": effect.get("offset", {}).get("x", 0),
                "y": effect.get("offset", {}).get("y", 0)
            }
            
            if variable_ref:
                # This effect color is bound to a variable
                result.append(SimplifiedEffect(
                    type=effect_type.lower(),
                    reference=variable_ref
                ))
            else:
                # This is a direct color value
                hex_color, alpha = convert_figma_color_to_hex_opacity(color, opacity)
                
                # Create effect properties
                effect_properties = {
                    "type": effect_type.lower(),
                    "color": hex_color,
                    "opacity": alpha,
                    "radius": radius,
                    "offset": offset
                }
                
                # Get or create style reference
                style_id = get_or_create_style_definition("effects", effect_properties, global_vars)
                
                # Create the effect with a reference to the global style
                result.append(SimplifiedEffect(
                    type=effect_type.lower(),
                    reference=StyleReference(
                        type="style",
                        id=style_id
                    )
                ))
        
        elif effect_type == "LAYER_BLUR" or effect_type == "BACKGROUND_BLUR":
            radius = effect.get("radius", 0)
            
            # Create effect properties
            effect_properties = {
                "type": effect_type.lower(),
                "radius": radius
            }
            
            # Get or create style reference
            style_id = get_or_create_style_definition("effects", effect_properties, global_vars)
            
            # Create the effect with a reference to the global style
            result.append(SimplifiedEffect(
                type=effect_type.lower(),
                reference=StyleReference(
                    type="style",
                    id=style_id
                )
            ))
    
    return result


def build_text_style(
    node_data: Dict,
    variables_data: Dict,
    global_vars: Dict
) -> Optional[SimplifiedTextStyle]:
    """
    Build a simplified text style from node data.
    
    Args:
        node_data: Raw node data from Figma API
        variables_data: Figma variables data
        global_vars: Global variables dictionary for de-duplication
        
    Returns:
        SimplifiedTextStyle object with reference to globalVars or None if not applicable
    """
    if node_data.get("type") != "TEXT" or "style" not in node_data:
        return None
    
    style = node_data["style"]
    
    # Extract text style properties
    font_family = style.get("fontFamily")
    font_size = style.get("fontSize")
    font_weight = style.get("fontWeight")
    line_height = style.get("lineHeightPx") or style.get("lineHeight")
    letter_spacing = style.get("letterSpacing")
    text_align = style.get("textAlignHorizontal")
    text_case = style.get("textCase")
    text_decoration = style.get("textDecoration")
    
    # Check if font size is bound to a variable
    font_size_variable_ref = extract_variable_reference(
        node_data, 
        ["style", "fontSize"], 
        variables_data,
        global_vars
    )
    
    # Check if line height is bound to a variable
    line_height_variable_ref = extract_variable_reference(
        node_data, 
        ["style", "lineHeightPx"], 
        variables_data,
        global_vars
    )
    
    # Check if letter spacing is bound to a variable
    letter_spacing_variable_ref = extract_variable_reference(
        node_data, 
        ["style", "letterSpacing"], 
        variables_data,
        global_vars
    )
    
    # If any property is bound to a variable, we need to create a special composite text style
    if font_size_variable_ref or line_height_variable_ref or letter_spacing_variable_ref:
        # Create a new composite text style with variable references
        style_props = {
            "fontFamily": font_family,
            "fontWeight": font_weight,
            "textAlign": text_align,
            "textCase": text_case,
            "textDecoration": text_decoration
        }
        
        # Add variable references where applicable
        if font_size_variable_ref:
            style_props["fontSize"] = {"type": "variable", "id": font_size_variable_ref.id}
        else:
            style_props["fontSize"] = font_size
            
        if line_height_variable_ref:
            style_props["lineHeight"] = {"type": "variable", "id": line_height_variable_ref.id}
        else:
            style_props["lineHeight"] = line_height
            
        if letter_spacing_variable_ref:
            style_props["letterSpacing"] = {"type": "variable", "id": letter_spacing_variable_ref.id}
        else:
            style_props["letterSpacing"] = letter_spacing
        
        # Get or create style reference
        style_id = get_or_create_style_definition("textStyles", style_props, global_vars)
        
        # Return a reference to this composite style
        return SimplifiedTextStyle(
            reference=StyleReference(
                type="style",
                id=style_id
            )
        )
    
    # For pure static text styles without variable references
    # Create text style properties
    text_style_props = {
        "fontFamily": font_family,
        "fontSize": font_size,
        "fontWeight": font_weight,
        "lineHeight": line_height,
        "letterSpacing": letter_spacing,
        "textAlign": text_align,
        "textCase": text_case,
        "textDecoration": text_decoration
    }
    
    # Get or create style reference
    style_id = get_or_create_style_definition("textStyles", text_style_props, global_vars)
    
    # Return text style with reference to the global style
    return SimplifiedTextStyle(
        reference=StyleReference(
            type="style",
            id=style_id
        )
    )


def build_layout(
    node_data: Dict,
    parent_node_data: Optional[Dict],
    variables_data: Dict,
    global_vars: Dict
) -> Optional[str]:
    """
    Build a layout reference key for the node and store the layout data in globalVars.
    
    Args:
        node_data: Raw node data from Figma API
        parent_node_data: Raw parent node data from Figma API
        variables_data: Figma variables data
        global_vars: Global variables dictionary for de-duplication
        
    Returns:
        String reference key to the layout in globalVars.definitions.layouts
    """
    # Extract layout information from the node
    layout_info = {}
    
    # Check for auto-layout properties
    layout_mode = node_data.get("layoutMode")
    
    # Create a layout object based on the node type
    if layout_mode in ["HORIZONTAL", "VERTICAL"]:
        # For auto-layout frames
        layout_info["mode"] = "row" if layout_mode == "HORIZONTAL" else "column"
        
        # Alignment
        primary_axis_align = node_data.get("primaryAxisAlignItems", "START").lower()
        counter_axis_align = node_data.get("counterAxisAlignItems", "START").lower()
        
        layout_info["alignment"] = {
            "primaryAxis": primary_axis_align,
            "counterAxis": counter_axis_align
        }
        
        # Extract padding
        padding = {}
        if "paddingTop" in node_data: padding["top"] = node_data["paddingTop"]
        if "paddingRight" in node_data: padding["right"] = node_data["paddingRight"]
        if "paddingBottom" in node_data: padding["bottom"] = node_data["paddingBottom"]
        if "paddingLeft" in node_data: padding["left"] = node_data["paddingLeft"]
        
        if padding:
            layout_info["padding"] = padding
        
        # Item spacing (gap)
        if "itemSpacing" in node_data:
            layout_info["gap"] = node_data["itemSpacing"]
        
        # Layout sizing
        sizing = {}
        
        # Default to "fill" for width and height in auto-layout
        if "layoutSizingHorizontal" in node_data:
            h_sizing = node_data["layoutSizingHorizontal"].lower()
            sizing["horizontal"] = "hug" if h_sizing == "HUG" else "fixed" if h_sizing == "FIXED" else "fill"
        else:
            sizing["horizontal"] = "fill"
            
        if "layoutSizingVertical" in node_data:
            v_sizing = node_data["layoutSizingVertical"].lower()
            sizing["vertical"] = "hug" if v_sizing == "HUG" else "fixed" if v_sizing == "FIXED" else "fill"
        else:
            sizing["vertical"] = "fill"
            
        layout_info["sizing"] = sizing
    else:
        # For non-auto-layout nodes
        layout_info["mode"] = "none"
        
        # For non-auto-layout, still include sizing information based on the bounding box
        sizing = {}
        if "absoluteBoundingBox" in node_data:
            box = node_data["absoluteBoundingBox"]
            # We don't include the actual dimensions here, just the sizing behavior
            sizing["horizontal"] = "fixed"
            sizing["vertical"] = "fixed"
        
        if sizing:
            layout_info["sizing"] = sizing
    
    # Get or create layout definition
    layout_id = get_or_create_style_definition("layouts", layout_info, global_vars)
    
    return layout_id