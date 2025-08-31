from typing import Any, Dict, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tyre_agent.models import PredictPaceInput, EstimateDropInput

class NLParser:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        
        llm = ChatOpenAI(model=model_name, temperature=temperature)

        self.llm_with_tools = llm.bind_tools([PredictPaceInput, EstimateDropInput])
        self.prompt = ChatPromptTemplate.from_messages(
            [(
                    "system",
                    """
                    Você é um especialista em Pneus de Fórmula 1 que deve escolher uma ferramenta para responder à pergunta do usuário.

                    SUA MISSÃO:
                    - Analisar a pergunta e decidir entre `PredictPaceInput` ou `EstimateDropInput`.
                    - Sempre escolha exatamente uma ferramenta ou nenhuma, se não houver dados suficientes.

                    REGRAS:
                    1. `PredictPaceInput`: Use esta ferramenta para prever os tempos de volta futuros de um piloto. É útil quando a pergunta é sobre 'qual será o pace', 'ritmo esperado' ou 'tempos das próximas voltas'.
                    2. `EstimateDropInput`: Use esta ferramenta para estimar em quantas voltas um pneu sofrerá uma queda brusca de performance. É útil para perguntas sobre 'até quando o pneu aguenta', 'quando vai cair o rendimento' ou 'previsão de queda'.
                    3. Se a pergunta mencionar as duas coisas (pace + duração), escolha a mais explícita.  
                    Exemplo: "qual o pace e até quando dura?" → prefira `PredictPaceInput` (se houver dados de voltas).
                    4. Preencha todos os argumentos possíveis da ferramenta escolhida a partir do texto do usuário.
                    5. Se informações críticas estiverem ausentes para preencher os argumentos, NÃO chame nenhuma ferramenta e informa quais dados faltaram para completar a ação.
                    6. Nunca invente dados. Use apenas o que foi explicitamente informado pelo usuário.

                    """
                ),
                ("human", "{user_text}"),
            ])

        self.chain = self.prompt | self.llm_with_tools

    async def parse(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        try:
            ai_msg = await self.chain.ainvoke({"user_text": text, "recursion_limit": 5})

            if not ai_msg.tool_calls:
                return None

            tool_call = ai_msg.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name == PredictPaceInput.__name__:
                return "predict_pace_next_laps_tool", tool_args
            
            if tool_name == EstimateDropInput.__name__:
                return "estimate_laps_to_drop_tool", tool_args

            return None 

        except Exception as e:
            print(f"Erro no parsing do LLM: {e}")
            return None