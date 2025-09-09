import os
import json
from typing import Literal, Union

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from supervisor_agent.state import SupervisorState
from supervisor_agent.clients import A2AClient
from supervisor_agent.tools import supervisor_tools

TYRE_AGENT_URL = os.getenv("TYRE_AGENT_URL")
WEATHER_AGENT_URL = os.getenv("WEATHER_AGENT_URL")
AGENTS = {"tyre_agent": TYRE_AGENT_URL, "weather_agent": WEATHER_AGENT_URL}

print(f"--- SUPERVISOR: URLs carregadas - TYRE: {TYRE_AGENT_URL}, WEATHER: {WEATHER_AGENT_URL} ---")

class GetTelemetryArgs(BaseModel):
    driver_id: str = Field(description="O ID do piloto para buscar a telemetria.")

class CallAgentArgs(BaseModel):
    question: str = Field(description="A pergunta a ser feita para o agente especialista.")

class FinalAnswerArgs(BaseModel):
    pass

class Action(BaseModel):
    tool: Literal["get_telemetry_data", "call_weather_agent", "call_tyre_agent", "finalizar_resposta"]
    args: Union[GetTelemetryArgs, CallAgentArgs, FinalAnswerArgs]

planner_llm = ChatOpenAI(model="gpt-4o", temperature=0.0).with_structured_output(Action, method="function_calling")
planner_prompt = ChatPromptTemplate.from_template(
"""Você é o Engenheiro de Estratégia Chefe da Scuderia Ferrari. 
Sua tarefa é formular uma recomendação para uma pergunta do pit wall sobre o piloto {driver_id}.

PERGUNTA ORIGINAL: {raw_text}

FERRAMENTAS DISPONÍVEIS NESTE PASSO (escolha apenas entre elas): {available_tools}

DADOS JÁ COLETADOS:
- Agent Cards do Tyre Agent (Análise de Pneus) e do Weather Agent (Previsão do Tempo): {agent_cards}
- Skills do Tyre Agent (Análise de Pneus) e do Weather Agent (Previsão do Tempo): {skills_index}
- Telemetria: {telemetry_data}
- Previsão do Tempo: {weather_forecast}
- Análise de Pneus: {tyre_analysis}

SUA TAREFA:
Com base nos dados acima, qual é a próxima ação? Se já tiver informações suficientes, a ação é 'finalizar_resposta'. Senão, escolha a próxima ferramenta e forneça os argumentos necessários conforme o esquema.
Se for chamar os agentes, considere as informações contidas nos Agent Cards e as Skills listadas de cada um.
Não refaça as mesmas perguntas com as mesmas intenções para os agentes. 

FERRAMENTAS DISPONÍVEIS E COMO CONVERSAR COM ELAS:
1. get_telemetry_data(driver_id: str)
2. call_weather_agent(question: str)
3. call_tyre_agent(question: str)
4. finalizar_resposta()

Decida a próxima ação."""
)
planner_chain = planner_prompt | planner_llm

synthesizer_llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
synthesizer_prompt_template = ChatPromptTemplate.from_template(
"""Você é o Engenheiro de Estratégia Chefe da Scuderia Ferrari. 
Formule uma recomendação clara e concisa para o piloto {driver_id}, com base na pergunta original e em todos os dados coletados.

PERGUNTA ORIGINAL: {raw_text}

DADOS COLETADOS:
- Telemetria: {telemetry_data}
- Previsão do Tempo: {weather_forecast}
- Análise de Pneus: {tyre_analysis}

RECOMENDAÇÃO FINAL PARA A EQUIPE:"""
)
synthesizer_chain = synthesizer_prompt_template | synthesizer_llm

async def fetch_agent_cards(state: SupervisorState) -> dict:
    # Verifica se já tem agent cards no estado
    if state.get("agent_cards") and state.get("skills_index"):
        print("--- SUPERVISOR: Agent cards já estão no estado ---")
        return {}
    
    print("--- SUPERVISOR: Buscando Agent Cards... ---")
    agent_cards, skills_index = {}, {}

    for agent_name, base_url in AGENTS.items():
        if not base_url:
            print(f"--- AVISO: URL ausente para {agent_name} ---")
            continue

        try:
            client = A2AClient(agent_url=base_url)
            card = await client.get_agent_card()
            await client.close()

            if not card:
                print(f"--- AVISO: Não consegui obter Agent Card de {agent_name} ---")
                continue

            agent_cards[agent_name] = card

            skill_map = {}
            for skill in card.get("skills", []) or []:
                skill_id = skill.get("id")
                props = []
                for ex in skill.get("examples", []) or []:
                    try:
                        data = json.loads(ex)
                        if isinstance(data, dict):
                            if isinstance(data.get("properties"), dict):
                                props = list(data["properties"].keys()); break
                            payload = data.get("payload")
                            if isinstance(payload, dict):
                                props = list(payload.keys()); break
                    except Exception:
                        pass
                if skill_id:
                    skill_map[skill_id] = {
                        "name": skill.get("name"),
                        "description": skill.get("description"),
                        "properties": props,
                    }
            skills_index[agent_name] = skill_map
        except Exception as e:
            print(f"--- ERRO ao buscar Agent Card de {agent_name}: {e} ---")
            continue
    
    print(f"--- SUPERVISOR: Agent Cards coletados: {list(agent_cards.keys())} ---")
    return {"agent_cards": agent_cards, "skills_index": skills_index}


async def plan_step(state: SupervisorState) -> dict:
    try:
        print("--- SUPERVISOR: Iniciando plan_step ---")
        
        if state.get("final_response"):
            print("--- SUPERVISOR: Já tem resposta final, retornando vazio ---")
            return {}

        state.setdefault("agent_cards", {})
        state.setdefault("skills_index", {})
        state.setdefault("telemetry_data", None)
        state.setdefault("weather_forecast", None)
        state.setdefault("tyre_analysis", None)
        state.setdefault("action_history", [])
        
        print(f"--- SUPERVISOR: Estado atual - agent_cards: {bool(state.get('agent_cards'))}, skills_index: {bool(state.get('skills_index'))} ---")
    except Exception as e:
        print(f"--- ERRO em plan_step: {e} ---")
        return {"error": str(e)}

    needs_telemetry = state.get("telemetry_data") is None
    needs_tyre = state.get("tyre_analysis") is None
    needs_weather = state.get("weather_forecast") is None

    if needs_telemetry:
        driver = (state.get("driver_id") or "hamilton").lower()
        return {"tool_to_call": "get_telemetry_data", "tool_args": {"driver_id": driver}}

    if not needs_tyre and not needs_weather:
        return {"tool_to_call": "finalizar_resposta", "tool_args": {}}

    available_tools = []
    if needs_tyre:    available_tools.append("call_tyre_agent")
    if needs_weather: available_tools.append("call_weather_agent")
    available_tools.append("finalizar_resposta")

    history = state.get("action_history", [])
    history_str = "\n".join(reversed(history[-10:])) if history else "—"

    print("--- SUPERVISOR: Planejando próximo passo... ---")
    response = await planner_chain.ainvoke({
        **state,
        "available_tools": "\n- " + "\n- ".join(available_tools),
        "action_history": history_str,
    })
    tool, args = response.tool, response.args

    if tool not in available_tools:
        if needs_weather:
            print("--- SUPERVISOR: Tool fora da lista. Redirecionando para call_weather_agent ---")
            return {"tool_to_call": "call_weather_agent", "tool_args": {"question": state["raw_text"]}}
        if needs_tyre:
            print("--- SUPERVISOR: Tool fora da lista. Redirecionando para call_tyre_agent ---")
            return {"tool_to_call": "call_tyre_agent", "tool_args": {"question": state["raw_text"]}}
        return {"tool_to_call": "finalizar_resposta", "tool_args": {}}

    print(f"--- SUPERVISOR: Próxima ação decidida: {tool} com args {args} ---")
    return {"tool_to_call": tool, "tool_args": args.dict()}


async def execute_tool(state: SupervisorState) -> dict:
    if state.get("final_response"):
        return {}

    tool_name = state["tool_to_call"]
    tool_args = state["tool_args"]

    if tool_name == "get_telemetry_data":
        driver_id = tool_args.get("driver_id", state.get("driver_id"))
        telemetry = await supervisor_tools.get_telemetry_data(driver_id)
        return {"telemetry_data": telemetry}

    elif tool_name == "call_weather_agent":
        question = tool_args.get("question", state["raw_text"])
        telemetry = state.get("telemetry_data")
        driver_id = state.get("driver_id")

        if telemetry:
            try:
                telemetry_json = json.dumps(telemetry, ensure_ascii=False)
            except Exception:
                telemetry_json = str(telemetry)
            question = f"Piloto: {driver_id}\nPergunta: {question}\n\nTelemetria:\n{telemetry_json}"

        print("PERGUNTA FEITA PARA O WEATHER:")
        print(question)

        client = A2AClient(agent_url=WEATHER_AGENT_URL)
        forecast = await client.send_message(question, state["thread_id"])
        await client.close()
        return {"weather_forecast": forecast}

    elif tool_name == "call_tyre_agent":
        question = tool_args.get("question", state["raw_text"])
        telemetry = state.get("telemetry_data")
        driver_id = state.get("driver_id")

        if telemetry:
            try:
                telemetry_json = json.dumps(telemetry, ensure_ascii=False)
            except Exception:
                telemetry_json = str(telemetry)
            question = f"Piloto: {driver_id}\nPergunta: {question}\n\nTelemetria:\n{telemetry_json}"

        print("PERGUNTA FEITA PARA O TYRE:")
        print(question)

        client = A2AClient(agent_url=TYRE_AGENT_URL)
        analysis = await client.send_message(question, state["thread_id"])
        await client.close()
        return {"tyre_analysis": analysis}

    return {}


async def synthesize_final_response(state: SupervisorState) -> dict:
    if state.get("final_response"):
        return {}

    print("--- SUPERVISOR: Sintetizando resposta final... ---")
    response = await synthesizer_chain.ainvoke(state)
    return {"final_response": response.content}