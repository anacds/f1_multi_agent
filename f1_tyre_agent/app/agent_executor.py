from typing import Optional, Any
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils.errors import ServerError, InternalError
from a2a.types import Message, Part
from app.agent import TyreAgent

def _get_text_from_part(part: Any) -> Optional[str]:
    kind = getattr(part, "kind", None) or getattr(part, "type", None)
    text_attr = getattr(part, "text", None)
    if kind == "text" and isinstance(text_attr, str) and text_attr.strip():
        return text_attr

    if isinstance(part, dict):
        k = part.get("kind") or part.get("type")
        t = part.get("text")
        if k == "text" and isinstance(t, str) and t.strip():
            return t

    if hasattr(part, "model_dump"):
        try:
            d = part.model_dump()
            k = d.get("kind") or d.get("type")
            t = d.get("text")
            if k == "text" and isinstance(t, str) and t.strip():
                return t
        except Exception:
            pass

    return None


def _extract_text_and_conversation(context: RequestContext) -> tuple[str, str]:
    msg = getattr(context, "message", None)

    if msg is None:
        raw = getattr(context, "raw_request", None)
        if isinstance(raw, dict):
            params = raw.get("params") or {}
            msg = params.get("message")

    if msg is None:
        raise ValueError("Contexto sem 'message'.")

    conv_id = (
        getattr(msg, "conversation_id", None)
        or getattr(msg, "conversationId", None)
        or (isinstance(msg, dict) and (msg.get("conversation_id") or msg.get("conversationId")))
        or getattr(context, "context_id", None)
        or "default"
    )

    parts = (
        getattr(msg, "parts", None)
        or (isinstance(msg, dict) and msg.get("parts"))
        or []
    )

    if hasattr(parts, "model_dump"):
        try:
            parts = parts.model_dump()
        except Exception:
            pass

    if isinstance(parts, list):
        for p in parts:
            txt = _get_text_from_part(p)
            if txt:
                return txt, conv_id

    direct_text = getattr(msg, "text", None) or (isinstance(msg, dict) and msg.get("text"))
    if isinstance(direct_text, str) and direct_text.strip():
        return direct_text, conv_id

    raise ValueError("Mensagem sem texto")


class TyreAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = TyreAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        try:
            raw_text, conv_id = _extract_text_and_conversation(context)
            final_text = await self.agent.run(raw_text, conv_id)

            response_message = Message(
                messageId=f"{conv_id}-{context.context_id or 'response'}",
                role="agent", 
                conversationId=conv_id,
                parts=[
                    Part(
                        kind="text",
                        text=final_text
                    )
                ]
            )

            await event_queue.enqueue_event(response_message)
        
        except Exception as e:
            raise ServerError(error=InternalError(message=str(e))) from e

    async def cancel(self, context: RequestContext) -> None:
        return