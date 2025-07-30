**Engineering Plan: Figma Data MCP Server (Python Edition)**

**Project Goal:** Develop a Python FastMCP server to provide AI coding agents with structured Figma design data, emphasizing components, variants, and variables, to facilitate efficient generation and reuse of Jetpack Compose and SwiftUI UI components.

**Core Technologies:** Python, FastMCP, Pydantic, HTTPX, PyYAML, AIOFiles.

---

**Phase 1: Foundation & Figma API Service**

*   **Objective:** Establish the basic project structure and implement a service to interact with the Figma API.
*   **Modules to Create/Update:**
    *   `figma_mcp_server/` (Root project directory)
    *   `figma_mcp_server/main.py` (Initial FastMCP server setup)
    *   `figma_mcp_server/figma_service.py`
    *   `figma_mcp_server/models.py` (Initial Pydantic models for API responses)
    *   `.env` (for `FIGMA_API_KEY`)
    *   `requirements.txt` or `pyproject.toml` (for dependencies)

*   **Tasks:**
    1.  **[P0] Project Setup:**
        *   Create the project directory structure.
        *   Set up a Python virtual environment.
        *   Install initial dependencies: `fastmcp`, `httpx`, `python-dotenv`, `pydantic`, `pyyaml`.
    2.  **[P0] Basic `main.py`:**
        *   Create a minimal `FastMCP` server instance.
        *   Implement loading `FIGMA_API_KEY` from `.env`.
        *   Add a basic `if __name__ == "__main__": mcp.run(transport="stdio")` block.
    3.  **[P0] `figma_service.py` - `FigmaService` Class:**
        *   Define the `FigmaService` class.
        *   Constructor: Accepts `api_key: str`.
        *   Private `async def _request(self, method: str, endpoint: str, params: Optional[dict] = None, json_data: Optional[dict] = None) -> dict:`
            *   Uses `httpx.AsyncClient()`.
            *   Sets `X-Figma-Token` header.
            *   Handles basic error checking (HTTP status codes) and raises exceptions.
    4.  **[P0] `figma_service.py` - Core Data Fetching Methods:**
        *   `async def get_file_data(self, file_key: str, node_ids: Optional[List[str]] = None, depth: Optional[int] = None) -> dict:`
            *   Calls `GET /v1/files/:file_key`.
            *   Constructs query parameters for `ids` and `depth` if provided.
        *   `async def get_local_variables(self, file_key: str) -> dict:`
            *   Calls `GET /v1/files/:file_key/variables/local`.
        *   `async def get_file_components(self, file_key: str) -> dict:`
            *   Calls `GET /v1/files/:file_key/components`.
        *   `async def get_file_component_sets(self, file_key: str) -> dict:`
            *   Calls `GET /v1/files/:file_key/component_sets`.
    5.  **[P1] `models.py` - Initial Pydantic Models (Figma API Partial Structures):**
        *   Define Pydantic models for the *expected structure* of responses from the Figma API methods created in Task 1.4 (e.g., `FigmaFileResponse`, `FigmaVariablesResponse`, `FigmaNode`). This helps with type validation of API responses. Start with key fields only and expand as needed.
    6.  **[P1] Unit Tests for `FigmaService`:**
        *   Use `unittest.mock` or `pytest-mock` to mock `httpx.AsyncClient` responses.
        *   Test successful API calls and basic error handling.

---

**Phase 2: Core Data Parsing & Simplification Logic**

*   **Objective:** Implement the logic to transform raw Figma API data into the `SimplifiedDesign` structure, focusing on nodes, components, and basic styles (without variable linking yet).
*   **Modules to Create/Update:**
    *   `figma_mcp_server/models.py` (Define `SimplifiedNode`, `SimplifiedDesign`, `BoundingBox`, `SimplifiedLayout`, `SimplifiedEffect`, `SimplifiedTextStyle`, etc. Pydantic models for our target output structure)
    *   `figma_mcp_server/figma_utils.py`
    *   `figma_mcp_server/figma_transformers.py`
    *   `figma_mcp_server/figma_parser.py`

*   **Tasks:**
    1.  **[P0] `models.py` - Define `SimplifiedDesign` Pydantic Models:**
        *   Implement Pydantic models for all elements of the target `SimplifiedDesign` YAML structure (e.g., `SimplifiedNode`, `BoundingBox`, `SimplifiedLayout`, `SimplifiedTextStyle`, `SimplifiedFill`, `SimplifiedEffect`, `MainComponentDefinition`, `AppliedVariantInfo`, `SimplifiedDesign` itself).
        *   The `SimplifiedDesign` model should include fields for `name`, `lastModified`, `thumbnailUrl`, `nodes: List[SimplifiedNode]`, `components: Dict[str, MainComponentDefinition]`, `componentSets: Dict[str, Any]`, `figmaVariables: Dict[str, Any]` (initially empty/basic), `globalVars: Dict[str, Any]`.
    2.  **[P0] `figma_utils.py` - Utility Functions:**
        *   Port essential utility functions from the Node.js version (e.g., `format_rgba_color`, `convert_figma_color_to_hex_opacity`, `generate_var_id`, `generate_css_shorthand`, `is_visible`).
        *   Add unit tests for these utilities.
    3.  **[P1] `figma_transformers.py` - Style & Layout Transformers:**
        *   Implement initial versions of:
            *   `build_simplified_strokes(node_data: dict) -> dict`
            *   `build_simplified_effects(node_data: dict) -> dict`
            *   `build_simplified_layout(node_data: dict, parent_node_data: Optional[dict]) -> dict` (This will be complex and iterative).
        *   Focus on extracting direct style values first.
        *   Add unit tests for these transformers with mock Figma node data.
    4.  **[P0] `figma_parser.py` - Core Parsing Logic:**
        *   Define `parse_figma_node(raw_node_data: dict, global_vars: dict, components_map: dict, component_sets_map: dict, parent_node_data: Optional[dict]) -> Optional[SimplifiedNode]:`
            *   Handles basic node properties: `id`, `name`, `type`, `boundingBox`.
            *   Integrates calls to `build_simplified_strokes`, `build_simplified_effects`, `build_simplified_layout`.
            *   Handles `fills` and `textStyle` properties (initially just extracting raw values).
            *   Identifies component instances (`type: "INSTANCE"`) and extracts `componentId`. It should look up the `componentName` from the `components_map`.
            *   Recursively calls itself for `children`.
        *   Define `parse_figma_response(raw_file_data: dict, raw_components_data: dict, raw_component_sets_data: dict, raw_variables_data: dict) -> SimplifiedDesign:`
            *   Initializes `global_vars` (for de-duplicating styles not yet linked to variables).
            *   Populates `SimplifiedDesign.name`, `lastModified`, `thumbnailUrl`.
            *   Processes `raw_components_data` and `raw_component_sets_data` to populate `SimplifiedDesign.components` (with `MainComponentDefinition` including `name`, `id`, `description`, `variantProperties`) and `SimplifiedDesign.componentSets`.
            *   Iterates through the document tree in `raw_file_data` calling `parse_figma_node`.
    5.  **[P1] Style De-duplication (`globalVars.styles`):**
        *   In `parse_figma_node`, when a style (fill, stroke, effect, layout, textStyle) is processed and *not yet linked to a Figma Variable*, generate a unique ID for it (e.g., `fill_XYZ123`), store the style definition in `global_vars.styles`, and put the ID reference on the `SimplifiedNode`.

---

**Phase 3: Integrating Figma Variables**

*   **Objective:** Enhance the parsing logic to recognize and represent Figma Variables, and link node styles to these variables.
*   **Modules to Create/Update:**
    *   `figma_mcp_server/models.py` (Update `SimplifiedDesign` and style-related models to support variable references)
    *   `figma_mcp_server/figma_parser.py`
    *   `figma_mcp_server/figma_utils.py` (Potentially for variable name/path manipulation)

*   **Tasks:**
    1.  **[P0] `models.py` - Update Pydantic Models for Variable References:**
        *   Modify `SimplifiedFill`, `SimplifiedLayout.padding/gap/dimensions`, `SimplifiedTextStyle.fontSize`, etc., to allow `Union[ActualValueType, StyleReference]`, where `StyleReference` is a string like `variable:path/to/variable`.
        *   Define Pydantic models for the `figmaVariables` section within `SimplifiedDesign` (e.g., `FigmaVariableOutput`, `FigmaVariableCollectionOutput`).
    2.  **[P0] `figma_parser.py` - Process Figma Variables:**
        *   In `parse_figma_response`, process the `raw_variables_data` (from `FigmaService.get_local_variables`).
        *   Populate the `SimplifiedDesign.figmaVariables` field with a structured representation of these variables (e.g., grouped by collection, including `id`, full `nameFromFigma`, `resolvedValue` for the default mode, `description`).
    3.  **[P1] `figma_parser.py` - Link Node Styles to Variables:**
        *   Modify `parse_figma_node` (and style transformers in `figma_transformers.py`):
            *   When processing style properties (fills, strokes, itemSpacing, padding, fontSize, etc.), check the `boundVariables` field from the raw Figma node data.
            *   If a property is bound to a variable, the corresponding field in `SimplifiedNode` should store the variable reference (e.g., `fill: "variable:Color/App/Primary"`). The resolved value can also be stored for convenience or fallback.
            *   If not bound to a variable, continue using the `globalVars.styles` de-duplication from Phase 2.
    4.  **[P1] Unit Tests for Variable Parsing and Linking:**
        *   Test parsing of variable definitions.
        *   Test that node styles correctly reference variables when bindings exist.
        *   Test fallback to `globalVars.styles` when no variable binding.

---

**Phase 4: Implementing MCP Tools**

*   **Objective:** Expose the Figma data processing logic as FastMCP tools.
*   **Modules to Create/Update:**
    *   `figma_mcp_server/main.py`

*   **Tasks:**
    1.  **[P0] `main.py` - `get_figma_data` Tool:**
        *   Define the `@mcp.tool() async def get_figma_data(...)` function.
        *   Use Pydantic `Field` with `Annotated` for parameter descriptions (`fileKey`, `nodeId`, `depth`).
        *   Inject `Context` for logging and accessing `FigmaService` (store `FigmaService` instance on `mcp.state.figma_service`).
        *   Call `FigmaService` methods to get raw file, components, component sets, and variables data.
        *   Call `parse_figma_response` to get the `SimplifiedDesign` Pydantic model/dict.
        *   Serialize the `SimplifiedDesign` object to YAML using `PyYAML`.
        *   Return the YAML string.
        *   Implement error handling (log errors with `ctx.error`, potentially raise `ToolError`).
    2.  **[P1] `figma_service.py` - Image Fetching Logic:**
        *   `async def get_image_render_urls(self, file_key: str, node_ids: List[str], format: str, scale: Optional[float]) -> dict:`
            *   Calls `GET /v1/images/:file_key`.
        *   `async def get_image_fill_source_urls(self, file_key: str) -> dict:` (This might need careful mapping from `imageRef` to a URL if the old endpoint is fully deprecated or if we need to handle it differently). The original node.js version uses `GET /files/:file_key/images` for fills.
        *   `async def download_image_data(self, image_url: str) -> bytes:` (fetches raw image bytes).
    3.  **[P1] `main.py` - `download_figma_images` Tool:**
        *   Define `@mcp.tool() async def download_figma_images(...)`.
        *   Parameters: `fileKey`, `nodes: List[Dict[str, Any]]` (each dict with `nodeId`, `fileName`, optional `imageRef`), `scale`, `localPath`.
        *   Logic:
            *   Separate nodes into those needing direct render vs. image fill.
            *   Call `FigmaService.get_image_render_urls` for direct renders.
            *   Call `FigmaService.get_image_fill_source_urls` to get a map of `imageRef` to URL, then find URLs for nodes with `imageRef`.
            *   For each image URL obtained:
                *   Fetch image data using `FigmaService.download_image_data`.
                *   Save image bytes to `localPath/fileName` using `aiofiles`.
            *   Return a success/failure message with a list of downloaded files/errors.
        *   Use `os.makedirs(localPath, exist_ok=True)`.
    4.  **[P1] Integration Testing with FastMCP Client:**
        *   Write simple Python scripts using `fastmcp.Client` to call the tools with a test Figma file key and verify the output structure (or image downloads).
        *   Use `pytest` for these tests.

---

**Phase 5: Refinement, Logging, and Finalization**

*   **Objective:** Polish the server, improve logging, and ensure robustness.
*   **Modules to Create/Update:**
    *   All modules, especially `main.py`, `figma_service.py`, `figma_parser.py`.

*   **Tasks:**
    1.  **[P1] Comprehensive Logging:**
        *   Add detailed logging using `ctx.info`, `ctx.warning`, `ctx.error` within tools.
        *   Log key steps in `FigmaService` and `figma_parser`.
        *   Ensure errors from Figma API are logged with details.
    2.  **[P1] Error Handling Review:**
        *   Ensure all potential failure points (API calls, parsing, file I/O) are handled gracefully.
        *   Use `ToolError` for errors that should be clearly communicated to the LLM client.
    3.  **[P2] Output Validation (YAML):**
        *   Manually inspect YAML output for key components from your test Figma file.
        *   Ensure it aligns with the `SimplifiedDesign` Pydantic models and the needs of the LLM.
    4.  **[P2] Code Cleanup & Documentation:**
        *   Add docstrings to all functions and classes.
        *   Refactor code for clarity and efficiency.
    5.  **[P2] README Update:**
        *   Document how to set up and run the Python server.
        *   Explain environment variable requirements.
        *   Provide example MCP client configuration (e.g., for Cursor if it supports custom Python commands, or how to run via `python main.py` for stdio).

---

**Priority Legend:**

*   **[P0]**: Must-have for basic functionality / foundational.
*   **[P1]**: Important for core features and robustness.
*   **[P2]**: Refinements, nice-to-haves for improved usability/maintainability.

