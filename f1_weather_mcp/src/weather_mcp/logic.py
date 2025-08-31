import os
import httpx
from typing import Any, Dict, List, Optional
from fastmcp.exceptions import ToolError
from .models import MinutelyForecastInput, MinutelyForecastOutput, SummaryWindow

def _bool_will_rain(summary_phrase: Optional[str], summaries: List[Dict[str, Any]]) -> bool:

    if summary_phrase:
        p = summary_phrase.lower()
        if "rain" in p or "shower" in p:
            return True

    for s in summaries:
        txt = (s.get("MinuteText") or "").lower()
        if "rain" in txt or "shower" in txt:
            return True
    return False


def _first_rain_minute(summaries: List[Dict[str, Any]]) -> Optional[int]:

    best: Optional[int] = None

    for s in summaries:
        txt = (s.get("MinuteText") or "").lower()
        if "rain" in txt or "shower" in txt:
            start = s.get("StartMinute")
            if isinstance(start, int):
                if best is None or start < best:
                    best = start
    return best


def _normalize_summaries(summaries: List[Dict[str, Any]], cutoff_minutes: int) -> List[SummaryWindow]:

    out: List[SummaryWindow] = []

    for s in summaries:
        try:
            start = int(s.get("StartMinute", 0))
            end = int(s.get("EndMinute", start))
            count = int(s.get("CountMinute", max(1, end - start + 1)))
            txt = s.get("MinuteText")
        except Exception:
            continue

        if start > cutoff_minutes:
            continue
        end = min(end, cutoff_minutes)

        out.append(
            SummaryWindow(
                start_minute=start,
                end_minute=end,
                count_minute=count,
                text_template=txt,
            )
        )

    out.sort(key=lambda w: (w.start_minute, w.end_minute))
    return out


async def get_minutely_forecast(req: MinutelyForecastInput) -> MinutelyForecastOutput:

    key = os.getenv("ACCUWEATHER_API_KEY")
    url = os.getenv("ACCUWEATHER_API_URL")

    params = {
        "q": f"{req.lat},{req.lon}",
        "apikey": key
    }

    async with httpx.AsyncClient(timeout=4.0) as client:
        r = await client.get(url, params=params)
        if r.status_code >= 400:
            raise ToolError(f"Erro no AccuWeather - {r.status_code}: {r.text}")
        data = r.json()

    summary = data.get("Summary") or {}
    summaries = data.get("Summaries") or []

    phrase = summary.get("Phrase")
    will_rain = _bool_will_rain(phrase, summaries)
    rain_start = _first_rain_minute(summaries)

    windows = _normalize_summaries(summaries, cutoff_minutes=req.minutes)

    return MinutelyForecastOutput(
        lat=req.lat,
        lon=req.lon,
        will_rain=bool(will_rain),
        rain_start_in_min=rain_start,
        phrase=phrase,
        summaries=windows,
        confidence=0.7,
    )