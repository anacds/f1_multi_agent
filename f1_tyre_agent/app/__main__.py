import os
import uvicorn
import json

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentSkill

from app.agent_executor import TyreAgentExecutor
from tyre_agent.models import PredictPaceInput, EstimateDropInput

host = os.getenv("TYRE_AGENT_HOST", "0.0.0.0")
port = int(os.getenv("TYRE_AGENT_PORT", "8891"))

def create_app():

    card = AgentCard(
        protocolVersion="0.1.0",
        name="Tyre Agent",
        description="Agente de estratégia de pneus para Fórmula 1, especializado em projetar os tempos das próximas voltas e queda da performance dos pneus.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[ 
            AgentSkill(
                id=PredictPaceInput.__name__, 
                name="Prever Tempos Das Próximas Voltas",
                description="Projeta os tempos de volta para as próximas voltas.",
                tags=["tyre", "pace"],
                examples=[
                    json.dumps(PredictPaceInput.model_json_schema())
                ]
            ),
            AgentSkill(
                id=EstimateDropInput.__name__,
                name="Estimar Queda de Performance",
                description="Estima em quantas voltas ocorrerá uma queda brusca de performance.",
                tags=["tyre", "degradation"],
                examples=[
                    json.dumps(EstimateDropInput.model_json_schema())
                ]
            )
        ],
    )

    handler = DefaultRequestHandler(
        agent_executor=TyreAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    app = A2AStarletteApplication(agent_card=card, http_handler=handler)
    return app.build()


def main():
    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    main()