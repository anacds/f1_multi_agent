from supervisor_agent.graph import graph as supervisor_graph
from supervisor_agent.state import SupervisorState
from supervisor_agent.nodes import fetch_agent_cards

class SupervisorAgent:
    def __init__(self):
        self._agent_cards = None
        self._skills_index = None
    
    async def _ensure_agent_cards(self):
        if self._agent_cards is None or self._skills_index is None:
            result = await fetch_agent_cards({})
            self._agent_cards = result.get("agent_cards", {})
            self._skills_index = result.get("skills_index", {})
            print("--- SUPERVISOR: Agent cards carregados no cache da instância ---")
    
    async def run(self, user_text: str, thread_id: str) -> str:
        await self._ensure_agent_cards()
        
        initial: SupervisorState = {
            "raw_text": user_text,
            "thread_id": thread_id,
            "driver_id": "hamilton",
            "action_history": [],
            "telemetry_data": None,
            "weather_forecast": None,
            "tyre_analysis": None,
            "agent_cards": self._agent_cards,  
            "skills_index": self._skills_index,  
        }
        final_state = await supervisor_graph.ainvoke(initial)
        return final_state.get("final_response", "Ocorreu um erro no supervisor.")