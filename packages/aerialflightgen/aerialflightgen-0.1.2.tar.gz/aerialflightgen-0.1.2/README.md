# aerialflightgen

Aerial Flight Plan Generator from GeoJSON

`aerialflightgen` is a lightweight Python package that converts a GeoJSON polygon (e.g. from [geojson.io](https://geojson.io)) into a structured drone flight plan — with optional 2D and 3D plotting.

---

## Features

- Lawn-mower style path generator
- Outputs structured `(x, y, z, t)` waypoints
- Exports to JSON
- CLI with `--plot` and `--3dplot`
- Designed for drone simulation, testing, and robotics

---

## Installation

```bash
pip install aerialflightgen
````

---

## Usage (CLI)

```bash
aerialgen polygon.geojson \
  --altitude 100 \
  --speed 5 \
  --rows 6 \
  --out mission.json \
  --plot
```

Use `--3dplot` for 3D altitude visualization:

```bash
aerialgen polygon.geojson --3dplot
```

---

## Usage (Python)

```python
from aerialflightgen import FlightPlanGenerator

planner = FlightPlanGenerator("polygon.geojson", altitude=120, speed=6, rows=8)
mission = planner.to_dict()
planner.save_to_json("mission.json")
```

---

## Output Format

```json
{
  "mission_id": "generated_mission",
  "start_time": 0.0,
  "end_time": 120.0,
  "waypoints": [
    { "x": 79.78, "y": 11.97, "z": 100, "t": 0.0 },
    { "x": 79.79, "y": 11.97, "z": 100, "t": 10.0 }
  ]
}
```

---

## Author

Created by [Thirumurugan Chokkalingam](https://github.com/ThiruLoki)
MIT License

```

