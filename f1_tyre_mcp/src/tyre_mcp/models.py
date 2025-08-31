from pydantic import BaseModel, Field
from typing import List, Optional, Literal

Compound = Literal["S", "M", "H"]

class PredictPaceInput(BaseModel):
    api_version: str = "1"
    trace_id: Optional[str] = None
    compound: Compound
    stint_laps: int = Field(ge=0)
    last_n_laps: List[float] = Field(min_length=3)
    track_temp: float
    tyre_wear_level: float = Field(ge=0)
    future_laps: int = Field(ge=1, le=5)

class EstimateDropInput(BaseModel):
    api_version: str = "1"
    trace_id: Optional[str] = None
    compound: Compound
    stint_laps: int = Field(ge=0)
    last_n_laps: List[float] = Field(min_length=3)
    tyre_wear_level: float = Field(ge=0)

class PredictPaceOutput(BaseModel):
    proj_lap_times_next_X: List[float]
    confidence: float = Field(ge=0, le=1)
    api_version: str = "1"
    trace_id: Optional[str] = None

class EstimateDropOutput(BaseModel):
    laps_to_drop: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    api_version: str = "1"
    trace_id: Optional[str] = None