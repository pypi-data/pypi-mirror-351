## Figma API: Key Concepts & Endpoints for Component-Driven Development

This document outlines the essential aspects of the Figma REST API relevant for building an MCP server that extracts design data for generating mobile UI component libraries (Jetpack Compose & SwiftUI), with a focus on components, variants, and variables.

**Official API Documentation:** [https://www.figma.com/developers/api](https://www.figma.com/developers/api)

**OpenAPI Specification & TypeScript Types:** [figma/rest-api-spec on GitHub](https://github.com/figma/rest-api-spec) (Useful for understanding response structures)

---

**1. Core Concepts**

*   **File:** The top-level container for a Figma document. It contains pages, components, styles, and variables.
*   **Page (Canvas):** A design surface within a file. A file can have multiple pages.
*   **Node:** The fundamental building block in a Figma file. Everything on a canvas is a node (e.g., Frames, Rectangles, Text, Component Instances, Main Components). Nodes form a tree structure.
    *   **Common Node Properties:** `id` (unique within the file), `name`, `type` (e.g., "FRAME", "TEXT", "COMPONENT", "INSTANCE"), `visible`, `opacity`, `fills`, `strokes`, `effects`, `children`, `absoluteBoundingBox`, etc.
*   **Component (Main Component / Component Definition):** A reusable design element. When you create a component in Figma, it becomes a main component definition.
    *   Can have **Variants**: Different states or versions of a component (e.g., Button states: Default, Hover, Disabled). Variants are defined by component properties.
    *   **Component Properties:** User-defined properties that control the appearance or behavior of a component's variants (e.g., a "State" property with values "Default", "Pressed"; a boolean property "HasIcon").
*   **Component Set:** A special type of node that groups multiple variants of a single component.
*   **Instance:** A copy of a main component that you place in your designs. Instances can have their properties overridden (e.g., text content, specific colors, variant selections).
*   **Variables (Design Tokens):** Reusable values for design properties like colors, numbers (spacing, radii, font sizes), strings, and booleans.
    *   Organized into **Collections** (e.g., "Brand Colors", "Spacing Tokens").
    *   Can have different **Modes** (e.g., "Light Mode", "Dark Mode", though you're not using dark mode initially).
    *   Can be **aliased** (one variable referencing another).
    *   Nodes can have their properties **bound** to variables. This is crucial for our goal.
*   **Styles:** Predefined sets of properties (e.g., color styles, text styles, effect styles) that can be applied to nodes. While powerful, Variables are often preferred for more granular token management. Styles can also be composed of variables.

---

**2. Authentication**

*   **Personal Access Token (PAT):** The primary method for server-to-server API access.
    *   Generated in your Figma account settings.
    *   Grants access to all files the user has access to.
    *   Sent via the `X-Figma-Token` HTTP header.
*   **OAuth2:** Available for applications acting on behalf of other users, but more complex to implement. (Out of scope for V1 for our project).

---

**3. Key API Endpoints & Parameters**

All responses are in JSON format.

*   **`GET /v1/files/:file_key`**
    *   **Purpose:** Retrieves the full document tree and metadata for a given file.
    *   **`file_key`:** The unique identifier for a Figma file (from the URL).
    *   **Query Parameters:**
        *   `version`: (Optional) Get a specific version of the file.
        *   `ids`: (Optional) A comma-separated list of node IDs to return. If specified, only these nodes and their children (and parents up to the root) will be returned.
        *   `depth`: (Optional) An integer specifying the depth of the traversal. `depth=1` returns top-level nodes (pages).
        *   `geometry`: (Optional) Set to `"paths"` to export vector data.
        *   `plugin_data`: (Optional) To include data written by plugins.
        *   `branch_data`: (Optional) To get metadata for file branches.
        *   `variable_data`: (Implicitly included, but check documentation for specifics if variables aren't appearing as expected. The `GET /v1/files/:file_key/variables/local` endpoint is more direct for variables).
    *   **Response Includes:**
        *   `document`: The root node of the file, containing children (pages).
        *   `components`: A dictionary of all local components defined in the file. The key is the component's node ID.
        *   `componentSets`: A dictionary of all local component sets.
        *   `schemaVersion`, `styles`, `name`, `lastModified`, `thumbnailUrl`, etc.
        *   **`styles` object:** A map of style IDs to `Style` objects, which detail properties like fills, strokes, text properties, etc.
        *   **`document.children[page_index].children[...]`**: This is where you traverse to find specific nodes.
        *   **Node Properties:** Within each node, you'll find its type, geometry (`absoluteBoundingBox`), styling properties (`fills`, `strokes`, `effects`, `strokeWeight`, `cornerRadius`), layout properties (`layoutMode`, `primaryAxisAlignItems`, `itemSpacing`, `paddingLeft`, etc.), and for component instances, `componentId` and `componentProperties` (which show applied variant values).
        *   **`boundVariables`:** For properties that are linked to Figma Variables, this field will appear on the property (e.g., on a `fills` object or `fontSize` property) and will map the property name (e.g., "color") to a `VariableAlias` object containing the ID of the bound variable.

*   **`GET /v1/files/:file_key/nodes`**
    *   **Purpose:** Retrieves a specific set of nodes from a file. More targeted than fetching the whole file if you only need specific parts.
    *   **Query Parameters:**
        *   `ids`: (Required) A comma-separated list of node IDs to retrieve.
        *   `depth`, `version`, `geometry`, `plugin_data`, `variable_data` (as above).
    *   **Response Includes:**
        *   `nodes`: A dictionary where keys are the requested node IDs, and values are the corresponding `Node` objects (including their children up to the specified depth).
        *   Also includes `components`, `componentSets`, etc., relevant to the requested nodes.

*   **`GET /v1/files/:file_key/components`**
    *   **Purpose:** Returns a list of all components published from the specified file.
    *   **Response Includes:** A `meta.components` array, each object describing a component (`key`, `file_key`, `node_id`, `name`, `description`, `componentSetId`).

*   **`GET /v1/files/:file_key/component_sets`**
    *   **Purpose:** Returns a list of all component sets published from the specified file.
    *   **Response Includes:** A `meta.component_sets` array.

*   **`GET /v1/files/:file_key/variables/local`**
    *   **Purpose:** Retrieves all local variables defined in the specified file. This is the **primary endpoint for fetching your design tokens**.
    *   **Response Structure:**
        *   `meta`:
            *   `variableCollections`: An object where keys are `VariableCollectionId`s. Each collection object has `id`, `name`, `modes` (an array of `{modeId, name}`), and `defaultModeId`.
            *   `variables`: An object where keys are `VariableId`s. Each variable object has `id`, `name` (e.g., "brand/primary", "spacing/small"), `variableCollectionId`, `resolvedType` (COLOR, FLOAT, STRING, BOOLEAN), and `valuesByMode` (an object where keys are `ModeId`s and values are the actual variable values for that mode, e.g., `{"1:0": {"r":0,"g":0.5,"b":1,"a":1}}` for a color).
    *   **Note:** Accessing variables via the REST API might require an Enterprise plan for the Figma team, and the token needs `file_variables:read` scope if using OAuth. For Personal Access Tokens, this should generally work if your account has access.

*   **`GET /v1/images/:file_key`**
    *   **Purpose:** Renders specified nodes from a file as images (PNG, JPG, SVG, PDF).
    *   **Query Parameters:**
        *   `ids`: (Required) Comma-separated list of node IDs to render.
        *   `format`: (Required) `png`, `jpg`, `svg`, `pdf`.
        *   `scale`: (Optional) Number between 0.01 and 4. Default is 1. For PNGs.
        *   `svg_include_id`: (Optional, boolean) For SVG, whether to include IDs.
        *   `svg_simplify_stroke`: (Optional, boolean) For SVG, whether to simplify strokes.
        *   `use_absolute_bounds`: (Optional, boolean) Use the node's absolute bounding box.
        *   `version`: (Optional) File version.
    *   **Response Includes:**
        *   `images`: An object where keys are node IDs and values are URLs to the rendered images. These URLs are temporary and expire.
        *   `err`: Null if successful, or an error message.

*   **`GET /v1/files/:file_key/images`** (Deprecated but might still be seen)
    *   **Purpose:** Returns image fills referenced in a file. The newer `GET /v1/images/:file_key` is generally preferred for rendering nodes.
    *   **Response Includes:** `meta.images`: An object where keys are image `ref`s (found in `Paint` objects of type `IMAGE`) and values are URLs to the original image files. These URLs are also temporary.

---

**4. Understanding Node Properties for UI Generation**

*   **Layout (AutoLayout):**
    *   `layoutMode`: "NONE", "HORIZONTAL" (row), "VERTICAL" (column).
    *   `primaryAxisSizingMode`, `counterAxisSizingMode`: "FIXED" or "AUTO" (hug contents). For children of AutoLayout frames.
    *   `primaryAxisAlignItems`, `counterAxisAlignItems`: "MIN", "MAX", "CENTER", "SPACE_BETWEEN", "BASELINE".
    *   `paddingLeft`, `paddingRight`, `paddingTop`, `paddingBottom`.
    *   `itemSpacing`: Gap between items in an AutoLayout frame.
    *   `layoutGrow`: For children of AutoLayout frames (0 or 1), similar to flex-grow.
    *   `layoutAlign`: For children of AutoLayout frames, how it aligns in the cross-axis ("STRETCH", "INHERIT", "MIN", "CENTER", "MAX").
    *   `constraints`: For children of non-AutoLayout frames (how they resize/reposition).
*   **Styling:**
    *   `fills`: Array of `Paint` objects. Pay attention to `type` ("SOLID", "GRADIENT_LINEAR", etc.), `color` (RGBA), `opacity`, `imageRef` (for image fills).
    *   `strokes`: Array of `Paint` objects.
    *   `strokeWeight`: Thickness of the stroke.
    *   `strokeAlign`: "INSIDE", "OUTSIDE", "CENTER".
    *   `effects`: Array of `Effect` objects (e.g., "DROP_SHADOW", "LAYER_BLUR") with properties like `radius`, `offset`, `color`.
    *   `cornerRadius`, `rectangleCornerRadii`.
*   **Text:**
    *   `characters`: The text content.
    *   `style` (TypeStyle object): `fontFamily`, `fontWeight`, `fontSize`, `textAlignHorizontal`, `textAlignVertical`, `lineHeightPx`, `letterSpacing`, `textCase`, `textDecoration`.
*   **Components & Variants:**
    *   **Main Component Node (`type: "COMPONENT"` or `"COMPONENT_SET"`):**
        *   `componentPropertyDefinitions`: An object describing the variant properties defined on this component (e.g., `{"State": {"type": "VARIANT", "variantOptions": ["Default", "Pressed"], "defaultValue": "Default"}}`).
    *   **Instance Node (`type: "INSTANCE"`):**
        *   `componentId`: ID of the main component it's an instance of.
        *   `componentProperties`: An object showing the selected variant property values for this instance (e.g., `{"State": {"type": "TEXT", "value": "Pressed"}}`).
        *   Overrides are determined by comparing the instance's properties to its main component's properties.

---

**5. Rate Limiting**

*   The Figma API has rate limits, which are generally applied per user (based on the access token).
*   While specific numbers can change, be mindful of making too many requests in a short period.
*   The documentation mentions that for very large files or image render requests, timeouts (resulting in 500 errors) can occur.
*   If using OAuth, rate limits might apply to the entire application.
*   Implement error handling for `429 Too Many Requests` and consider exponential backoff if needed.

---

**Key Takeaways for Your Project:**

1.  **File & Node Structure:** You'll primarily use `GET /v1/files/:file_key` and potentially `GET /v1/files/:file_key/nodes` to get the design hierarchy.
2.  **Variables are Central:** `GET /v1/files/:file_key/variables/local` is essential for your design token workflow. You'll need to map `boundVariables` in node properties back to these definitions.
3.  **Components & Variants:** The `components` and `componentSets` fields in the file response, along with `componentId` and `componentProperties` on instances, are key to understanding component usage.
4.  **Image Export:** `GET /v1/images/:file_key` will be used for the `download_figma_images` tool.
5.  **Transformation is Key:** The raw JSON is verbose. Your Python parsing logic will be crucial to distill it into the `SimplifiedDesign` structure we've discussed, focusing on linking styles to variables and clearly identifying component usage.

This overview should provide a good foundation for understanding how to interact with the Figma API for your specific goals. The official Figma API documentation will be your best friend for detailed property names and exact response structures.