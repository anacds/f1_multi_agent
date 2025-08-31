import os
import json
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentSkill

from app.agent_executor import WeatherExecutor
from weather_agent.models import AgentRequest

host = os.getenv("A2A_HOST")
port = int(os.getenv("A2A_PORT"))

def create_app():
    host = os.getenv("A2A_HOST")
    port = int(os.getenv("A2A_PORT"))

    card = AgentCard(
        protocolVersion="0.3.0",
        name="Weather Agent",
        description="Agente A2A de previsão do tempo para corridas de Fórmula 1.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[
            AgentSkill(
                id=AgentRequest.__name__,
                name="Minutely Nowcast",
                description="Retorna previsão minuto a minuto.",
                tags=["weather", "nowcast"],
                examples=[
                    json.dumps(AgentRequest.model_json_schema())
                ],
            )
        ],
    )

    handler = DefaultRequestHandler(
        agent_executor=WeatherExecutor(),
        task_store=InMemoryTaskStore(),
    )
    app = A2AStarletteApplication(agent_card=card, http_handler=handler)
    return app.build()


def main():
    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    main()