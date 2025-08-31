from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal 

Compound = Literal["S", "M", "H"]

class PredictPaceInput(BaseModel):
    """
    Use esta ferramenta para prever os tempos de volta futuros de um piloto.
    É útil quando a pergunta é sobre 'qual será o pace', 'ritmo esperado' ou 'tempos das próximas voltas'.
    """

    model_config = ConfigDict(extra="ignore")
    compound: Compound = Field(..., description="Composto do pneu (S, M, ou H)")
    stint_laps: int = Field(..., ge=0, description="Número de voltas já completadas neste stint")
    last_n_laps: List[float] = Field(..., min_length=3, description="Lista com os tempos das últimas 3 ou mais voltas")
    track_temp: float = Field(..., description="Temperatura da pista em graus Celsius")
    tyre_wear_level: float = Field(..., ge=0, description="Nível de desgaste atual do pneu (ex: 0.75 para 75%)")
    future_laps: int = Field(default=3, ge=1, le=5, description="Número de voltas futuras para prever")


class EstimateDropInput(BaseModel):
    """
    Use esta ferramenta para estimar em quantas voltas um pneu sofrerá uma queda brusca de performance.
    É útil para perguntas sobre 'até quando o pneu aguenta', 'quando vai cair o rendimento' ou 'previsão de queda'.
    """

    model_config = ConfigDict(extra="ignore")
    compound: Compound = Field(..., description="Composto do pneu (S, M, ou H)")
    stint_laps: int = Field(..., ge=0, description="Número de voltas já completadas neste stint")
    last_n_laps: List[float] = Field(..., min_length=3, description="Lista com os tempos das últimas 3 ou mais voltas")
    tyre_wear_level: float = Field(..., ge=0, description="Nível de desgaste atual do pneu (ex: 0.75 para 75%)")
