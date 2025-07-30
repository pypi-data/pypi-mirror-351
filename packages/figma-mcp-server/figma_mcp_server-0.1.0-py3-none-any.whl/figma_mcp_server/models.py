"""
Pydantic models for Figma API responses and the SimplifiedDesign structure.
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, RootModel


# Simplified Design Models - These define our output structure

class BoundingBox(BaseModel):
    """Represents the bounding box of a node in the design."""
    x: float
    y: float
    width: float
    height: float


class StyleReference(BaseModel):
    """Reference to a style or variable."""
    type: str = Field(..., description="Type of reference (variable, style)")
    id: str = Field(..., description="ID of the variable or style being referenced")


class SimplifiedFill(BaseModel):
    """Represents a fill reference to either a variable or a style in globalVars."""
    reference: StyleReference
    type: str = "fill"


class SimplifiedStroke(BaseModel):
    """Represents a stroke reference to either a variable or a style in globalVars."""
    reference: StyleReference
    type: str = "stroke"


class SimplifiedEffect(BaseModel):
    """Represents an effect reference to either a variable or a style in globalVars."""
    reference: StyleReference
    type: str = Field(..., description="Effect type (shadow, blur, etc.)")


class SimplifiedTextStyle(BaseModel):
    """Represents text styling properties as a reference to globalVars."""
    reference: StyleReference


class SimplifiedLayout(BaseModel):
    """Represents layout properties of a node."""
    mode: Optional[str] = None  # "NONE", "HORIZONTAL", "VERTICAL"
    alignment: Optional[Dict[str, str]] = None  # primaryAxis, counterAxis
    padding: Optional[Dict[str, Optional[Union[float, StyleReference]]]] = None
    gap: Optional[Union[float, StyleReference]] = None
    dimensions: Optional[Dict[str, Optional[Union[float, StyleReference]]]] = None  # width, height
    grow: Optional[float] = None  # layoutGrow equivalent
    positioning: Optional[str] = None  # "ABSOLUTE" or "RELATIVE"


class AppliedVariantInfo(RootModel[Dict[str, str]]):
    """Information about the applied variant properties of a component instance.
    
    This is a dict where keys are property names and values are the selected variant values.
    E.g., {"State": "Default", "Size": "Medium"}
    """
    pass


class SimplifiedNode(BaseModel):
    """Represents a node in the simplified design structure."""
    id: str
    name: str
    type: str
    layout: Optional[str] = None  # Reference key to layout in globalVars.definitions.layouts
    visible: bool = True
    opacity: Optional[float] = None
    fills: Optional[List[SimplifiedFill]] = None
    strokes: Optional[List[SimplifiedStroke]] = None
    effects: Optional[List[SimplifiedEffect]] = None
    textStyle: Optional[SimplifiedTextStyle] = None
    text: Optional[str] = None  # For text nodes
    cornerRadius: Optional[Union[float, StyleReference]] = None
    
    # Component-specific fields
    componentId: Optional[str] = None  # For instances, ID of the main component
    componentName: Optional[str] = None  # For instances, name of the main component
    appliedVariants: Optional[AppliedVariantInfo] = None  # For instances, selected variants
    overriddenProperties: Optional[Dict[str, Any]] = None  # Properties overridden at instance level
    
    children: Optional[List['SimplifiedNode']] = None


class MainComponentDefinition(BaseModel):
    """Definition of a main component (reusable UI element)."""
    id: str
    name: str
    description: Optional[str] = None
    variantProperties: Optional[Dict[str, List[str]]] = None  # Property name to possible values


class FigmaVariableOutput(BaseModel):
    """Representation of a Figma Variable."""
    id: str
    nameFromFigma: str
    resolvedValue: Any
    description: Optional[str] = None
    collectionName: Optional[str] = None


class GlobalVars(BaseModel):
    """Container for global variables and definitions."""
    definitions: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class SimplifiedDesign(BaseModel):
    """Top-level model for the simplified design output."""
    name: str
    lastModified: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    nodes: List[SimplifiedNode]
    components: Dict[str, MainComponentDefinition] = Field(default_factory=dict)
    componentSets: Dict[str, Any] = Field(default_factory=dict)
    figmaVariables: Dict[str, FigmaVariableOutput] = Field(default_factory=dict)
    globalVars: GlobalVars = Field(default_factory=GlobalVars)


# Figma API Response Models - These represent the structure of the Figma API responses

class FigmaUser(BaseModel):
    """Figma user information."""
    id: str
    handle: str
    img_url: Optional[str] = None


class FigmaVersion(BaseModel):
    """Figma file version information."""
    id: str
    created_at: str
    label: Optional[str] = None
    description: Optional[str] = None
    user: FigmaUser


class FigmaComponent(BaseModel):
    """Figma component metadata."""
    key: str
    name: str
    description: Optional[str] = None
    componentSetId: Optional[str] = None
    documentationLinks: Optional[List[Dict[str, str]]] = None


class FigmaComponentSet(BaseModel):
    """Figma component set metadata."""
    key: str
    name: str
    description: Optional[str] = None


class FigmaFileComponentsResponse(BaseModel):
    """Response structure for the /v1/files/:file_key/components endpoint."""
    meta: Dict[str, Any]
    status: int


class FigmaFileComponentSetsResponse(BaseModel):
    """Response structure for the /v1/files/:file_key/component_sets endpoint."""
    meta: Dict[str, Any]
    status: int


class FigmaVariable(BaseModel):
    """Figma variable definition."""
    id: str
    name: str
    key: Optional[str] = None
    variableCollectionId: str
    resolvedType: str  # "COLOR", "FLOAT", "STRING", "BOOLEAN"
    valuesByMode: Dict[str, Any]  # Mode ID to value mapping


class FigmaVariableCollection(BaseModel):
    """Collection of related Figma variables."""
    id: str
    name: str
    key: Optional[str] = None
    modes: List[Dict[str, str]]  # List of {modeId: string, name: string}
    defaultModeId: str


class FigmaVariablesResponse(BaseModel):
    """Response structure for the /v1/files/:file_key/variables/local endpoint."""
    meta: Dict[str, Any]
    status: int


class FigmaImagesResponse(BaseModel):
    """Response structure for the /v1/images/:file_key endpoint."""
    err: Optional[str] = None
    images: Dict[str, str]  # Node ID to image URL mapping
    status: int


class FigmaFileResponse(BaseModel):
    """Response structure for the /v1/files/:file_key endpoint."""
    document: Dict[str, Any]  # Root node with children (pages)
    components: Dict[str, Any]  # Component ID to Component object mapping
    componentSets: Dict[str, Any]  # Component set ID to Component Set object mapping
    schemaVersion: int
    styles: Dict[str, Any]
    name: str
    lastModified: str
    thumbnailUrl: str
    version: str
    role: Optional[str] = None
    editorType: Optional[str] = None
    linkAccess: Optional[str] = None 