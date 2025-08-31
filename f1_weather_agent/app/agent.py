from typing import Dict, Any, AsyncGenerator
from weather_agent import nodes

class WeatherAgent:
    async def stream(
        self, user_text: str, thread_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executa os nós em sequência, gerenciando o estado manualmente.
        """
        state: Dict[str, Any] = {"raw_text": user_text, "thread_id": thread_id}

        yield {"content": "Analisando sua solicitação...", "is_task_complete": False}
        state = await nodes.parse_nl(state)

        yield {"content": "Consultando o serviço de meteorologia...", "is_task_complete": False}
        state = await nodes.call_mcp(state)

        yield {"content": "Formatando a previsão...", "is_task_complete": False}
        state = await nodes.synthesize_response(state)

        final_text = state.get("final_text", "Erro: O nó final não produziu um texto.")
        
        yield {
            "content": final_text,
            "is_task_complete": True,
        }