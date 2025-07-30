from typing import Optional, Union, Any, Dict, Callable, Awaitable

from langchain_core.tools import (
    StructuredTool,
    BaseTool as LangchainBaseTool,
)

from gram_ai.base import BaseAdapter, GramInstanceRequest


class GramLangchain(BaseAdapter):
    def _create_async_langchain_adapter(
        self, original_async_execute: Callable[[Union[Dict[str, Any], str]], Awaitable[str]]
    ) -> Callable[..., Awaitable[str]]:
        async def langchain_compatible_coroutine(**kwargs) -> str:
            return await original_async_execute(kwargs)
        return langchain_compatible_coroutine

    def _create_sync_langchain_adapter(
        self, original_sync_execute: Callable[[Union[Dict[str, Any], str]], str]
    ) -> Callable[..., str]:
        def langchain_compatible_func(**kwargs) -> str:
            return original_sync_execute(kwargs)
        return langchain_compatible_func

    def tools(
        self,
        project: str,
        toolset: str,
        environment: Optional[str] = None,
    ) -> list[LangchainBaseTool]:        
        gram_request = GramInstanceRequest(project=project, toolset=toolset, environment=environment)
        
        base_tools_list = self.base_tools(gram_request)

        result: list[LangchainBaseTool] = []
        for base_tool in base_tools_list:
            adapted_coroutine = self._create_async_langchain_adapter(base_tool.execute)
            adapted_func = self._create_sync_langchain_adapter(base_tool.execute_sync)

            result.append(
                StructuredTool(
                    name=base_tool.name,
                    description=base_tool.description,
                    args_schema=base_tool.parameters, # This is Dict[str, Any] JSON schema
                    coroutine=adapted_coroutine,
                    func=adapted_func,
                )
            )
        
        return result

