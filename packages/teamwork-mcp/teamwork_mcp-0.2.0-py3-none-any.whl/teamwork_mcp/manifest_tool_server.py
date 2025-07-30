import inspect
import importlib
from typing import Any
from pydantic import BaseModel, Field
from mcp.server.fastmcp.tools import Tool
from mcp.server.fastmcp.exceptions import ToolError
from teamwork_mcp import FastMCP, launch_mcp_server_forever
from teamwork_mcp.manifest_tool import tool_manifest_collection, raw_mcp_tool_manifest_collection
from mcp.server.fastmcp.utilities.func_metadata import FuncMetadata, func_metadata

fastmcp = FastMCP("manifest_tool_server")

def get_fast_mcp_server():
    return fastmcp

def add_tool(self, tool) -> Tool:
    """Add a tool to the server."""
    existing = self._tools.get(tool.name)
    if existing:
        if self.warn_on_duplicate_tools:
            raise RuntimeError(f"Tool already exists: {tool.name}")
        return existing
    self._tools[tool.name] = tool
    return tool


class NewFuncMetadata(FuncMetadata):
    arg_model:Any = Field(None, description="The Pydantic model for the arguments of the function.")
    async def call_fn_with_arg_validation(
        self,
        fn,
        fn_is_async: bool,
        arguments_to_validate,
        arguments_to_pass_directly,
    ):
        return fn(self.arg_model(**arguments_to_validate))

def launch_manifest_mcp_server_forever(port=8080):
    # 1. 动态添加标准格式的mcp tool
    for module in raw_mcp_tool_manifest_collection:
        # python 魅力时刻
        importlib.import_module(module)
    # 2. 添加清旭的pydantic协议的tool
    for tool_cls, tool_func in tool_manifest_collection.items():
        fn = tool_func
        func_name = tool_cls().tool_name
        if func_name == "<lambda>":
            raise ValueError("You must provide a name for lambda functions")
        func_doc = tool_cls.model_fields['tool_name'].description
        is_async = inspect.iscoroutinefunction(fn)

        func_arg_metadata = func_metadata(fn, skip_names=[])
        func_arg_metadata = NewFuncMetadata(**func_arg_metadata.model_dump())
        func_arg_metadata.arg_model = tool_cls
        parameters = tool_cls.model_json_schema()
        
        toolx = Tool(fn=fn,
            name=func_name,
            description=func_doc,
            parameters=parameters,
            fn_metadata=func_arg_metadata,
            is_async=is_async,
            context_kwarg=None,
        )
        fastmcp._tool_manager.add_tool = add_tool
        fastmcp._tool_manager.add_tool(fastmcp._tool_manager, toolx)
    launch_mcp_server_forever(fastmcp=fastmcp, host="0.0.0.0", port=port)





