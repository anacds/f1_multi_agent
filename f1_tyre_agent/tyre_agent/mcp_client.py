import os
import uuid
from typing import Optional, Dict, Any
from fastmcp import Client 

TYRE_MCP_URL = os.getenv("TYRE_MCP_URL")

class TyreMCPClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 15.0):
        self.base_url = base_url or TYRE_MCP_URL
        if not self.base_url:
            raise RuntimeError("TYRE_MCP_URL não definido no .env")
        
        self.client = Client(self.base_url, timeout=timeout)


    async def predict_pace(self, llm_args: Dict[str, Any]) -> Dict[str, Any]:
        mcp_payload = {
            "api_version": "1",
            "trace_id": "tyre-agent-" + str(uuid.uuid4()),
            **llm_args
        }

        async with self.client as session:
            result = await session.call_tool(
                "predict_pace_next_laps_tool",
                {"payload": mcp_payload}
            )

        return vars(result.data)

    async def estimate_drop(self, llm_args: Dict[str, Any]) -> Dict[str, Any]:
        
        mcp_payload = {
            "api_version": "1",
            "trace_id": "tyre-agent-" + str(uuid.uuid4()),
            **llm_args
        }

        async with self.client as session:
            result = await session.call_tool(
                "estimate_laps_to_drop_tool",
                {"payload": mcp_payload}
            )
        
        return vars(result.data)

    async def close(self):
        if self.client.is_connected:
            await self.client.close()