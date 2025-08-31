import os
import uuid
from typing import Optional, Dict, Any
from fastmcp import Client

WEATHER_MCP_URL = os.getenv("WEATHER_MCP_URL")

class WeatherMCPClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 15.0):
        self.base_url = base_url or WEATHER_MCP_URL
        if not self.base_url:
            raise RuntimeError("WEATHER_MCP_URL não definido no .env")
        self.client = Client(self.base_url, timeout=timeout)

    async def get_minutely_nowcast(self, llm_args: Dict[str, Any]) -> Dict[str, Any]:
        mcp_payload = {
            "api_version": "1",
            "trace_id": "weather-agent-" + str(uuid.uuid4()),
            **llm_args
        }

        async with self.client as session:
            result = await session.call_tool(
                "get_minutely_forecast_tool",
                {"payload": mcp_payload}
            )

        return vars(result.data)

    async def close(self):
        if self.client.is_connected:
            await self.client.close()