from typing import Dict, Any, List, Optional, TypedDict

class SupervisorState(TypedDict, total=False):
    raw_text: str
    thread_id: str
    driver_id: Optional[str]
    plan: str
    tool_to_call: str
    tool_args: Dict[str, Any]
    telemetry_data: Dict[str, Any]
    weather_forecast: Dict[str, Any]
    tyre_analysis: Dict[str, Any]
    action_history: List[str]
    final_response: str
    agent_cards: Dict[str, Any]
    skills_index: Dict[str, Dict[str, Any]]