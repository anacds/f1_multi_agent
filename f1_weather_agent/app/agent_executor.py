import logging
from typing import Dict

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, UnsupportedOperationError, InternalError
from a2a.utils.errors import ServerError

from app.agent import WeatherAgent

logger = logging.getLogger(__name__)


def _extract_user_text(context: RequestContext) -> str:
    msg = getattr(context, "message", None)
    if not msg:
        return ""
    parts = getattr(msg, "parts", None) or []

    texts = []
    for p in parts:
        try:
            if isinstance(p, dict):
                kind = p.get("kind") or p.get("type")
                if kind == "text":
                    t = p.get("text") or ""
                    if t:
                        texts.append(t)
                    continue

            node = getattr(p, "root", p) 
            kind = getattr(node, "kind", None) or getattr(node, "type", None)
            if kind == "text":
                t = getattr(node, "text", "") or ""
                if t:
                    texts.append(t)
        except Exception:
            continue

    return "\n".join(texts).strip()


def _text_part(text: str) -> Dict[str, str]:
    return {"kind": "text", "text": text}

class WeatherExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = WeatherAgent()

    async def execute(self, context: RequestContext, event_queue) -> None:
        if not context.task_id or not context.context_id or not context.message:
            raise ValueError("Contexto A2A incompleto.")

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        
        try:
            if not context.current_task:
                await updater.submit()
            await updater.start_work()

            raw_text = _extract_user_text(context)
            final_message_text = "Não foi possível obter uma resposta final."

            async for item in self.agent.stream(raw_text, context.context_id):
                part = _text_part(item["content"])

                if item.get("is_task_complete"):
                    final_message_text = item["content"]
                    break

                await updater.update_status(
                    TaskState.working,
                    message=updater.new_agent_message([part]),
                )
            
            final_message = updater.new_agent_message([_text_part(final_message_text)])
            await updater.update_status(TaskState.completed, message=final_message)

        except Exception as e:
            logger.exception("Falha no WeatherExecutor")
            error_message = updater.new_agent_message([_text_part(f"Erro interno: {e}")])
            await updater.update_status(TaskState.failed, message=error_message)
            raise ServerError(error=InternalError(message=str(e))) from e

    async def cancel(self, *_):
        raise ServerError(error=UnsupportedOperationError("N/A"))