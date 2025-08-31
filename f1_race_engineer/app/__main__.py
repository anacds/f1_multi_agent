import os
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentSkill

from app.agent_executor import SupervisorExecutor

host = os.getenv("SUPERVISOR_HOST")
port = int(os.getenv("SUPERVISOR_PORT"))

def create_app():
    card = AgentCard(
        name="Supervisor de Estratégia de Corrida F1",
        description="Agente orquestrador que direciona perguntas sobre pneus ou clima para os especialistas apropriados.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False, pushNotifications=False),
        skills=[
            AgentSkill(
                id="supervisor.route", 
                name="Roteamento de Tarefas", 
                description="Roteia perguntas para agentes de pneus ou clima.",
                tags=["supervisor", "routing", "f1", "strategy"]
            )
        ],
        defaultInputModes=["text"],
        defaultOutputModes=["text"]
    )

    handler = DefaultRequestHandler(
        agent_executor=SupervisorExecutor(),
        task_store=InMemoryTaskStore(),
    )
    app = A2AStarletteApplication(agent_card=card, http_handler=handler)
    return app.build()

def main():
    reload = os.getenv("A2A_RELOAD", "false").lower() in ("true", "1")
    app_string = "app.__main__:create_app"
    
    if reload:
        uvicorn.run(app_string, host=host, port=port, reload=True, factory=True)
    else:
        uvicorn.run(create_app(), host=host, port=port)

if __name__ == "__main__":
    main()