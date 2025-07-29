# Symbiote Creative Labs Unreal Engine 5 MCP Server

[![PyPI version](https://badge.fury.io/py/symbiote-unreal-mcp.svg)](https://badge.fury.io/py/symbiote-unreal-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Attribution

> **This project is based on [chongdashu/unreal-mcp](https://github.com/chongdashu/unreal-mcp), an MIT-licensed Unreal Engine MCP server.**
> We are not forking, but have built our implementation using the current version as a reference and foundation.
> All original copyright and license notices from [chongdashu/unreal-mcp](https://github.com/chongdashu/unreal-mcp) are retained.

A comprehensive Model Context Protocol (MCP) server for Unreal Engine integration, providing powerful automation tools for Blueprint creation, actor manipulation, UMG widget development, and more.

## Differences from [chongdashu/unreal-mcp]

- Refactored for PyPI packaging and modern Python project structure
- Enhanced documentation and examples

## Features

- **Blueprint Management**: Create, compile, and manipulate Blueprint classes
- **Actor Operations**: Spawn, delete, and modify actors in your levels
- **UMG Widget Tools**: Create and manage UMG Widget Blueprints with ease
- **Node Graph Manipulation**: Add and connect Blueprint nodes programmatically
- **Component Management**: Add and configure components on Blueprints and actors
- **Project Settings**: Manage input mappings and project configurations
- **Viewport Control**: Focus viewport, take screenshots, and manage camera positions

## Installation

### From PyPI

```bash
pip install unreal-mcp
```

### From Source

```bash
git clone https://github.com/symbiote-labs/Symbiote_UE5.git
cd unreal-mcp
pip install -e .
```

## Quick Start

### 1. Start the MCP Server

```bash
unreal-mcp
```

Or programmatically:

```python
from unreal_mcp import UnrealMCPServer

server = UnrealMCPServer()
server.run()
```

### 2. Configure Unreal Engine

The server connects to Unreal Engine via TCP socket on port `55557`. Make sure your Unreal Engine instance is configured to accept MCP connections on this port.

### 3. Use with MCP Clients

The server implements the Model Context Protocol and can be used with any MCP-compatible client, such as Claude Desktop or other AI assistants.

## Available Tools

### Blueprint Tools

- `create_blueprint(name, parent_class)` - Create new Blueprint classes
- `compile_blueprint(blueprint_name)` - Compile Blueprint changes
- `add_component_to_blueprint(blueprint_name, component_type, component_name)` - Add components
- `set_blueprint_property(blueprint_name, property_name, property_value)` - Set Blueprint properties

### Actor Management

- `spawn_actor(name, type, location, rotation, scale)` - Create actors in the level
- `delete_actor(name)` - Remove actors
- `get_actors_in_level()` - List all actors in current level
- `set_actor_transform(name, location, rotation, scale)` - Modify actor transforms

### UMG Widget Tools

- `create_umg_widget_blueprint(widget_name, parent_class, path)` - Create UMG Widget Blueprints
- `add_text_block_to_widget(widget_name, text_block_name, text, position, size)` - Add text blocks
- `add_button_to_widget(widget_name, button_name, text, position, size)` - Add buttons
- `bind_widget_event(widget_name, widget_component_name, event_name)` - Bind widget events

### Blueprint Node Management

- `add_blueprint_event_node(blueprint_name, event_type)` - Add event nodes
- `add_blueprint_function_node(blueprint_name, target, function_name)` - Add function nodes
- `connect_blueprint_nodes(blueprint_name, source_node_id, source_pin, target_node_id, target_pin)` - Connect nodes
- `add_blueprint_variable(blueprint_name, variable_name, variable_type)` - Add variables

### Editor Tools

- `focus_viewport(target, location, distance, orientation)` - Focus viewport on objects
- `take_screenshot(filename, show_ui, resolution)` - Capture screenshots
- `import_fbx(file_path, output_path)` - Import FBX files

## Configuration

The server can be configured through environment variables or by modifying the connection settings:

```python
# Default configuration
UNREAL_HOST = "127.0.0.1"
UNREAL_PORT = 55557
```

## Examples

### Creating a Simple Actor Blueprint

```python
# Create a new Blueprint
response = create_blueprint("MyActor", "Actor")

# Add a Static Mesh Component
add_component_to_blueprint(
    "MyActor",
    "StaticMeshComponent",
    "MeshComponent",
    location=[0, 0, 0]
)

# Set the static mesh
set_static_mesh_properties(
    "MyActor",
    "MeshComponent",
    "/Engine/BasicShapes/Cube.Cube"
)

# Compile the Blueprint
compile_blueprint("MyActor")
```

### Creating a UMG Widget

```python
# Create a new Widget Blueprint
create_umg_widget_blueprint("MainMenu", "UserWidget", "/Game/UI")

# Add a button
add_button_to_widget(
    "MainMenu",
    "PlayButton",
    "Play Game",
    position=[100, 100],
    size=[200, 50]
)

# Bind the button click event
bind_widget_event("MainMenu", "PlayButton", "OnClicked", "StartGame")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Portions of the code and design are derived from [chongdashu/unreal-mcp](https://github.com/chongdashu/unreal-mcp), also MIT-licensed.

## Support

- **Documentation**: [GitHub README](https://github.com/symbiote-labs/unreal-mcp#readme)
- **Issues**: [GitHub Issues](https://github.com/symbiote-labs/unreal-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/symbiote-labs/unreal-mcp/discussions)

## Changelog

### v0.1.1
- Documentation updates
### v0.1.0
- Initial release
- Blueprint creation and manipulation tools
- Actor management functionality
- UMG Widget Blueprint tools
- Blueprint node graph manipulation
- Editor tools for viewport and screenshot management
- Project settings management
