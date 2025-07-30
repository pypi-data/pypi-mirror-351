from typing import Any, Optional

from agents import FunctionTool, Tool, RunContextWrapper

from gram_ai.base import BaseAdapter, GramInstanceRequest


class GramOpenAIAgents(BaseAdapter):
    def tools(
        self,
        project: str,
        toolset: str,
        environment: Optional[str] = None,
    ) -> list[Tool]:
        gram_request = GramInstanceRequest(project=project, toolset=toolset, environment=environment)
        
        base_tools_list = self.base_tools(gram_request)

        result: list[Tool] = []
        for base_tool in base_tools_list:
            async def invoke_wrapper(_ctx: RunContextWrapper[Any], data: str, current_base_tool=base_tool) -> Any:
                return await current_base_tool.execute(data)

            result.append(
                FunctionTool(
                    name=base_tool.name,
                    description=base_tool.description,
                    params_json_schema=base_tool.parameters,
                    strict_json_schema=False,
                    on_invoke_tool=invoke_wrapper,
                )
            )

        return result
