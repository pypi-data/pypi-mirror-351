"""
Core logic for parsing Figma API responses into SimplifiedDesign structures.
"""
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    SimplifiedNode,
    SimplifiedDesign,
    BoundingBox,
    MainComponentDefinition,
    FigmaVariableOutput,
    AppliedVariantInfo
)
from .figma_transformers import (
    build_bounding_box,
    build_fills,
    build_strokes,
    build_effects,
    build_text_style,
    build_layout
)
from .figma_utils import (
    is_visible,
    is_component_instance,
    get_variable_name_from_id,
    get_collection_name,
    get_resolved_variable_value,
    clean_figma_name
)


def get_default_mode_id(collection_id: str, variables_data: Dict) -> Optional[str]:
    """
    Get the default mode ID for a variable collection.
    
    Args:
        collection_id: ID of the variable collection
        variables_data: Variables data from the Figma API
        
    Returns:
        Default mode ID or None if not found
    """
    if "meta" not in variables_data or "variableCollections" not in variables_data["meta"]:
        return None
    
    for coll_id, collection in variables_data["meta"]["variableCollections"].items():
        if coll_id == collection_id and "defaultModeId" in collection:
            return collection["defaultModeId"]
    
    return None


def parse_figma_node(
    raw_node_data: Dict,
    variables_data: Dict,
    components_map: Dict,
    component_sets_map: Dict,
    global_vars: Dict,
    parent_node_data: Optional[Dict] = None
) -> Optional[SimplifiedNode]:
    """
    Parse a Figma node into a SimplifiedNode structure.
    
    Args:
        raw_node_data: Raw node data from Figma API
        variables_data: Variables data from Figma API
        components_map: Dictionary mapping component IDs to component data
        component_sets_map: Dictionary mapping component set IDs to component set data
        global_vars: Global variables dictionary for de-duplication and tracking
        parent_node_data: Parent node data (if any) for context
        
    Returns:
        SimplifiedNode structure or None if the node should be skipped
    """
    # Skip invisible nodes
    if not is_visible(raw_node_data):
        return None
    
    # Skip nodes without an ID or type
    if "id" not in raw_node_data or "type" not in raw_node_data:
        return None
    
    # Extract basic node properties
    node_id = raw_node_data["id"]
    node_name = clean_figma_name(raw_node_data.get("name", ""))
    node_type = raw_node_data["type"]
    
    # Initialize the SimplifiedNode with basic properties
    simplified_node = SimplifiedNode(
        id=node_id,
        name=node_name,
        type=node_type,
        visible=True
    )
    
    # Add opacity if present
    if "opacity" in raw_node_data:
        simplified_node.opacity = raw_node_data["opacity"]
    
    # Add fills
    fills = build_fills(raw_node_data, variables_data, global_vars)
    if fills:
        simplified_node.fills = fills
    
    # Add strokes
    strokes = build_strokes(raw_node_data, variables_data, global_vars)
    if strokes:
        simplified_node.strokes = strokes
    
    # Add effects
    effects = build_effects(raw_node_data, variables_data, global_vars)
    if effects:
        simplified_node.effects = effects
    
    # Add text style and content for text nodes
    if node_type == "TEXT":
        text_style = build_text_style(raw_node_data, variables_data, global_vars)
        if text_style:
            simplified_node.textStyle = text_style
        
        # Add text content
        if "characters" in raw_node_data:
            simplified_node.text = raw_node_data["characters"]
    
    # Add layout properties (now returns a layout reference key)
    layout_key = build_layout(raw_node_data, parent_node_data, variables_data, global_vars)
    if layout_key:
        simplified_node.layout = layout_key
    
    # Add position and size information
    if "absoluteBoundingBox" in raw_node_data and raw_node_data["absoluteBoundingBox"] is not None:
        abs_box = raw_node_data["absoluteBoundingBox"]
        simplified_node.absoluteBounds = BoundingBox(
            x=abs_box.get("x", 0),
            y=abs_box.get("y", 0),
            width=abs_box.get("width", 0),
            height=abs_box.get("height", 0)
        )
        
        # Calculate relative bounds if parent is available
        if (parent_node_data and 
            "absoluteBoundingBox" in parent_node_data and 
            parent_node_data["absoluteBoundingBox"] is not None):
            parent_box = parent_node_data["absoluteBoundingBox"]
            
            # Calculate position relative to parent
            relative_x = abs_box["x"] - parent_box["x"]
            relative_y = abs_box["y"] - parent_box["y"]
            
            simplified_node.relativeBounds = BoundingBox(
                x=relative_x,
                y=relative_y,
                width=abs_box.get("width", 0),
                height=abs_box.get("height", 0)
            )
    
    # Add corner radius
    if "cornerRadius" in raw_node_data:
        simplified_node.cornerRadius = raw_node_data["cornerRadius"]
    
    # Handle component sets - show variant information
    if node_type == "COMPONENT_SET":
        # Extract component variants from children
        variant_summary = {}
        if "children" in raw_node_data and raw_node_data["children"]:
            for child in raw_node_data["children"]:
                if child.get("type") == "COMPONENT":
                    child_name = clean_figma_name(child.get("name", ""))
                    variant_props = extract_variant_properties_from_name(child_name)
                    if variant_props:
                        for prop, values in variant_props.items():
                            if prop not in variant_summary:
                                variant_summary[prop] = set()
                            variant_summary[prop].update(values)
        
        # Convert sets to lists for serialization
        if variant_summary:
            simplified_node.variantProperties = {k: list(v) for k, v in variant_summary.items()}
    
    # Handle component instances
    if is_component_instance(raw_node_data):
        component_id = raw_node_data["componentId"]
        simplified_node.componentId = component_id
        
        # Look up the component name and clean it
        if component_id in components_map:
            component_name = clean_figma_name(components_map[component_id].get("name", ""))
            simplified_node.componentName = component_name
        
        # Extract variant properties
        if "componentProperties" in raw_node_data:
            variant_props = {}
            
            for key, prop in raw_node_data["componentProperties"].items():
                if prop.get("type") == "VARIANT" and "value" in prop:
                    variant_props[key] = prop["value"]
            
            if variant_props:
                simplified_node.appliedVariants = AppliedVariantInfo(root=variant_props)
        
        # Extract overridden properties
        if "componentProperties" in raw_node_data:
            overridden = {}
            
            for key, prop in raw_node_data["componentProperties"].items():
                if prop.get("type") not in ["VARIANT"] and "value" in prop:
                    overridden[key] = prop["value"]
            
            if overridden:
                simplified_node.overriddenProperties = overridden
    
    # Recursively process children
    if "children" in raw_node_data and raw_node_data["children"]:
        children = []
        
        for child in raw_node_data["children"]:
            simplified_child = parse_figma_node(
                child,
                variables_data,
                components_map,
                component_sets_map,
                global_vars,
                raw_node_data  # Current node becomes the parent for its children
            )
            
            if simplified_child:
                children.append(simplified_child)
        
        if children:
            simplified_node.children = children
    
    return simplified_node


def process_figma_variables(variables_data: Dict) -> Dict[str, FigmaVariableOutput]:
    """
    Process and structure Figma variables data.
    
    Args:
        variables_data: Variables data from the Figma API
        
    Returns:
        Dictionary of variable ID to FigmaVariableOutput
    """
    result = {}
    
    if "meta" not in variables_data:
        return result
    
    if "variables" not in variables_data["meta"]:
        return result
    
    for var_id, variable in variables_data["meta"]["variables"].items():
        if "name" not in variable or "resolvedType" not in variable:
            continue
        
        variable_name = variable["name"]
        collection_id = variable.get("variableCollectionId")
        collection_name = get_collection_name(collection_id, variables_data) if collection_id else None
        
        # Get resolved value for default mode
        resolved_value = None
        if "valuesByMode" in variable:
            default_mode_id = None
            if collection_id:
                default_mode_id = get_default_mode_id(collection_id, variables_data)
            
            resolved_value = get_resolved_variable_value(var_id, variables_data, default_mode_id)
        
        # Create the variable output
        var_output = FigmaVariableOutput(
            id=var_id,
            nameFromFigma=variable_name,
            resolvedValue=resolved_value,
            collectionName=collection_name
        )
        
        result[variable_name] = var_output
    
    return result


def extract_variant_properties_from_name(name: str) -> Optional[Dict[str, List[str]]]:
    """
    Extract variant properties from a component name.
    
    Many Figma components follow naming patterns like:
    - "Button/State=Default"
    - "Component/Property=Value/Property2=Value2"
    
    This function attempts to extract these properties.
    
    Args:
        name: Component name
        
    Returns:
        Dictionary of property names to possible values, or None if no properties found
    """
    if not name:
        return None
        
    variant_props = {}
    
    # Check for equals sign pattern (State=Default)
    if "=" in name:
        # Try to extract properties in the format "Property=Value"
        parts = name.split("/")
        for part in parts:
            if "=" in part:
                try:
                    prop, value = part.split("=", 1)
                    if prop and value:
                        if prop not in variant_props:
                            variant_props[prop] = []
                        if value not in variant_props[prop]:
                            variant_props[prop].append(value)
                except:
                    pass
    
    # If no equals sign pattern found, try to extract from path structure
    # Format like: ComponentName/Variant1/Variant2
    elif "/" in name:
        parts = name.split("/")
        if len(parts) > 1:
            # Skip the first part (component name) and use remaining parts as Style variants
            styles = parts[1:]
            if styles:
                variant_props["Style"] = styles
    
    return variant_props if variant_props else None


def process_component_definitions(
    raw_components_data: Dict,
    raw_component_sets_data: Dict,
    raw_file_data: Dict
) -> Tuple[Dict[str, Dict], Dict[str, Dict], Dict[str, MainComponentDefinition]]:
    """
    Process component and component set definitions.
    
    Args:
        raw_components_data: Component data from the Figma API
        raw_component_sets_data: Component set data from the Figma API
        raw_file_data: Raw file data from the Figma API (contains components data)
        
    Returns:
        Tuple of (components_map, component_sets_map, simplified_components)
    """
    components_map = {}
    component_sets_map = {}
    simplified_components = {}
    
    # 1. First, process components from raw_file_data.components (main file API response)
    # This will have componentId -> component mappings
    if "components" in raw_file_data and raw_file_data["components"]:
        for comp_id, comp_data in raw_file_data["components"].items():
            components_map[comp_id] = comp_data
            
            # Extract name from component data and clean it
            component_name = clean_figma_name(comp_data.get("name", ""))
            
            # Try to extract variant properties from the name
            variant_properties = extract_variant_properties_from_name(component_name)
            
            # Create a simplified component definition
            simplified_components[comp_id] = MainComponentDefinition(
                id=comp_id,
                name=component_name,
                description=comp_data.get("description", ""),
                variantProperties=variant_properties
            )
    
    # 2. Process component sets from raw_component_sets_data
    if "meta" in raw_component_sets_data and "component_sets" in raw_component_sets_data["meta"]:
        for comp_set in raw_component_sets_data["meta"]["component_sets"]:
            if "key" in comp_set and "name" in comp_set:
                component_sets_map[comp_set["key"]] = comp_set
    
    # 3. Process components from raw_components_data (components endpoint)
    # These have more metadata like componentSetId relationships
    if "meta" in raw_components_data and "components" in raw_components_data["meta"]:
        for component in raw_components_data["meta"]["components"]:
            if "key" in component and "name" in component:
                # Update our map with additional metadata
                components_map[component["key"]] = {**components_map.get(component["key"], {}), **component}
                
                # Clean component name
                component_name = clean_figma_name(component.get("name", ""))
                
                # Extract variant properties for components with a component set
                variant_properties = extract_variant_properties_from_name(component_name)
                
                if not variant_properties and "componentSetId" in component and component["componentSetId"] in component_sets_map:
                    # Try to extract variant properties from component set
                    comp_set = component_sets_map[component["componentSetId"]]
                    if "name" in comp_set:
                        # Try to extract variant properties from the component set name
                        variant_properties = extract_variant_properties_from_name(clean_figma_name(comp_set.get("name", "")))
                
                # Create or update the MainComponentDefinition
                if component["key"] in simplified_components:
                    # Update existing component with more data
                    existing = simplified_components[component["key"]]
                    existing.name = component_name  # Update with cleaned name
                    if variant_properties and not existing.variantProperties:
                        existing.variantProperties = variant_properties
                    if "description" in component and not existing.description:
                        existing.description = component["description"]
                else:
                    # Create new component definition
                    simplified_components[component["key"]] = MainComponentDefinition(
                        id=component["key"],
                        name=component_name,
                        description=component.get("description", ""),
                        variantProperties=variant_properties
                    )
    
    return components_map, component_sets_map, simplified_components


def parse_figma_response(
    raw_file_data: Dict,
    raw_components_data: Dict,
    raw_component_sets_data: Dict,
    raw_variables_data: Dict
) -> SimplifiedDesign:
    """
    Parse a complete Figma API response into a SimplifiedDesign structure.
    
    Args:
        raw_file_data: Raw file data from Figma API
        raw_components_data: Raw components data from Figma API
        raw_component_sets_data: Raw component sets data from Figma API
        raw_variables_data: Raw variables data from Figma API
        
    Returns:
        SimplifiedDesign structure
    """
    # Initialize global variables for de-duplication
    global_vars = {
        "styles": {
            "fills": {},
            "strokes": {},
            "effects": {},
            "textStyles": {},
            "layouts": {}
        }, 
        "definitions": {
            "fills": {},
            "strokes": {},
            "effects": {},
            "textStyles": {},
            "layouts": {}
        }
    }
    
    # Process component definitions
    components_map, component_sets_map, component_definitions = process_component_definitions(
        raw_components_data,
        raw_component_sets_data,
        raw_file_data
    )
    
    # Process variables
    figma_variables = process_figma_variables(raw_variables_data)
    
    # Extract file metadata
    name = raw_file_data.get("name", "Untitled Figma File")
    last_modified = raw_file_data.get("lastModified", "")
    thumbnail_url = raw_file_data.get("thumbnailUrl", "")
    
    # Process document and extract nodes
    document = raw_file_data.get("document", {})
    if not document:
        # Empty document
        return SimplifiedDesign(
            name=name,
            lastModified=last_modified,
            thumbnailUrl=thumbnail_url,
            nodes=[],
            components=component_definitions,
            componentSets={},
            figmaVariables=figma_variables,
            globalVars=global_vars
        )
    
    # Choose a root node to start from
    # For a complete file, this would be the document
    # For a node fetch, this would be the specific node
    root_nodes = []
    
    if "children" in document:
        # Traverse the entire document (all pages)
        for page in document["children"]:
            # Skip invisible pages
            if not is_visible(page):
                continue
            
            # Process page
            simplified_page = parse_figma_node(
                page,
                raw_variables_data,
                components_map,
                component_sets_map,
                global_vars
            )
            
            if simplified_page:
                root_nodes.append(simplified_page)
    
    # Process all nodes and apply simplification
    simplified_nodes = []
    for node in root_nodes:
        simplified_node = simplify_node_for_output(node, focus_on_components=False)  # Set to False to keep more details
        # Include more nodes to preserve structure
        if (simplified_node.children or 
            simplified_node.type in ["COMPONENT_SET", "COMPONENT", "FRAME", "SECTION", "CANVAS"] or 
            simplified_node.componentId):
            simplified_nodes.append(simplified_node)
    
    # Collect actually used components and filter the component definitions
    used_component_ids = collect_used_components(simplified_nodes)
    filtered_components = filter_components_by_usage(component_definitions, used_component_ids)
    
    return SimplifiedDesign(
        name=name,
        lastModified=last_modified,
        thumbnailUrl=thumbnail_url,
        nodes=simplified_nodes,
        components=filtered_components,
        componentSets={},
        figmaVariables=figma_variables,
        globalVars=global_vars
    )


def simplify_node_for_output(node: SimplifiedNode, focus_on_components: bool = True) -> SimplifiedNode:
    """
    Create a simplified version of a node focused on component structure.
    
    Args:
        node: The original SimplifiedNode
        focus_on_components: If True, emphasize component information and reduce other details
        
    Returns:
        Simplified version of the node
    """
    # Create a copy of the node with essential information
    simplified = SimplifiedNode(
        id=node.id,
        name=node.name,
        type=node.type,
        visible=node.visible
    )
    
    # Always keep component-related information
    if node.componentId:
        simplified.componentId = node.componentId
    if node.componentName:
        simplified.componentName = node.componentName
    if node.appliedVariants:
        simplified.appliedVariants = node.appliedVariants
    if node.variantProperties:
        simplified.variantProperties = node.variantProperties
    
    # Keep styling information for ALL nodes, not just components
    if node.cornerRadius is not None:
        simplified.cornerRadius = node.cornerRadius
    if node.opacity is not None:
        simplified.opacity = node.opacity
    if node.fills:
        simplified.fills = node.fills
    if node.strokes:
        simplified.strokes = node.strokes
    if node.effects:
        simplified.effects = node.effects
    if node.layout:
        simplified.layout = node.layout
    
    # Keep text content for text nodes
    if node.type == "TEXT" and node.text:
        simplified.text = node.text
        if node.textStyle:
            simplified.textStyle = node.textStyle
    
    # Recursively simplify children, keeping ALL children for detailed structure
    if node.children:
        simplified_children = []
        for child in node.children:
            # Keep ALL children for component-related nodes to preserve complete structure
            if (node.type in ["COMPONENT_SET", "COMPONENT"] or node.componentId or 
                child.type in ["COMPONENT_SET", "COMPONENT"] or child.componentId):
                simplified_children.append(simplify_node_for_output(child, False))  # Don't filter children
            # Include other important structural nodes
            elif child.type in ["FRAME", "SECTION", "CANVAS", "RECTANGLE", "ELLIPSE", "GROUP", "INSTANCE"] and child.children:
                simplified_children.append(simplify_node_for_output(child, focus_on_components))
            # Include leaf nodes that might have styling information
            elif child.type in ["RECTANGLE", "ELLIPSE", "GROUP", "INSTANCE", "TEXT", "VECTOR"]:
                simplified_children.append(simplify_node_for_output(child, False))  # Keep all styling
        
        if simplified_children:
            simplified.children = simplified_children
    
    return simplified


def has_component_descendants(node: SimplifiedNode) -> bool:
    """
    Check if a node has any component-related descendants.
    
    Args:
        node: The node to check
        
    Returns:
        True if the node has component sets, components, or instances in its tree
    """
    if node.type in ["COMPONENT_SET", "COMPONENT"] or node.componentId:
        return True
    
    if node.children:
        return any(has_component_descendants(child) for child in node.children)
    
    return False


def collect_used_components(nodes: List[SimplifiedNode]) -> set:
    """
    Collect all component IDs that are actually used in the given nodes.
    
    Args:
        nodes: List of SimplifiedNode to traverse
        
    Returns:
        Set of component IDs that are actually used
    """
    used_components = set()
    
    def traverse_node(node: SimplifiedNode):
        # If this node is a component instance, add its component ID
        if node.componentId:
            used_components.add(node.componentId)
        
        # If this node is a component or component set, include it
        if node.type in ["COMPONENT", "COMPONENT_SET"]:
            used_components.add(node.id)
        
        # Recursively traverse children
        if node.children:
            for child in node.children:
                traverse_node(child)
    
    # Traverse all nodes
    for node in nodes:
        traverse_node(node)
    
    return used_components


def filter_components_by_usage(
    component_definitions: Dict[str, MainComponentDefinition],
    used_component_ids: set
) -> Dict[str, MainComponentDefinition]:
    """
    Filter component definitions to only include those that are actually used.
    
    Args:
        component_definitions: All component definitions
        used_component_ids: Set of component IDs that are actually used
        
    Returns:
        Filtered component definitions
    """
    filtered = {}
    
    for comp_id, comp_def in component_definitions.items():
        if comp_id in used_component_ids:
            filtered[comp_id] = comp_def
    
    return filtered 