from asyncio import Queue
from langchain.tools import Tool, StructuredTool
from ws_bom_robot_app.llm.models.api import LlmAppTool
from ws_bom_robot_app.llm.tools.tool_manager import ToolManager
from ws_bom_robot_app.llm.providers.llm_manager import LlmInterface

def get_structured_tools(llm: LlmInterface, tools: list[LlmAppTool], callbacks:list, queue: Queue) -> list[StructuredTool]:
  _structured_tools :list[StructuredTool] = []
  for tool in [tool for tool in tools if tool.is_active]:
    if _tool_config := ToolManager._list.get(tool.function_name):
      _tool_instance = ToolManager(llm, tool, callbacks, queue)
      _structured_tool = StructuredTool.from_function(
        coroutine=_tool_instance.get_coroutine(),
        name=tool.function_id if tool.function_id else tool.function_name,
        description=tool.function_description,
        args_schema=_tool_config.model
        #infer_schema=True,
        #parse_docstring=True,
        #error_on_invalid_docstring=True
      )
      _structured_tool.tags = [tool.function_id if tool.function_id else tool.function_name]
      _structured_tools.append(_structured_tool)
  return _structured_tools
