from .models import PredictPaceInput, PredictPaceOutput, EstimateDropInput, EstimateDropOutput

def predict_pace_next_laps(req: PredictPaceInput) -> PredictPaceOutput:

    BASE_DEGRADATION = 0.20
    WEAR_FACTOR = 0.10
    WEAR_CAP = 0.40
    HOT_THRESHOLD = 30.0
    HOT_FACTOR = 0.01
    BASE_CONF = 0.85
    MIN_CONF = 0.50

    last_index = len(req.last_n_laps) - 1
    base = req.last_n_laps[last_index]

    wear_adj = req.tyre_wear_level * WEAR_FACTOR
    if wear_adj > WEAR_CAP:
        wear_adj = WEAR_CAP

    if req.track_temp > HOT_THRESHOLD:
        temp_adj = (req.track_temp - HOT_THRESHOLD) * HOT_FACTOR
    else:
        temp_adj = 0.0

    step = BASE_DEGRADATION + wear_adj + temp_adj

    series = []
    i = 1
    while i <= req.future_laps:
        value = base + step * i
        value = round(value, 3)
        series.append(value)
        i += 1

    conf = BASE_CONF - wear_adj
    if conf < MIN_CONF:
        conf = MIN_CONF
    conf = round(conf, 2)

    return PredictPaceOutput(
        proj_lap_times_next_X=series,
        confidence=round(conf, 2),
        trace_id=req.trace_id,
    )

def estimate_laps_to_drop(req: EstimateDropInput) -> EstimateDropOutput:
    # mock
    base = 8
    wear_penalty = int(req.tyre_wear_level * 6)
    stint_penalty = max((req.stint_laps - 12) // 5, 0)
    laps = max(base - wear_penalty - stint_penalty, 0)

    conf = 0.6 if req.tyre_wear_level > 0.5 else 0.7

    return EstimateDropOutput(
        laps_to_drop=laps,
        confidence=round(conf, 2),
        trace_id=req.trace_id,
    )