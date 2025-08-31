import logging
import uuid
from typing import Optional, Any, Dict

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils.errors import ServerError, InternalError
from a2a.types import Message, Part, TextPart

from app.agent import SupervisorAgent

logger = logging.getLogger(__name__)

def _get_text_from_part(part: Any) -> Optional[str]:
    try:
        if isinstance(part, dict):
            if part.get("kind") == "text":
                return part.get("text")
            return None

        content_part = getattr(part, "root", part)
        
        if getattr(content_part, "kind", None) == "text":
            return getattr(content_part, "text", None)
            
    except Exception:
        return None
    
    return None

def _extract_text_and_conversation(context: RequestContext) -> tuple[str, str]:
    msg = getattr(context, "message", None)
    if not msg:
        raise ValueError("Contexto da requisição A2A não contém 'message'.")

    conv_id = (
        getattr(msg, "conversation_id", None)
        or getattr(msg, "conversationId", None)
        or (isinstance(msg, dict) and (msg.get("conversation_id") or msg.get("conversationId")))
        or "default_conversation"
    )

    parts = getattr(msg, "parts", []) or []
    for p in parts:
        txt = _get_text_from_part(p)
        if txt and txt.strip():
            return txt, str(conv_id)

    raise ValueError("A mensagem na requisição A2A não contém uma parte de texto válida.")


class SupervisorExecutor(AgentExecutor):
    def __init__(self):
        self.agent = SupervisorAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        try:
            raw_text, conv_id = _extract_text_and_conversation(context)
            final_text = await self.agent.run(raw_text, conv_id)
            text_content = TextPart(kind="text", text=final_text)
            response_part = Part(root=text_content)

            response_message = Message(
                messageId=f"response-{str(uuid.uuid4())}",
                role="agent",
                conversationId=conv_id,
                parts=[response_part] 
            )

            await event_queue.enqueue_event(response_message)

        except Exception as e:
            logger.exception("Falha no SupervisorExecutor")
            raise ServerError(error=InternalError(message=str(e))) from e

    async def cancel(self, context: RequestContext) -> None:
        return