from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from tyre_agent.state import AgentState
from tyre_agent.nlp import NLParser
from tyre_agent.mcp_client import TyreMCPClient

import json

parser = NLParser(model_name="gpt-4o-mini", temperature=0.7)
mcp = TyreMCPClient()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um especialista em pneus de F1. 
            Sua tarefa é traduzir os dados técnicos brutos de uma ferramenta em uma resposta clara, concisa e técnica para um supervisor de corrida. 
            Seja direto e informativo.
            A ferramenta chamada foi '{tool_name}' e os dados retornados foram {backend_data}.
            Não invente dados."""
        ),
    ]
)
chain = prompt | llm


async def parse_and_call_backend(state: AgentState) -> dict:
    raw_text = state.get("raw_text", "")
    parsed_result = await parser.parse(raw_text)

    if not parsed_result:
        return {
            "backend_result": {"error": "Não consegui identificar uma ação clara ou faltam dados na sua pergunta."},
            "tool_to_call": "no_tool_found"
        }

    tool_name, tool_args = parsed_result
    backend_result = {}
    
    try:
        if tool_name == "predict_pace_next_laps_tool":
            backend_result = await mcp.predict_pace(tool_args)
        elif tool_name == "estimate_laps_to_drop_tool":
            backend_result = await mcp.estimate_drop(tool_args)
        else:
            backend_result = {"error": "Ferramenta desconhecida retornada pelo parser."}
    except Exception as e:
        backend_result = {"error": f"Erro ao chamar o backend: {str(e)}"}
    
    return {
        "backend_result": backend_result,
        "tool_to_call": tool_name
    }

async def synthesize_response(state: AgentState) -> dict:
    backend_result = state.get("backend_result", {})
    tool_name = state.get("tool_to_call", "unknown")

    if "error" in backend_result:
        return {"final_text": f"Erro: {backend_result['error']}"}

    try:
        backend_data_str = json.dumps(backend_result, indent=2, ensure_ascii=False)
        response_message = await chain.ainvoke({
            "tool_name": tool_name,
            "backend_data": backend_data_str,
            "recursion_limit": 5
        })
        
        return {"final_text": response_message.content}
        
    except Exception as e:
        return {"final_text": f"Erro ao sintetizar a resposta final: {str(e)}"}