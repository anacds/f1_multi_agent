from langgraph.graph import StateGraph, END
from supervisor_agent.state import SupervisorState
from supervisor_agent import nodes

print("--- SUPERVISOR: Importando módulo nodes ---")
print(f"--- SUPERVISOR: Funções disponíveis em nodes: {dir(nodes)} ---")

def should_continue(state: SupervisorState) -> str:
    if state.get("final_response"):
        return "end"
    if state.get("tool_to_call") == "finalizar_resposta":
        return "end"
    return "continue"

def needs_agent_cards(state: SupervisorState) -> str:
    """Verifica se precisa buscar agent cards ou se já estão no estado"""
    if state.get("agent_cards") and state.get("skills_index"):
        print("--- SUPERVISOR: Agent cards já estão no estado, pulando busca ---")
        return "continue"
    return "fetch_agent_cards"

builder = StateGraph(SupervisorState)

builder.add_node("fetch_agent_cards", nodes.fetch_agent_cards)
builder.add_node("planner", nodes.plan_step)
builder.add_node("executor", nodes.execute_tool)
builder.add_node("synthesizer", nodes.synthesize_final_response)

builder.set_entry_point("fetch_agent_cards")

builder.add_conditional_edges(
    "fetch_agent_cards",
    needs_agent_cards,
    {
        "continue": "planner", 
        "fetch_agent_cards": "fetch_agent_cards",
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

print("--- SUPERVISOR: Compilando grafo ---")
try:
    graph = builder.compile()
    print("--- SUPERVISOR: Grafo compilado com sucesso ---")
except Exception as e:
    print(f"--- ERRO ao compilar grafo: {e} ---")
    raise