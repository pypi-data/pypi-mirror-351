# aerialflightgen/planner.py

import json
from typing import List, Dict

class FlightPlanGenerator:
    def __init__(self, geojson_path: str, altitude: float = 100.0, speed: float = 5.0, rows: int = 6):
        self.geojson_path = geojson_path
        self.altitude = altitude
        self.speed = speed
        self.rows = rows
        self.coords = self._load_coords()

    def _load_coords(self) -> List[List[float]]:
        with open(self.geojson_path, 'r') as f:
            geo = json.load(f)
        return geo["features"][0]["geometry"]["coordinates"][0]

    def _get_bounds(self):
        lons = [pt[0] for pt in self.coords]
        lats = [pt[1] for pt in self.coords]
        return min(lons), max(lons), min(lats), max(lats)

    def generate_waypoints(self) -> List[Dict]:
        lon_min, lon_max, lat_min, lat_max = self._get_bounds()
        lat_step = (lat_max - lat_min) / (self.rows - 1)

        waypoints = []
        t = 0.0
        segment_length = 50.0  # meters (assumed)
        dt = segment_length / self.speed  # time step in seconds

        for i in range(self.rows):
            lat = lat_min + i * lat_step
            lons = [lon_min, lon_max] if i % 2 == 0 else [lon_max, lon_min]
            for lon in lons:
                waypoints.append({
                    "x": lon,
                    "y": lat,
                    "z": self.altitude,
                    "t": round(t, 2)
                })
                t += dt

        return waypoints

    def to_dict(self) -> Dict:
        waypoints = self.generate_waypoints()
        return {
            "mission_id": "generated_mission",
            "start_time": 0.0,
            "end_time": waypoints[-1]["t"] if waypoints else 0.0,
            "waypoints": waypoints
        }

    def save_to_json(self, out_path: str):
        data = self.to_dict()
        with open(out_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Flight plan saved to {out_path}")
