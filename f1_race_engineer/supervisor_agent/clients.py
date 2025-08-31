import httpx
from typing import Dict, Any, Optional
from uuid import uuid4

from a2a.client import A2ACardResolver, A2AClient as LibA2AClient
from a2a.types import AgentCard, MessageSendParams, SendMessageRequest
from a2a.utils.constants import EXTENDED_AGENT_CARD_PATH

class A2AClient:
    def __init__(self, agent_url: str, timeout: float = 30.0):
        if not agent_url:
            raise ValueError("A URL do agente não pode ser vazia.")
        self.base_url = agent_url.rstrip("/")
        self.httpx = httpx.AsyncClient(timeout=timeout)
        self._agent_card: Optional[AgentCard] = None
        self._a2a_client: Optional[LibA2AClient] = None

    async def _ensure_client(self) -> None:
        if self._a2a_client:
            return

        resolver = A2ACardResolver(httpx_client=self.httpx, base_url=self.base_url)
        card = await resolver.get_agent_card()
        if getattr(card, "supports_authenticated_extended_card", False):
            try:
                card = await resolver.get_agent_card(
                    relative_card_path=EXTENDED_AGENT_CARD_PATH,
                    http_kwargs={"headers": {"Authorization": "Bearer dummy-token"}},
                )
            except Exception:
                pass

        self._agent_card = card
        self._a2a_client = LibA2AClient(httpx_client=self.httpx, agent_card=card)

    async def get_agent_card(self) -> Optional[Dict[str, Any]]:
        try:
            await self._ensure_client()
            return self._agent_card.model_dump(exclude_none=True) if self._agent_card else None
        except Exception as e:
            print(f"Erro ao buscar Agent Card de {self.base_url}: {e}")
            return None

    async def send_message(self, text: str, conversation_id: str) -> str:
        await self._ensure_client()
        assert self._a2a_client is not None

        params_dict: Dict[str, Any] = {
            "message": {
                "role": "user",
                "messageId": uuid4().hex,
                "conversationId": conversation_id,
                "parts": [{"kind": "text", "text": text}],
            }
        }

        try:
            request = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**params_dict))
            resp = await self._a2a_client.send_message(request)
            data = resp.model_dump(mode="json", exclude_none=True)

            print("Especialista respondeu:")
            print(data)

            result = data.get("result") or {}
            status = result.get("status") or {}
            message = status.get("message") or {}
            parts = message.get("parts") or []

            for part in parts:
                if part.get("kind") == "text":
                    return part.get("text", "Resposta vazia do agente.")

            return "Formato de resposta inesperado do agente especialista."

        except httpx.HTTPStatusError as e:
            return f"Erro de comunicação com o agente em {self.base_url}: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"Erro inesperado ao chamar o agente: {str(e)}"

    async def close(self):
        await self.httpx.aclose()