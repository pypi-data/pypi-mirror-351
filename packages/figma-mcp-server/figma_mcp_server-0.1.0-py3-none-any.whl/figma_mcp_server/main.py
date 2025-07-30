"""
Main entry point for the Figma Data MCP Server.

Defines the FastMCP server instance and implements the MCP tools.
"""
import os
import yaml
import asyncio
import json
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
import aiofiles
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .figma_service import FigmaService, FigmaAPIError
from .figma_parser import parse_figma_response


# Load environment variables
load_dotenv()

# Get Figma API key
FIGMA_API_KEY = os.getenv("FIGMA_API_KEY")
if not FIGMA_API_KEY:
    print("WARNING: FIGMA_API_KEY environment variable not set. Set it in .env file.")

# Debug flag
DEBUG = os.getenv("FIGMA_MCP_DEBUG", "0") == "1"

# Initialize Figma service globally
figma_service = FigmaService(FIGMA_API_KEY) if FIGMA_API_KEY else None

# Create FastMCP server
mcp = FastMCP(name="Figma Data MCP Server")


# MCP Tool parameter models
class GetFigmaDataParams(BaseModel):
    """Parameters for the get_figma_data tool."""
    fileKey: str = Field(..., description="The key of the Figma file (from the URL)")
    nodeId: Optional[str] = Field(None, description="Optional ID of a specific node to fetch")
    depth: Optional[int] = Field(None, description="Optional depth limit for node traversal")


class DownloadFigmaImageNode(BaseModel):
    """A node to download as an image."""
    nodeId: str = Field(..., description="ID of the node to render")
    fileName: str = Field(..., description="File name to save the image as")
    imageRef: Optional[str] = Field(None, description="Image reference ID for image fills")


class DownloadFigmaImagesParams(BaseModel):
    """Parameters for the download_figma_images tool."""
    fileKey: str = Field(..., description="The key of the Figma file")
    nodes: List[DownloadFigmaImageNode] = Field(..., description="Nodes to download as images")
    scale: float = Field(2.0, description="Scale factor for PNG images (1.0-4.0)")
    localPath: str = Field(..., description="Absolute local directory path to save images")
    format: str = Field("png", description="Image format (png or svg)")


# MCP Tools
@mcp.tool()
async def get_figma_data(
    params: GetFigmaDataParams,
    ctx: Context
) -> str:
    """
    Fetch and simplify Figma file or node data, returning it as YAML.
    
    Retrieves data from the Figma API, processes it to extract components,
    variants, and variables, and returns a simplified structure optimized
    for LLM consumption and code generation.
    
    Args:
        params: Parameters for fetching Figma data
        ctx: MCP context for logging and state access
        
    Returns:
        YAML string representing the simplified design data
        
    Raises:
        ToolError: If the Figma API key is missing or API requests fail
    """
    # Check if Figma API key is set
    if not figma_service:
        raise ToolError("FIGMA_API_KEY environment variable not set")
    
    try:
        # Log start of the operation
        ctx.info(f"Fetching Figma data for file: {params.fileKey}" + 
              (f", node: {params.nodeId}" if params.nodeId else ""))
        
        # Fetch file data
        node_ids = [params.nodeId] if params.nodeId else None
        raw_file_data = await figma_service.get_file_data(
            params.fileKey, 
            node_ids, 
            params.depth
        )
        
        if DEBUG:
            # Log file data details for debugging
            if "document" in raw_file_data:
                ctx.debug(f"Document has {len(raw_file_data['document'].get('children', []))} pages")
            
            if "components" in raw_file_data:
                ctx.debug(f"File has {len(raw_file_data['components'])} components")
                sample_keys = list(raw_file_data['components'].keys())[:3]
                ctx.debug(f"Sample component keys: {sample_keys}")
                if sample_keys:
                    component_sample = json.dumps(raw_file_data['components'][sample_keys[0]], indent=2)[:200]
                    ctx.debug(f"Sample component data: {component_sample}...")
            else:
                ctx.debug("No components found in file data")
        
        # Fetch component data
        ctx.info("Fetching component data")
        raw_components_data = await figma_service.get_file_components(params.fileKey)
        
        # Fetch component set data
        ctx.info("Fetching component set data")
        raw_component_sets_data = await figma_service.get_file_component_sets(params.fileKey)
        
        # Fetch variables data (optional)
        raw_variables_data = {"meta": {"variables": {}, "variableCollections": {}}}
        try:
            ctx.info("Fetching variable data")
            raw_variables_data = await figma_service.get_local_variables(params.fileKey)
        except FigmaAPIError as e:
            ctx.warning(f"Unable to fetch variables (possibly due to permissions): {str(e)}")
            ctx.info("Continuing without variables data")
        
        # Parse the data
        ctx.info("Parsing and transforming Figma data")
        simplified_design = parse_figma_response(
            raw_file_data,
            raw_components_data,
            raw_component_sets_data,
            raw_variables_data
        )
        
        # Log result stats for debugging
        if DEBUG:
            ctx.debug(f"Final components count: {len(simplified_design.components)}")
            if simplified_design.components:
                ctx.debug(f"Sample final component keys: {list(simplified_design.components.keys())[:3]}")
            else:
                ctx.debug("No components in final output!")
        
        # Convert to YAML
        ctx.info("Converting to YAML")
        yaml_output = yaml.dump(
            simplified_design.model_dump(exclude_none=True),
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True
        )
        
        ctx.info("Successfully generated YAML data")
        return yaml_output
        
    except FigmaAPIError as e:
        # Log the error and re-raise as a ToolError
        ctx.error(f"Figma API error: {str(e)}")
        raise ToolError(f"Figma API error: {str(e)}")
    
    except Exception as e:
        # Log the error and re-raise as a ToolError
        ctx.error(f"Error processing Figma data: {str(e)}")
        raise ToolError(f"Error processing Figma data: {str(e)}")


@mcp.tool()
async def download_figma_images(
    params: DownloadFigmaImagesParams,
    ctx: Context
) -> str:
    """
    Download images of specified nodes from a Figma file.
    
    Renders nodes as images and/or downloads image fills, saving them
    to the specified local directory.
    
    Args:
        params: Parameters for downloading images
        ctx: MCP context for logging and state access
        
    Returns:
        Message with results of the download operation
        
    Raises:
        ToolError: If the Figma API key is missing, API requests fail,
                  or there are file system issues
    """
    # Check if Figma API key is set
    if not figma_service:
        raise ToolError("FIGMA_API_KEY environment variable not set")
    
    try:
        # Ensure local path exists
        local_path = Path(params.localPath)
        os.makedirs(local_path, exist_ok=True)
        
        # Format validation
        if params.format not in ["png", "svg", "jpg", "pdf"]:
            raise ToolError(f"Unsupported format: {params.format}. Use png, svg, jpg, or pdf.")
        
        # Separate nodes into direct renders vs image fills
        render_nodes = []
        image_fill_nodes = []
        
        for node in params.nodes:
            if node.imageRef:
                image_fill_nodes.append(node)
            else:
                render_nodes.append(node)
        
        # Process direct renders
        successful_downloads = []
        failed_downloads = []
        
        if render_nodes:
            ctx.info(f"Rendering {len(render_nodes)} nodes as {params.format} images")
            
            # Get image URLs
            node_ids = [node.nodeId for node in render_nodes]
            render_result = await figma_service.get_image_render_urls(
                params.fileKey,
                node_ids,
                params.format,
                params.scale
            )
            
            if "images" not in render_result:
                raise ToolError("Failed to get image URLs from Figma API")
            
            # Download each image
            for node in render_nodes:
                if node.nodeId in render_result["images"]:
                    image_url = render_result["images"][node.nodeId]
                    
                    if not image_url:
                        failed_downloads.append(f"{node.nodeId} (URL not available)")
                        continue
                    
                    try:
                        # Download the image
                        image_data = await figma_service.download_image_data(image_url)
                        
                        # Ensure filename has proper extension
                        filename = node.fileName
                        if not filename.endswith(f".{params.format}"):
                            filename = f"{filename}.{params.format}"
                        
                        # Save the image
                        async with aiofiles.open(local_path / filename, 'wb') as f:
                            await f.write(image_data)
                        
                        successful_downloads.append(filename)
                        
                    except Exception as e:
                        failed_downloads.append(f"{node.fileName}: {str(e)}")
                else:
                    failed_downloads.append(f"{node.nodeId} (not found in API response)")
        
        # Process image fills
        if image_fill_nodes:
            ctx.info(f"Downloading {len(image_fill_nodes)} image fills")
            
            # Get image fill URLs
            fill_result = await figma_service.get_image_fill_source_urls(params.fileKey)
            
            if "meta" not in fill_result or "images" not in fill_result["meta"]:
                raise ToolError("Failed to get image fill URLs from Figma API")
            
            # Download each image fill
            for node in image_fill_nodes:
                if node.imageRef in fill_result["meta"]["images"]:
                    image_url = fill_result["meta"]["images"][node.imageRef]
                    
                    if not image_url:
                        failed_downloads.append(f"{node.imageRef} (URL not available)")
                        continue
                    
                    try:
                        # Download the image
                        image_data = await figma_service.download_image_data(image_url)
                        
                        # Ensure filename has proper extension (fills are typically jpg/png)
                        filename = node.fileName
                        if not (filename.endswith(".jpg") or filename.endswith(".png")):
                            filename = f"{filename}.jpg"  # Default to jpg for image fills
                        
                        # Save the image
                        async with aiofiles.open(local_path / filename, 'wb') as f:
                            await f.write(image_data)
                        
                        successful_downloads.append(filename)
                        
                    except Exception as e:
                        failed_downloads.append(f"{node.fileName}: {str(e)}")
                else:
                    failed_downloads.append(f"{node.imageRef} (not found in API response)")
        
        # Prepare result message
        success_count = len(successful_downloads)
        fail_count = len(failed_downloads)
        
        result_message = f"Downloaded {success_count} of {success_count + fail_count} images to {local_path}."
        
        if successful_downloads:
            result_message += f"\n\nSuccessful downloads:\n" + "\n".join(successful_downloads)
        
        if failed_downloads:
            result_message += f"\n\nFailed downloads:\n" + "\n".join(failed_downloads)
        
        return result_message
        
    except FigmaAPIError as e:
        # Log the error and re-raise as a ToolError
        ctx.error(f"Figma API error: {str(e)}")
        raise ToolError(f"Figma API error: {str(e)}")
    
    except Exception as e:
        # Log the error and re-raise as a ToolError
        ctx.error(f"Error downloading images: {str(e)}")
        raise ToolError(f"Error downloading images: {str(e)}")


# Server run logic
if __name__ == "__main__":
    # Check if Figma API key is set
    if not FIGMA_API_KEY:
        print("ERROR: FIGMA_API_KEY environment variable not set. Set it in .env file.")
        exit(1)
    
    # Use first command-line argument as transport if provided
    import sys
    transport = "stdio"  # Default
    
    if len(sys.argv) > 1:
        transport = sys.argv[1]
    
    if transport == "http":
        # Run with HTTP transport for testing
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        # Run with stdio transport (default)
        mcp.run(transport="stdio") 