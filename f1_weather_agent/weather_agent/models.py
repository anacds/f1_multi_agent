from pydantic import BaseModel, Field
from typing import Optional, List

class AgentRequest(BaseModel):
    lat: float
    lon: float
    minutes: int = Field(default=30, ge=1, le=60)

class SummaryWindow(BaseModel):
    start_minute: int
    end_minute: int
    count_minute: int
    text_template: Optional[str] = None

class AgentOutput(BaseModel):
    will_rain: bool
    rain_start_in_min: Optional[int] = None
    phrase: Optional[str] = None
    summaries: List[SummaryWindow] = []
    confidence: float = 0.7
    explanation: Optional[str] = None