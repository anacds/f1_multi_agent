from langgraph.graph import StateGraph, END
from tyre_agent.state import AgentState
from tyre_agent import nodes

builder = StateGraph(AgentState)

builder.add_node("parse_and_call", nodes.parse_and_call_backend)
builder.add_node("synthesize_response", nodes.synthesize_response)
builder.set_entry_point("parse_and_call")
builder.add_edge("parse_and_call", "synthesize_response")
builder.add_edge("synthesize_response", END)

graph = builder.compile()