# Figma Data MCP Server (Python Edition)

Give your AI coding agents (like Cursor) powerful, structured access to your Figma design data, with a deep focus on Components, Variants, and Variables. This Model Context Protocol (MCP) server is implemented in Python using FastMCP and is designed to help generate and reuse mobile UI components for Jetpack Compose (Android) and SwiftUI (iOS).

This project is inspired by and aims to provide a Python-based alternative/enhancement to the [figma-developer-mcp](https://github.com/GLips/Figma-Context-MCP) Node.js server, tailored for a component-driven workflow.

## Features

*   **Rich Figma Data Extraction:** Fetches comprehensive data about your Figma files, including:
    *   Node hierarchy, layout, and styling properties.
    *   **Component Definitions:** Detailed information about main components and their variant properties.
    *   **Component Instances:** Clear identification of main components, applied variants, and local overrides.
    *   **Figma Variables (Design Tokens):** Extracts local variables (colors, numbers for spacing/radii, strings, booleans) and their values.
    *   **Style-to-Variable Linking:** Identifies when node styles are bound to Figma Variables, referencing the variable in the output.
*   **Simplified & Structured Output:** Transforms raw Figma API data into a YAML format optimized for LLM consumption.
*   **MCP Tools:**
    *   `get_figma_data`: Fetches and processes Figma file or node data.
    *   `download_figma_images`: Downloads specified image assets (PNG, SVG) from your Figma designs.
*   **Built with FastMCP:** Leverages the Pythonic and efficient FastMCP library for server implementation.
*   **Mobile Focus:** Designed to aid in the generation of Jetpack Compose (Android) and SwiftUI (iOS) components.

## Why this Server?

While general Figma data extraction is useful, this server specifically aims to:

1.  **Promote Component Reuse:** By providing clear data about `componentName` and `appliedVariants`, it helps AI agents identify and use existing coded components in your mobile projects.
2.  **Embrace Design Tokens:** Deep integration with Figma Variables allows AI to generate code that uses your theme's design tokens instead of hardcoded style values.
3.  **Streamline Mobile UI Development:** Reduce manual effort in translating designs to code and improve consistency between Figma and the final app.

## Installation

### Option 1: Install via pip (Recommended)

```bash
pip install figma-mcp-server
```

After installation, you can run the server using:
```bash
figma-mcp
```

### Option 2: Install and run with uvx (No installation required)

If you have [uvx](https://github.com/astral-sh/uv) installed, you can run the server directly without installing it:

```bash
uvx figma-mcp-server
```

This will automatically download and run the latest version.

### Option 3: Development Installation

For development or if you want to modify the code:

```bash
git clone https://github.com/yourusername/figma-mcp.git
cd figma-mcp
pip install -e .
```

## Getting Started

### Prerequisites

*   Python 3.9+
*   Access to a Figma file and a **Figma Personal Access Token**.
    *   Generate a token from your Figma account settings: `Help and account` > `Account settings` > `Personal access tokens`.

### Configuration

1. **Set up your Figma API key:**
   Create a `.env` file in your working directory:
   ```env
   FIGMA_API_KEY="your_figma_personal_access_token_here"
   ```

2. **Run the server:**
   ```bash
   figma-mcp
   ```

### Command Line Options

The `figma-mcp` command supports various options:

```bash
figma-mcp --help                    # Show all available options
figma-mcp                          # Run with stdio transport (default)
figma-mcp --transport http         # Run with HTTP transport on port 8000
figma-mcp --transport http --port 9000  # Run with HTTP transport on port 9000
figma-mcp --transport sse --port 8080   # Run with SSE transport on port 8080
figma-mcp --env-file custom.env    # Use custom environment file
figma-mcp --debug                  # Enable debug mode
```

**Supported transports:**
- `stdio` - Standard input/output (default, for MCP clients like Cursor)
- `http` - HTTP transport (alias for streamable-http)
- `streamable-http` - HTTP transport with streaming support
- `sse` - Server-Sent Events transport

---

## Quick Start with Scripts (Development)

If you're working with the source code, this project provides convenient scripts for setup, running, and testing:

### 1. Install & Run the Server

Use the provided script to set up your environment and start the server:

```bash
chmod +x install_and_run.sh
./install_and_run.sh [server arguments]
```
- This will:
  - Create a Python virtual environment if needed
  - Install all dependencies
  - Check for your `.env` file (and prompt you to edit it if missing)
  - Start the server (default: stdio mode)
- You can pass arguments to the server, e.g.:
  - `./install_and_run.sh` (default stdio)
  - `./install_and_run.sh http 9000` (HTTP mode on port 9000)

### 2. Test the Server

Use the test script to run the included test client:

```bash
chmod +x test_server.sh
./test_server.sh <tool> <file_key> [node_id]
```
- `<tool>`: `get_data` or `download_images`
- `<file_key>`: Your Figma file key (from the URL)
- `[node_id]`: (Optional) Specific node ID to fetch

**Examples:**
```bash
./test_server.sh get_data abc123
./test_server.sh get_data abc123 45:678
./test_server.sh download_images abc123
```
- The test client will preview YAML output or download images as appropriate.

---

## Manual Installation (Advanced/Optional)

If you prefer to set up manually:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/figma-mcp.git
    cd figma-mcp
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up your environment variables:**
    Create a `.env` file in the root of the project with your Figma Personal Access Token:
    ```env
    # Copy from env.example
    FIGMA_API_KEY="your_figma_personal_access_token_here"
    ```

### Running the Server (Manual)

The server primarily runs in **STDIO mode**, which is expected by clients like Cursor for direct integration.

```bash
python main.py
```

You should see output like:
```
Starting Figma Data MCP Server on STDIO...
```

For testing with tools like the [MCP Inspector](https://github.com/modelcontextprotocol/inspector), you can run it in HTTP mode:
```bash
python main.py http 8000
```

Output:
```
Starting Figma Data MCP Server with streamable-http transport on port 8000
```

### Command-line Arguments

The `main.py` script accepts the following command-line arguments:

- First argument: Transport type (`stdio`, `http`, `streamable-http`, or `sse`). Default is `stdio`.
- Second argument (for HTTP-based transports): Port number. Default is `8000`.

Examples:
```bash
python main.py                     # Run with stdio transport
python main.py http 9000           # Run with streamable-http transport on port 9000
python main.py sse 8080            # Run with SSE transport on port 8080
```

## MCP Client Configuration (Example for Cursor)

If you're using this server with Cursor, you can configure it in the Cursor MCP settings:

### If installed via pip:
```json
{
  "mcpServers": {
    "Figma Data MCP": {
      "command": "figma-mcp",
      "transport": "stdio"
    }
  }
}
```

### If using development setup:
```json
{
  "mcpServers": {
    "Figma Data MCP": {
      "command": "/path/to/your/.venv/bin/python", // Or just "python" if in PATH and venv active
      "args": ["/path/to/your/figma-mcp/main.py"],
      "transport": "stdio"
    }
  }
}
```

Make sure the `command` points to the Python interpreter within your virtual environment if you are using one.

## Tools Overview

*   **`get_figma_data`**:
    *   **Description:** Fetches and simplifies Figma file or node data, returning it as a YAML string. Focuses on component structure, variants, and variable bindings.
    *   **Parameters:**
        *   `fileKey` (string, required): The key of the Figma file.
        *   `nodeId` (string, optional): The ID of a specific node/frame to fetch.
        *   `depth` (integer, optional): Traversal depth for node fetching.
    *   **Returns:** YAML string representing the `SimplifiedDesign`.

*   **`download_figma_images`**:
    *   **Description:** Downloads specified image assets (PNG, SVG) from your Figma designs to a local path.
    *   **Parameters:**
        *   `fileKey` (string, required): The key of the Figma file.
        *   `nodes` (list of objects, required): Each object with `nodeId`, `fileName`, and optional `imageRef`.
        *   `scale` (float, optional, default: 2.0): Export scale for PNGs.
        *   `format` (string, optional, default: "png"): Image format (png, svg, jpg, pdf).
        *   `localPath` (string, required): Absolute local directory path to save images.
    *   **Returns:** String message indicating success or failure and listing downloaded files/errors.

## Project Structure

The code is organized into the following modules:

*   **`main.py`**: Root entry point for the server.
*   **`figma_mcp_server/`**: Main package containing the server implementation.
    *   **`main.py`**: FastMCP server definition and tool implementations.
    *   **`figma_service.py`**: Service for communicating with the Figma API.
    *   **`figma_parser.py`**: Core logic for parsing and transforming Figma API data.
    *   **`figma_transformers.py`**: Functions for transforming specific aspects of Figma data (e.g., fills, strokes, effects).
    *   **`figma_utils.py`**: Utility functions for processing Figma data.
    *   **`models.py`**: Pydantic models for the Figma API responses and our simplified output format.

## Understanding the YAML Output

The `get_figma_data` tool returns a YAML string with the following structure:

```yaml
name: "My Figma File"
lastModified: "2023-06-01T12:00:00Z"
thumbnailUrl: "https://example.com/thumb.png"
nodes:
  - id: "1:23"
    name: "Frame 1"
    type: "FRAME"
    layout: layout_4BPZ57  # Reference to layout in globalVars
    # ... other node properties ...
    children:
      - id: "1:24"
        name: "Button"
        type: "INSTANCE"  # This is a component instance
        layout: layout_0HZDJR
        componentId: "comp123"
        componentName: "PrimaryButton"  # Useful for code reuse!
        appliedVariants:  # Current variant selections for this instance
          State: "Default"  # Property: value pairs
          Size: "Large"
        # ... other properties ...

components:  # Definitions of all components referenced by instances
  comp123:
    id: "comp123"
    name: "PrimaryButton"
    description: "Main action button"
    variantProperties:  # All possible variant properties for this component
      State: ["Default", "Pressed", "Disabled"]
      Size: ["Small", "Medium", "Large"]

figmaVariables:
  "Color/Primary":
    id: "var123"
    nameFromFigma: "Color/Primary"
    resolvedValue: "#0066FF"
    collectionName: "Color"

globalVars:
  styles:
    layouts:
      layout_4BPZ57:  # Layout definition for non-auto layout nodes
        mode: none
        sizing:
          horizontal: fixed
          vertical: fixed
      layout_0HZDJR:  # Layout definition for auto-layout nodes
        mode: row
        alignment:
          primaryAxis: center
          counterAxis: center
        padding: 
          top: 8
          right: 16
          bottom: 8
          left: 16
        gap: 4
        sizing:
          horizontal: fixed
          vertical: fixed
    fills:
      # De-duplicated fill styles from the design
      # ...
    strokes:
      # De-duplicated stroke styles
      # ...
    textStyles:
      # De-duplicated text styles
      # ...
  definitions:
    # Actual style definitions
    # ...
```

This structure is specifically designed to make it easy for LLMs to:
1. Recognize component instances and their variants
2. Map Figma components to existing code components
3. Understand layout information through references to definitions in `globalVars.styles`
4. Access shared styles in a de-duplicated format for design token integration

### Component Structure

The component-related information follows this pattern:

1. **Component Instances in Nodes:** When a node is a component instance (`type: "INSTANCE"`), it includes:
   - `componentId`: The unique ID of the main component definition
   - `componentName`: The name of the main component (crucial for code mapping)
   - `appliedVariants`: Current variant selections (property-value pairs)
   - `overriddenProperties`: Any properties overridden at the instance level

2. **Component Definitions:** The `components` section contains definitions for all components used in instances:
   - Each component has an `id`, `name`, and optional `description`
   - `variantProperties` lists all possible variant properties and their possible values
   - These properties are extracted from component names when possible (following Figma naming conventions)

This structure enables AI coding agents to identify when a component from your design matches an existing coded component in your codebase, allowing for accurate reuse rather than regeneration.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.