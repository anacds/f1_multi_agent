from supervisor_agent.graph import graph as supervisor_graph
from supervisor_agent.state import SupervisorState

class SupervisorAgent:
    async def run(self, user_text: str, thread_id: str) -> str:
        initial: SupervisorState = {
            "raw_text": user_text,
            "thread_id": thread_id,
            "driver_id": "hamilton",
            "action_history": [],
            "telemetry_data": None,
            "weather_forecast": None,
            "tyre_analysis": None,
            "discovered_schemas": None,
        }
        final_state = await supervisor_graph.ainvoke(initial)
        return final_state.get("final_response", "Ocorreu um erro no supervisor.")