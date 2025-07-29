"""
Tools package for Unreal MCP Server.

This package contains all the tool modules that provide specific functionality
for interacting with Unreal Engine through the MCP protocol.
"""

from .blueprint_tools import *
from .editor_tools import *
from .node_tools import *
from .project_tools import *
from .umg_tools import *

__all__ = [
    # Blueprint tools
    "create_blueprint_class",
    "compile_blueprint",
    "get_blueprint_info",
    "add_blueprint_component",
    "set_blueprint_variable",
    "get_blueprint_variables",
    "add_blueprint_function",
    "get_blueprint_functions",
    "set_blueprint_parent_class",
    "add_blueprint_interface",
    "remove_blueprint_interface",
    "get_blueprint_interfaces",
    "duplicate_blueprint",
    "delete_blueprint",

    # Editor tools
    "create_actor",
    "delete_actor",
    "get_actor_info",
    "set_actor_location",
    "set_actor_rotation",
    "set_actor_scale",
    "get_actor_transform",
    "add_component_to_actor",
    "remove_component_from_actor",
    "get_actor_components",
    "set_component_property",
    "get_component_property",
    "get_all_actors",
    "get_selected_actors",
    "select_actor",
    "deselect_all_actors",
    "focus_viewport_on_actor",
    "set_viewport_camera_location",
    "get_viewport_camera_location",

    # Node tools
    "add_node_to_blueprint",
    "remove_node_from_blueprint",
    "connect_nodes",
    "disconnect_nodes",
    "get_blueprint_nodes",
    "get_node_info",
    "set_node_property",
    "get_node_property",
    "add_input_pin",
    "add_output_pin",
    "remove_pin",
    "get_node_pins",
    "create_variable_node",
    "create_function_call_node",
    "create_event_node",
    "create_custom_event",
    "add_timeline_node",
    "create_branch_node",
    "create_sequence_node",

    # Project tools
    "get_project_settings",
    "set_project_setting",
    "get_engine_version",
    "get_project_name",

    # UMG tools
    "create_widget_blueprint",
    "add_widget_to_panel",
    "remove_widget_from_panel",
    "set_widget_property",
    "get_widget_property",
    "bind_widget_event",
    "create_animation",
    "play_animation",
    "stop_animation",
    "set_widget_visibility",
    "get_widget_visibility",
    "add_slot_to_panel",
    "set_slot_property",
    "create_user_widget",
    "add_widget_to_viewport",
    "remove_widget_from_viewport",
]