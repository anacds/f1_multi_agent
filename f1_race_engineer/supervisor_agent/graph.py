from langgraph.graph import StateGraph, END
from supervisor_agent.state import SupervisorState
from supervisor_agent import nodes

def should_continue(state: SupervisorState) -> str:
    if state.get("final_response"):
        return "end"
    if state.get("tool_to_call") == "finalizar_resposta":
        return "end"
    return "continue"

builder = StateGraph(SupervisorState)

builder.add_node("fetch_agent_cards", nodes.fetch_agent_cards)
builder.add_node("planner", nodes.plan_step)
builder.add_node("executor", nodes.execute_tool)
builder.add_node("synthesizer", nodes.synthesize_final_response)

builder.set_entry_point("fetch_agent_cards")

builder.add_conditional_edges(
    "fetch_agent_cards",
    should_continue,
    {
        "continue": "planner", 
        "end": END             
    }
)


builder.add_edge("planner", "executor")

builder.add_conditional_edges(
    "executor",
    should_continue,
    {
        "continue": "planner",
        "end": "synthesizer"
    }
)

builder.add_edge("synthesizer", END)

graph = builder.compile()