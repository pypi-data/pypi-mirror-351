from openai.types.chat import ChatCompletionToolParam
from typing import List, Dict, Callable, Awaitable, Optional
from .base import BaseAdapter, GramInstanceRequest
from dataclasses import dataclass

@dataclass
class ToolExecutor:
    execute_sync: Callable[[str], str]
    execute_async: Callable[[str], Awaitable[str]]

@dataclass
class OpenAIFunctionCallingTools:
    tools: List[ChatCompletionToolParam]
    functionsMap: Dict[str, ToolExecutor]

class OpenAIAdapter(BaseAdapter):
    def tools(
        self,
        project: str,
        toolset: str,
        environment: Optional[str] = None,
    ) -> OpenAIFunctionCallingTools:
        gram_request = GramInstanceRequest(project=project, toolset=toolset, environment=environment)
        
        base_tools_list = self.base_tools(gram_request)

        tools_property: List[ChatCompletionToolParam] = [
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            )
            for tool in base_tools_list
        ]

        functions_map_property: Dict[str, ToolExecutor] = {}
        for tool in base_tools_list:
            functions_map_property[tool.name] = ToolExecutor(
                execute_sync=tool.execute_sync,
                execute_async=tool.execute
            )

        return OpenAIFunctionCallingTools(
            tools=tools_property,
            functionsMap=functions_map_property,
        )
