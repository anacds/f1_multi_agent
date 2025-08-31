from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .state import AgentState
from .nlp import NLParser
from .mcp_client import WeatherMCPClient
import json
from datetime import datetime

parser = NLParser()
caller = WeatherMCPClient() 

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um especialista em previsão do tempo na F1. 
            Sua tarefa é traduzir os dados técnicos brutos de uma ferramenta em uma resposta clara, concisa e técnica para um supervisor de corrida. 
            Seja direto e informativo.
            Os dados retornados foram {backend_data}.
            Não invente dados."""
        ),
    ]
)
chain = prompt | llm


async def parse_nl(state: AgentState) -> AgentState:
    raw = state.get("raw_text", "") or ""
    extracted = await parser.parse(raw)
    state["request"] = extracted or {}
    print(state)
    return state

async def call_mcp(state: AgentState) -> AgentState:
    req = state.get("request", {}) or {}
    lat = req.get("lat")
    lon = req.get("lon")
    minutes = req.get("minutes", 30)

    if lat is None or lon is None:
        state["result"] = {"error": "Faltam coordenadas (lat/lon)."}
        return state

    out = await caller.get_minutely_nowcast({
        "lat": float(lat),
        "lon": float(lon),
        "minutes": int(minutes),
    })
    state["result"] = out
    return state

async def synthesize_response(state: AgentState) -> AgentState:
    backend_result = state.get("result", {})

    if "error" in backend_result:
        final_text = f"Erro: {backend_result['error']}"
    else:
        try:
            backend_data_str = json.dumps(
                backend_result,
                indent=2,
                ensure_ascii=False,
                default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o)
            )
            
            response_message = await chain.ainvoke({
                "backend_data": backend_data_str,
                "recursion_limit": 5
            })
            final_text = response_message.content
            
        except Exception as e:
            final_text = f"Erro ao sintetizar a resposta final: {str(e)}"

    state["final_text"] = final_text
    return state