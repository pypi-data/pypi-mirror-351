**Product Requirements Document: Figma Data MCP Server (Python Edition)**

**1. Introduction & Purpose**

*   **1.1 Product Name:** Figma Data MCP Server (Python Edition)
*   **1.2 Project Goal:** To develop a Model Context Protocol (MCP) server in Python that provides AI coding agents (e.g., Cursor) with rich, structured data from Figma designs. The primary aim is to facilitate the efficient generation and reuse of mobile UI components for Jetpack Compose (Android) and SwiftUI (iOS) by leveraging Figma Components, Variants, and Variables.
*   **1.3 Problem Statement:** Manually translating Figma designs, especially those with hardcoded styles and evolving component structures, into production-ready mobile UI code is time-consuming, error-prone, and leads to inconsistencies. Existing Figma MCP solutions provide a good foundation but need to be tailored for deeper integration with Figma's component and design token (variables) systems to support a robust component library workflow.
*   **1.4 Target Users:**
    *   Mobile Developers (Android/Kotlin, iOS/Swift) within the company.
    *   AI Coding Agents (e.g., Cursor) used by these developers.
*   **1.5 Scope:**
    *   **In Scope:**
        *   Porting core functionality of the existing Node.js `figma-developer-mcp`.
        *   Enhanced extraction and representation of Figma Components, Component Sets, and their Variants.
        *   Comprehensive extraction and representation of Figma Variables (Colors, Numbers/Spacing, Strings, Booleans) used within the design scope.
        *   Clear linking between Figma node styles and Figma Variables in the output.
        *   Outputting resolved styles for elements not driven by variables.
        *   Providing tools to fetch simplified Figma data (for files or specific nodes) and download images.
        *   Output format (YAML) optimized for LLM consumption and code generation for Jetpack Compose and SwiftUI.
        *   Initial support for Figma Personal Access Token authentication.
        *   Operation primarily via STDIO transport for IDE integration.
    *   **Out of Scope (Initially/Future Considerations):**
        *   Figma OAuth authentication (defer for simplicity initially).
        *   Direct interaction with the local codebase (e.g., `componentLibraryPath` tool) - this is considered the AI agent's responsibility.
        *   Real-time updates or webhooks from Figma.
        *   Advanced Figma features not directly related to component structure or design tokens (e.g., prototyping interactions, comments, complex vector network processing beyond basic SVG export).
        *   Support for web frameworks (HTML/CSS/JS).
        *   Dark mode support (as per current company needs; variable extraction should be mode-aware if modes are used, but primary focus is on single-mode value resolution).

**2. Goals & Success Metrics**

*   **2.1 Primary Goals:**
    *   **G1:** Enable AI agents to accurately generate Jetpack Compose and SwiftUI code for Figma designs by providing detailed, structured component and variable information.
    *   **G2:** Facilitate the reuse of existing, already-coded UI components by the AI agent, minimizing redundant code generation.
    *   **G3:** Reduce the manual effort and time required for developers to translate Figma designs into mobile UI code.
    *   **G4:** Improve consistency between Figma designs and the implemented mobile UI components.
    *   **G5:** Encourage and support the team's transition towards a component-based and design-token-driven workflow in Figma.
*   **2.2 Success Metrics:**
    *   **M1:** Reduction in time spent by developers manually coding UI from Figma (Target: >30% reduction for common components after adoption).
    *   **M2:** Increased accuracy of AI-generated code for UI components, requiring fewer manual corrections (Target: >70% of generated code for a standard component being usable with minor tweaks).
    *   **M3:** AI agent successfully identifies and reuses an existing coded component >80% of the time when one with a matching name (from Figma `componentName`) exists in the project.
    *   **M4:** Server successfully processes and provides relevant data for 100% of the team's core Figma components and variable collections (once defined and used in Figma).
    *   **M5:** Positive qualitative feedback from the development team regarding ease of use and impact on workflow.

**3. User Stories & Key Workflows**

*   **US1:** As a Mobile Developer, I want to provide a Figma file/node URL to my AI coding agent so that it can access structured design data (including components, variants, and variables) to generate the corresponding Jetpack Compose UI code, prioritizing reuse of existing coded components.
*   **US2:** As a Mobile Developer, I want to provide a Figma file/node URL to my AI coding agent so that it can access structured design data (including components, variants, and variables) to generate the corresponding SwiftUI UI code, prioritizing reuse of existing coded components.
*   **US3:** As an AI Coding Agent, I need to receive simplified Figma data that clearly distinguishes between main component definitions, component instances, applied variants, and references to design tokens (Figma Variables) so I can make informed decisions about generating new code or reusing existing components.
*   **US4:** As a Mobile Developer, when my Figma designs use variables for colors, spacing, and radii, I want the AI-generated code to use corresponding theme variables/tokens in Kotlin/Swift, not hardcoded values.
*   **US5:** As a Mobile Developer, if a component already exists in my codebase, I want the AI agent to use that existing component and apply the specific variants and overrides from the Figma instance, rather than generating a new component from scratch.
*   **US6:** As a Mobile Developer, I want a tool to download necessary image assets (SVGs, PNGs) referenced in a Figma design to a specified local path.

*   **3.1 Key Workflow: Component Generation & Reuse (Illustrative Example)**

    This workflow demonstrates the primary interaction pattern and the desired outcome of component reuse.

    1.  **Developer Input (to AI Agent like Cursor):**
        *   Developer: "Implement this Figma screen: `https://www.figma.com/file/FILE_KEY/My-App-Designs?node-id=SCREEN_NODE_ID`"
        *   (Alternatively, points to a specific component instance within a screen)

    2.  **AI Agent & MCP Server Interaction:**
        *   The AI Agent (Cursor) identifies the Figma URL.
        *   It calls the `get_figma_data` tool on the "Figma Data MCP Server (Python Edition)" with `fileKey="FILE_KEY"` and `nodeId="SCREEN_NODE_ID"`.
        *   The MCP server fetches data from the Figma API, processes it, and returns a YAML output.

    3.  **MCP Server Output Snippet (for a specific component instance on the screen):**
        ```yaml
        # ... (other parts of SimplifiedDesign YAML) ...
        nodes:
          - id: "101:502" # Figma's internal ID for this instance
            name: "User Profile Retry Button" # Instance name in Figma layers
            type: "INSTANCE"
            layout: layout_ABC123 # Reference to layout in globalVars.styles.layouts
            componentId: "comp_78:901" # ID of the main component definition
            componentName: "PrimaryButton" # Crucial for code mapping and reuse
            appliedVariants:
              State: "Error" # Current variant selection for this instance
              Size: "Large"
            overriddenProperties: # Properties changed specifically on this instance
              text: "Retry Now"
            # ... other style references (potentially to variables) ...
        # ...
        components: # Definition of the main "PrimaryButton" component in the file
          "comp_78:901":
            id: "comp_78:901"
            name: "PrimaryButton" # Name of the main component
            description: "Standard action button for primary user flows."
            variantProperties: # Possible variants for this component
              State: ["Default", "Hover", "Disabled", "Error", "Loading"]
              Size: ["Small", "Medium", "Large"]
        # ...
        figmaVariables: # All relevant Figma Variables used in the fetched scope
          Color/Button/Background/Error: # Example variable path/name
            id: "VariableID:12345" # Figma's internal variable ID
            nameFromFigma: "Color/Button/Background/Error" # Full path name from Figma
            resolvedValue: "#FF3B30" # Resolved color for the current/default mode
            # collectionName: "Color"
        # ...
        globalVars:
          styles:
            layouts:
              layout_ABC123: # Layout definition for the button
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
            # ... other styles like fills, strokes, etc.
        ```

    4.  **AI Agent (LLM) Processing (Prompted for Reuse):**
        *   The LLM receives the YAML. For the `PrimaryButton` instance:
        *   It sees `componentName: "PrimaryButton"`.
        *   **Codebase Search:** The AI agent (Cursor), instructed by its meta-prompt, searches the developer's current project (e.g., Kotlin/Swift files) for an existing Composable/View named `PrimaryButton` (or a close match).

        *   **Scenario A: Existing Component Found (`PrimaryButton.kt` or `PrimaryButton.swift` exists):**
            *   LLM: "I found an existing `PrimaryButton` component. I will use it."
            *   It analyzes the parameters of the existing `PrimaryButton` function/struct.
            *   It maps `appliedVariants` (`State: "Error"`, `Size: "Large"`) and `overriddenProperties` (`text: "Retry Now"`) to the existing component's parameters.
            *   **Generated Code (Conceptual Kotlin - Jetpack Compose):**
                ```kotlin
                PrimaryButton(
                    text = "Retry Now", // From overriddenProperties
                    state = ButtonState.Error, // Mapped from appliedVariants.State
                    size = ButtonSize.Large,   // Mapped from appliedVariants.Size
                    // onClick = { /* TODO: Implement action */ }
                )
                ```
            *   **Generated Code (Conceptual Swift - SwiftUI):**
                ```swift
                PrimaryButton(
                    text: "Retry Now", // From overriddenProperties
                    state: .error,     // Mapped from appliedVariants.State
                    size: .large,      // Mapped from appliedVariants.Size
                    action: { /* TODO: Implement action */ }
                )
                ```

        *   **Scenario B: Existing Component NOT Found:**
            *   LLM: "No existing `PrimaryButton` component found. I will generate a new one."
            *   It refers to the `components["comp_78:901"]` definition in the YAML to understand the `PrimaryButton`'s possible `variantProperties` (like `State` and `Size`).
            *   It uses the style information (which might reference `figmaVariables` like `Color/Button/Background/Error`) from the instance and potentially the default main component structure (if the server provides a simplified version of it) to generate the new component.
            *   **Generated Code (Conceptual Kotlin - Jetpack Compose - New Component):**
                ```kotlin
                // LLM might define these based on variantProperties
                enum class ButtonState { Default, Hover, Disabled, Error, Loading }
                enum class ButtonSize { Small, Medium, Large }

                @Composable
                fun PrimaryButton(
                    text: String,
                    state: ButtonState = ButtonState.Default,
                    size: ButtonSize = ButtonSize.Medium,
                    onClick: () -> Unit
                ) {
                    val backgroundColor = when (state) {
                        // Assuming "Color/Button/Background/Error" variable is mapped to a theme color
                        ButtonState.Error -> MyAppTheme.colors.buttonBackgroundError
                        // ... other states ...
                        else -> MaterialTheme.colorScheme.primary
                    }
                    // ... rest of the Composable implementation ...
                }
                ```
            *   The LLM would then also generate the instance call as in Scenario A, but using the newly defined component.

    5.  **Developer Review & Integration:**
        *   The developer reviews the AI-generated code (either an instantiation of an existing component or a newly generated one).
        *   Integrates it into the application, adding specific logic (e.g., `onClick` handlers).

**4. Functional Requirements (Features)**

*   **FR1: Figma Authentication**
    *   **FR1.1:** Server must authenticate with the Figma API using a Personal Access Token provided via an environment variable (`FIGMA_API_KEY`).
*   **FR2: Data Fetching (`get_figma_data` tool)**
    *   **FR2.1:** Tool must accept a Figma `fileKey` as input.
    *   **FR2.2:** Tool must optionally accept a `nodeId` to fetch data for a specific node or frame.
    *   **FR2.3:** Tool must optionally accept a `depth` parameter to control traversal depth.
    *   **FR2.4:** Tool must fetch the relevant file/node data from the Figma API.
    *   **FR2.5:** Tool must fetch local Figma Variable definitions for the given `fileKey` (and potentially linked published libraries if simple to implement).
    *   **FR2.6:** Tool must fetch local Figma Component and Component Set definitions for the given `fileKey`.
*   **FR3: Data Simplification & Transformation**
    *   **FR3.1:** Raw Figma API responses must be transformed into a "SimplifiedDesign" structure (YAML output).
    *   **FR3.2 (Nodes):** Each node in the output should include: `id`, `name`, `type`, `layout` (reference key to layout properties stored in globalVars), resolved and/or variable-referenced styles (fills, strokes, effects, textStyle, opacity, borderRadius).
    *   **FR3.3 (Component Instances):** For component instances, output must include `componentId` (Figma's main component ID) and `componentName` (human-readable name of the main component).
    *   **FR3.4 (Component Instances - Variants):** Output must include `appliedVariants` (a dictionary of property:value for the instance).
    *   **FR3.5 (Component Instances - Overrides):** Clearly distinguish properties overridden at the instance level (e.g., under an `overriddenProperties` key).
    *   **FR3.6 (Main Components):** The `SimplifiedDesign` output must contain a top-level `components` dictionary detailing all main components within scope, including their `id`, `name`, `description`, and `variantProperties` (a dictionary of variant property names and their possible string values, e.g., `{"State": ["Default", "Error"]}`).
    *   **FR3.7 (Figma Variables):** The `SimplifiedDesign` output must contain a top-level `figmaVariables` dictionary.
        *   This dictionary should be structured, perhaps grouped by collection (e.g., `figmaVariables.Color.App.Primary`).
        *   Each variable entry should include its Figma `id`, full `nameFromFigma` (path), `description` (if any), and its `resolvedValue` (for the primary/default mode). The structure should facilitate mapping to theme tokens.
    *   **FR3.8 (Style-Variable Linking):** When a node's style property (e.g., fill color, padding) is bound to a Figma Variable, the output for that property should clearly reference the variable's name/ID (e.g., `fill: "variable:Color/App/Primary"` or an object `{ "type": "variable", "id": "VariableID:123" }`).
    *   **FR3.9 (Global Styles):** Styles not driven by Figma Variables should be de-duplicated into a `globalVars.styles` section, with nodes referencing these style IDs (e.g., `fill: "style_fill_ABC123"`).
    *   **FR3.9a (Layout Storage):** Layout information should be stored in `globalVars.styles.layouts` with each unique layout having its own key (e.g., `layout_ABC123`). Nodes should reference these layouts using the layout key instead of containing direct layout properties.
    *   **FR3.10 (Children):** Node output should include a `children` list, processed recursively, preserving the hierarchy relevant for UI structure.
*   **FR4: Image Downloading (`download_figma_images` tool)**
    *   **FR4.1:** Tool must accept `fileKey`, a list of nodes to download (each with `nodeId`, `fileName`, optional `imageRef`), `scale`, and `localPath`.
    *   **FR4.2:** Tool must fetch image URLs from Figma (for direct renders of vectors/frames as SVG/PNG and for image fills).
    *   **FR4.3:** Tool must download images to the specified `localPath` with the given `fileName`.
    *   **FR4.4:** Tool must report success or failure, including a list of downloaded files or errors.
*   **FR5: Server Operation**
    *   **FR5.1:** The server must be implemented using Python and the FastMCP library.
    *   **FR5.2:** The server must primarily support STDIO transport for integration with IDEs/agents.
    *   **FR5.3 (Optional):** Basic HTTP transport support for testing/debugging (e.g., with MCP Inspector).
*   **FR6: Output Format**
    *   **FR6.1:** The `get_figma_data` tool must return its output as a YAML string, with consistent and predictable ordering where possible (e.g., sorted keys for dictionaries representing styles or variables if it doesn't obscure meaning).

**5. Non-Functional Requirements**

*   **NFR1: Performance:**
    *   API calls to Figma should be asynchronous to avoid blocking.
    *   Processing of moderately complex Figma files (e.g., a few screens with 50-100 components/variables) should complete within a reasonable timeframe (e.g., < 10-15 seconds, heavily dependent on Figma API latency and complexity of data fetching).
*   **NFR2: Reliability:**
    *   The server should gracefully handle common Figma API errors (e.g., invalid file key, invalid node ID, authentication failure, rate limits) and report them clearly as MCP tool errors.
    *   Robust error handling within the parsing logic, providing informative messages where possible.
*   **NFR3: Maintainability:**
    *   Code should be well-structured (e.g., separate modules for API service, parsing, transformers, utils), documented, and include Python type hints (leveraging Pydantic for data models).
    *   Transformation logic (Figma API to SimplifiedDesign) should be modular and unit-testable.
*   **NFR4: Usability (for the LLM):**
    *   The YAML output structure should be intuitive, self-descriptive, and easy for an LLM to parse and understand for code generation.
    *   Naming conventions in the output should be consistent and as close to Figma's naming as feasible while being clean.

**6. Future Considerations / Potential Enhancements (Out of Scope for V1)**

*   Figma OAuth 2.0 authentication.
*   Support for more advanced Figma features (e.g., specific vector path data if needed beyond SVG export, text content rich text properties like individual word styling).
*   Caching mechanisms for Figma API responses to improve performance and reduce API calls during repeated requests for the same data.
*   Configuration options for the server (e.g., default depth, specific Figma modes to extract values from if multiple modes are used).
*   Support for fetching and referencing styles/variables/components from Published Figma Libraries.
*   CLI arguments for server configuration (e.g., API key, port for HTTP mode) to mirror `npx` behavior.

