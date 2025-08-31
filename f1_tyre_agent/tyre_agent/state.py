from typing import Dict, List, Any, Optional, TypedDict

class AgentState(TypedDict, total=False):
    thread_id: str
    raw_text: str
    intent: Optional[str]
    fields: Dict[str, Any]
    tool_to_call: List[str]
    backend_result: Dict[str, Any]
    final_text: str
    traces: List[str]