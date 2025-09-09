import os
from typing import Annotated
from fastmcp import FastMCP
from .models import (PredictPaceInput, PredictPaceOutput,EstimateDropInput, EstimateDropOutput)
from .logic import predict_pace_next_laps, estimate_laps_to_drop

HOST = os.getenv("MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_PORT", "8787"))

mcp = FastMCP(name="Tyre MCP", instructions=(
    "Este servidor MCP expõe funções relacionadas a pneus de Fórmula 1. Ele oferece duas ferramentas principais:\n\n"
    "1. `predict_pace_next_laps_tool`: Prevê os tempos de volta considerando o desgaste e a temperatura dos pneus.\n"
    "2. `estimate_laps_to_drop_tool`: Estima o número de voltas restantes antes da queda drástica de performance do pneu."
), stateless_http=True)

@mcp.tool
def predict_pace_next_laps_tool(
    payload: Annotated[PredictPaceInput, "Payload de entrada para previsão de pace"]
    ) -> PredictPaceOutput:
    """Prevê os tempos de volta nas próximas voltas considerando desgaste e temperatura dos pneus."""
    return predict_pace_next_laps(payload)

@mcp.tool
def estimate_laps_to_drop_tool(
    payload: Annotated[EstimateDropInput, "Payload para estimar em quantas voltas o desempenho cairá drasticamente"]
    ) -> EstimateDropOutput:
    """Estima quantas voltas restam antes da queda drástica de performance do pneu."""
    return estimate_laps_to_drop(payload)

@mcp.tool
def health_check() -> dict:
    """Health check endpoint for Docker"""
    return {"status": "healthy", "service": "tyre-mcp"}

if __name__ == "__main__":
    mcp.run(
        transport="http", 
        host=HOST,
        port=PORT,
        path="/mcp" 
    )