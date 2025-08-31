from typing import Dict, Any
from tyre_agent.graph import graph

class TyreAgent:
    async def run(self, user_text: str, thread_id: str) -> str:
        initial = {"raw_text": user_text, "thread_id": thread_id}
        final_state: Dict[str, Any] = await graph.ainvoke(initial)
        return final_state.get("final_text", "Não consegui gerar uma resposta.")