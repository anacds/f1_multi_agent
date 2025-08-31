from langgraph.graph import StateGraph, END
from weather_agent.state import AgentState
from weather_agent import nodes
import os

def build_graph(weather_mcp_url: str):
    
    g = StateGraph(AgentState)

    g.add_node("parse_nl", nodes.parse_nl)
    g.add_node("call_mcp", nodes.call_mcp)
    g.add_node("synthesize_response", nodes.synthesize_response)

    g.set_entry_point("parse_nl")
    
    g.add_edge("parse_nl", "call_mcp")
    g.add_edge("call_mcp", "synthesize_response")
    g.add_edge("synthesize_response", END)

    return g.compile()

WEATHER_MCP_URL = os.getenv("WEATHER_MCP_URL")  
graph = build_graph(WEATHER_MCP_URL)