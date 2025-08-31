from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from weather_agent.models import AgentRequest  # seu schema pydantic

class NLParser:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.2):
        llm = ChatOpenAI(model=model_name, temperature=temperature)

        self.llm_with_tools = llm.bind_tools([AgentRequest])
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             """Você extrai comandos de clima de linguagem natural para o schema AgentRequest.

Regras:
- Se o usuário fornecer latitude e longitude (ex.: "lat -23.55 lon -46.63"), use esses valores exatamente (float).
- Se mencionar uma janela de minutos (ex.: "próximos 15 min"), use esse número em `minutes`. Caso não apareça, use `minutes=30`.
- Não invente coordenadas.
- O idioma será pt-BR. Leia padrões como "min", "minutos", "em X min".
- Só chame a ferramenta AgentRequest se tiver lat e lon. Caso contrário, NÃO chame a ferramenta.
"""),
            ("human", "{user_text}")
        ])

        self.chain = self.prompt | self.llm_with_tools

    async def parse(self, text: str) -> Optional[Dict[str, Any]]:
        ai_msg = await self.chain.ainvoke({"user_text": text, "recursion_limit": 5})

        if not getattr(ai_msg, "tool_calls", None):
            return None

        tool_call = ai_msg.tool_calls[0]
        if tool_call["name"] != AgentRequest.__name__:
            return None

        args = tool_call["args"] or {}

        if "minutes" not in args or args["minutes"] is None:
            args["minutes"] = 30

        return args