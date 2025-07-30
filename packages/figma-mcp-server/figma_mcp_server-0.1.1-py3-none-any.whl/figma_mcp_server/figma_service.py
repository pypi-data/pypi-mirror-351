"""
Service for interacting with the Figma API.
"""
from typing import Dict, List, Optional
import httpx
from httpx import AsyncClient, Response


class FigmaAPIError(Exception):
    """Exception raised for Figma API errors."""
    pass


class FigmaService:
    """
    Service for interacting with the Figma API.
    
    Provides methods to fetch file data, components, variables, and images.
    """
    
    BASE_URL = "https://api.figma.com/v1"
    
    def __init__(self, api_key: str):
        """
        Initialize the Figma API service.
        
        Args:
            api_key: Figma Personal Access Token
        """
        if not api_key:
            raise ValueError("Figma API key is required")
        
        self.api_key = api_key
        self.headers = {
            "X-Figma-Token": api_key,
            "Content-Type": "application/json"
        }
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        json_data: Optional[Dict] = None
    ) -> Dict:
        """
        Make a request to the Figma API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON data for POST/PUT requests
            
        Returns:
            The JSON response as a dictionary
            
        Raises:
            FigmaAPIError: If the API returns an error
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        async with AsyncClient() as client:
            try:
                response: Response
                
                if method == "GET":
                    response = await client.get(
                        url, 
                        headers=self.headers, 
                        params=params
                    )
                elif method == "POST":
                    response = await client.post(
                        url, 
                        headers=self.headers, 
                        params=params, 
                        json=json_data
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    error_msg = f"Figma API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        if 'error' in error_data:
                            error_msg = f"Figma API error: {error_data['error']}"
                    except:
                        pass
                    
                    raise FigmaAPIError(f"{error_msg} - {response.text}")
                
                return response.json()
                
            except httpx.RequestError as e:
                raise FigmaAPIError(f"Request to Figma API failed: {str(e)}")
    
    async def get_file_data(
        self, 
        file_key: str, 
        node_ids: Optional[List[str]] = None, 
        depth: Optional[int] = None
    ) -> Dict:
        """
        Get the data for a Figma file.
        
        Args:
            file_key: The key of the Figma file (from the URL)
            node_ids: Optional list of specific node IDs to fetch
            depth: Optional depth limit for node traversal
            
        Returns:
            The file data as a dictionary
        """
        endpoint = f"/files/{file_key}"
        params = {}
        
        if node_ids:
            params["ids"] = ",".join(node_ids)
        
        if depth is not None:
            params["depth"] = depth
        
        return await self._request("GET", endpoint, params)
    
    async def get_file_nodes(
        self, 
        file_key: str, 
        node_ids: List[str], 
        depth: Optional[int] = None
    ) -> Dict:
        """
        Get specific nodes from a Figma file.
        
        Args:
            file_key: The key of the Figma file
            node_ids: List of node IDs to fetch
            depth: Optional depth limit for node traversal
            
        Returns:
            The nodes data as a dictionary
        """
        endpoint = f"/files/{file_key}/nodes"
        params = {"ids": ",".join(node_ids)}
        
        if depth is not None:
            params["depth"] = depth
        
        return await self._request("GET", endpoint, params)
    
    async def get_local_variables(self, file_key: str) -> Dict:
        """
        Get the local variables defined in a Figma file.
        
        Args:
            file_key: The key of the Figma file
            
        Returns:
            The variables data as a dictionary
        """
        endpoint = f"/files/{file_key}/variables/local"
        return await self._request("GET", endpoint)
    
    async def get_file_components(self, file_key: str) -> Dict:
        """
        Get the components defined in a Figma file.
        
        Args:
            file_key: The key of the Figma file
            
        Returns:
            The components data as a dictionary
        """
        endpoint = f"/files/{file_key}/components"
        return await self._request("GET", endpoint)
    
    async def get_file_component_sets(self, file_key: str) -> Dict:
        """
        Get the component sets defined in a Figma file.
        
        Args:
            file_key: The key of the Figma file
            
        Returns:
            The component sets data as a dictionary
        """
        endpoint = f"/files/{file_key}/component_sets"
        return await self._request("GET", endpoint)
    
    async def get_image_render_urls(
        self, 
        file_key: str, 
        node_ids: List[str], 
        format: str = "png", 
        scale: float = 2.0
    ) -> Dict:
        """
        Get URLs for rendered images of specified nodes.
        
        Args:
            file_key: The key of the Figma file
            node_ids: List of node IDs to render
            format: Image format (png, svg, pdf, jpg)
            scale: Scale factor for raster formats
            
        Returns:
            Dictionary with node IDs as keys and image URLs as values
        """
        endpoint = f"/images/{file_key}"
        params = {
            "ids": ",".join(node_ids),
            "format": format,
            "scale": scale
        }
        
        return await self._request("GET", endpoint, params)
    
    async def get_image_fill_source_urls(self, file_key: str) -> Dict:
        """
        Get URLs for image fills in a Figma file.
        
        Args:
            file_key: The key of the Figma file
            
        Returns:
            Dictionary with image refs as keys and image URLs as values
        """
        endpoint = f"/files/{file_key}/images"
        return await self._request("GET", endpoint)
    
    async def download_image_data(self, image_url: str) -> bytes:
        """
        Download the image data from a URL provided by the Figma API.
        
        Args:
            image_url: URL of the image to download
            
        Returns:
            The image data as bytes
            
        Raises:
            FigmaAPIError: If the download fails
        """
        async with AsyncClient() as client:
            try:
                response = await client.get(image_url)
                
                if response.status_code >= 400:
                    raise FigmaAPIError(f"Failed to download image: {response.status_code} - {response.text}")
                
                return response.content
                
            except httpx.RequestError as e:
                raise FigmaAPIError(f"Image download failed: {str(e)}") 