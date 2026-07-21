"""Minimal synthetic-only MCP Tool Call reference adapter.

The public surface is deliberately small and offline. It does not implement an
MCP transport, server, client, runtime, tool invocation, or production profile.
"""

from adapters.mcp.errors import AdapterError, AdapterErrorCode, MappingStatus
from adapters.mcp.mapping import (
    ADAPTER_IMPLEMENTATION_VERSION,
    SYNTHETIC_MAPPING_PROFILE_VERSION,
    SYNTHETIC_PROTOCOL_REVISION,
    SyntheticMCPToolCall,
    ToolCallMappingResult,
)
from adapters.mcp.tool_call_adapter import MCPToolCallAdapter, adapt_tool_call

__all__ = [
    "ADAPTER_IMPLEMENTATION_VERSION",
    "AdapterError",
    "AdapterErrorCode",
    "MCPToolCallAdapter",
    "MappingStatus",
    "SYNTHETIC_MAPPING_PROFILE_VERSION",
    "SYNTHETIC_PROTOCOL_REVISION",
    "SyntheticMCPToolCall",
    "ToolCallMappingResult",
    "adapt_tool_call",
]
