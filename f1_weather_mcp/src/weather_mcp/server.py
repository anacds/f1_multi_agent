import os
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from .models import MinutelyForecastInput, MinutelyForecastOutput
from .logic import get_minutely_forecast

HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8989"))

mcp = FastMCP(
    name="weather_mcp",
    instructions=(
        "Servidor MCP de previsões meteorológicas utilizando a API AccuWeather Minute Forecast."
        "Tool principal: get_minutely_forecast_tool"
        "A resposta inclui will_rain, rain_start_in_min, phrase e as janelas normalizadas."
    ),
    stateless_http=True
)

@mcp.resource("weather://specs")
def specs(context: Context) -> dict:
    return {
        "provider": "AccuWeather Minute Forecast",
        "inputs": {"lat": "float", "lon": "float", "minutes": {"min": 1, "max": 60, "default": 30}}
    }

@mcp.tool
async def get_minutely_forecast_tool(context: Context, payload: MinutelyForecastInput) -> MinutelyForecastOutput:
    try:
        if abs(payload.lat) > 90 or abs(payload.lon) > 180:
            raise ToolError("lat/lon fora de faixa.")

        out = await get_minutely_forecast(payload)

        context.info(
            "weather_mcp.accu.forecast.ok",
            extra={"will_rain": out.will_rain, "rain_start": out.rain_start_in_min, "windows": len(out.summaries)},
        )
        return out

    except ToolError:
        context.error("weather_mcp.accu.forecast.tool_error")
        raise
    except Exception as e:
        context.error("weather_mcp.accu.forecast.unexpected")
        raise ToolError(f"Falha interna no forecast (AccuWeather): {type(e).__name__}: {e}")

@mcp.tool
def health_check() -> dict:
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "weather-mcp"}

if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT, path="/mcp")