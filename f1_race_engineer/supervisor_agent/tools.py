from typing import Dict, Any

class SupervisorTools:
    async def get_telemetry_data(self, driver_id: str) -> Dict[str, Any]:
        print(f"--- FERRAMENTA: Buscando dados da telemetria para {driver_id}... ---")
        
        return {
            "circuit_id": "interlagos",
            "circuit_lat_lon": "-23.701,-46.697",
            "driver_id": "hamilton",
            "current_lap": 50,
            "track_temp": 42.8,
            "tyre_compound": "M",
            "tyre_stint_laps": 24,
            "tyre_wear_level": 0.55,
            "last_3_laps": [82.1, 82.2, 82.6]
        }
        
        
supervisor_tools = SupervisorTools()