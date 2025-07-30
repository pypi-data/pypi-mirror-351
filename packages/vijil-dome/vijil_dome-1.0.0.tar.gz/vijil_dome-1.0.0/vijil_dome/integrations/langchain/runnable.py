from langchain_core.runnables import Runnable
from vijil_dome.guardrails import Guardrail, GuardrailResult
from typing import Optional, Any, Dict, Union
from langchain_core.runnables.config import RunnableConfig


class GuardrailRunnable(Runnable):
    def __init__(self, guardrail: Guardrail):
        self.guardrail = guardrail
        super().__init__()

    def _handle_result(
        self, guardrail_result: GuardrailResult, query: str
    ) -> Dict[str, Any]:
        result = vars(guardrail_result)
        result["original_query"] = query
        return result

    def invoke(
        self,
        input: Union[str, Dict[str, Any]],
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ):
        query = input if isinstance(input, str) else input.get("query", "")
        guardrail_result = self.guardrail.scan(query)
        return self._handle_result(guardrail_result, query)

    async def ainvoke(
        self,
        input: Union[str, Dict[str, Any]],
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ):
        query = input if isinstance(input, str) else input.get("query", "")
        guardrail_result = await self.guardrail.async_scan(query)
        return self._handle_result(guardrail_result, query)
