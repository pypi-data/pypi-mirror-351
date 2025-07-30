from dataclasses import dataclass
from typing import Callable, Dict, Optional, Awaitable, Union, Any

from gram_ai.base import BaseAdapter, GramInstanceRequest


@dataclass
class GramFunctionCallingTool:
    name: str
    description: str
    parameters: Dict
    execute: Callable[[Union[Dict[str, Any], str]], str]
    aexecute: Callable[[Union[Dict[str, Any], str]], Awaitable[str]]


class GramFunctionCalling(BaseAdapter):
    def tools(
        self,
        project: str,
        toolset: str,
        environment: Optional[str] = None,
    ) -> list[GramFunctionCallingTool]:
        gram_request = GramInstanceRequest(project=project, toolset=toolset, environment=environment)
        
        base_tools_list = self.base_tools(gram_request)

        adapted_tools_list: list[GramFunctionCallingTool] = []
        for base_tool_item in base_tools_list:
            adapted_tools_list.append(
                GramFunctionCallingTool(
                    name=base_tool_item.name,
                    description=base_tool_item.description,
                    parameters=base_tool_item.parameters,
                    execute=base_tool_item.execute_sync,
                    aexecute=base_tool_item.execute,
                )
            )
        
        return adapted_tools_list

