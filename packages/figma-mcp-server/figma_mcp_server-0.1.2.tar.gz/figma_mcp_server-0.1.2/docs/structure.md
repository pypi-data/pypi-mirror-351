# Figma Data MCP Server - Project Structure

## Directory Structure

```
figma-mcp/
├── docs/                      # Documentation files
│   ├── figma.md               # Figma API details and concepts
│   ├── fastmcp.md             # FastMCP documentation
│   ├── plan.md                # Engineering plan with phases and tasks
│   ├── prd.md                 # Product Requirements Document
│   └── structure.md           # This file - project structure documentation
│
├── figma_mcp_server/          # Main server implementation
│   ├── __init__.py            # Package initialization
│   ├── main.py                # FastMCP server setup and tools
│   ├── models.py              # Pydantic models for data structures
│   ├── figma_service.py       # Figma API client service
│   ├── figma_utils.py         # Utility functions
│   ├── figma_parser.py        # Figma node parsing logic
│   └── figma_transformers.py  # Style and layout transformers
│
├── examples/                  # Example code for using the generated output
│   └── iOS/                   # Example iOS implementation with SwiftUI
│
├── images/                    # Downloaded Figma images
│
├── main.py                    # Root entry point for the server
├── test_client.py             # Client for testing the MCP server
├── test_server.sh             # Script to test the server
├── install_and_run.sh         # Script to install dependencies and run server
├── requirements.txt           # Python dependencies
├── env.example                # Example environment variables
└── README.md                  # Project README
```

## Core Components

### Server Module (`figma_mcp_server/`)

1. **main.py**
   - Configures and initializes the FastMCP server
   - Implements MCP tools (`get_figma_data`, `download_figma_images`)
   - Entry point for the MCP server when run as a module

2. **models.py**
   - Pydantic models for both Figma API responses and simplified design output
   - Defines `SimplifiedDesign`, `SimplifiedNode`, and related structures
   - Handles data validation and serialization

3. **figma_service.py**
   - `FigmaService` class for interacting with the Figma API
   - Methods for fetching file data, components, variables, and images
   - Handles API authentication and error handling

4. **figma_parser.py**
   - Core parsing logic to transform raw Figma API data
   - `parse_figma_node` and `parse_figma_response` functions
   - Processes the document tree and extracts relevant node data

5. **figma_transformers.py**
   - Style and layout transformation functions
   - Processes fills, strokes, effects, layouts, and text styles
   - Handles Figma-specific property transformations to simplified format

6. **figma_utils.py**
   - Utility functions for color conversion, ID generation, etc.
   - Helper methods used across multiple modules

### Root Files

1. **main.py**
   - Top-level entry point that imports and runs the server

2. **test_client.py**
   - Test client for interacting with the MCP server
   - Examples of how to make tool calls

3. **requirements.txt**
   - Lists all Python dependencies:
     - FastMCP (v2.0+)
     - Pydantic
     - HTTPX
     - PyYAML
     - python-dotenv
     - aiofiles

4. **env.example**
   - Template for `.env` file with required environment variables like `FIGMA_API_KEY`

## Data Flow

1. **Input**: Figma file key, node ID, depth parameters
2. **API Fetching**: `FigmaService` retrieves data from Figma API
3. **Parsing**: Raw data transformed via `figma_parser.py` and `figma_transformers.py`
4. **Model Creation**: Data validated and structured using Pydantic models
5. **Output**: Simplified design data returned as YAML

## Key Interfaces

### MCP Tools

1. **get_figma_data**
   - Parameters: `fileKey`, `nodeId`, `depth`
   - Returns: YAML string of simplified design data

2. **download_figma_images**
   - Parameters: `fileKey`, `nodes`, `scale`, `localPath`
   - Returns: Success/failure message with downloaded files list

### Core Data Models

1. **SimplifiedDesign** - Top-level output structure containing:
   - Document metadata (name, lastModified, thumbnailUrl)
   - Nodes tree (recursive SimplifiedNode objects)
   - Components and component sets dictionaries
   - Figma variables and global style variables
