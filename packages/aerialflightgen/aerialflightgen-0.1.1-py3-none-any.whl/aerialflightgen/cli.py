import argparse
from aerialflightgen.planner import FlightPlanGenerator
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_waypoints(waypoints):
    x = [wp["x"] for wp in waypoints]
    y = [wp["y"] for wp in waypoints]

    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue')
    for i, wp in enumerate(waypoints):
        plt.text(wp["x"], wp["y"], str(i), fontsize=8)
    plt.title("Drone Flight Path")
    plt.xlabel("Longitude (x)")
    plt.ylabel("Latitude (y)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_waypoints_3d(waypoints):
    x = [wp["x"] for wp in waypoints]
    y = [wp["y"] for wp in waypoints]
    z = [wp["z"] for wp in waypoints]

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(x, y, z, marker='o', linestyle='-', color='green')

    for i in range(len(x)):
        ax.text(x[i], y[i], z[i], str(i), size=8)

    ax.set_title("3D Drone Flight Path")
    ax.set_xlabel("Longitude (x)")
    ax.set_ylabel("Latitude (y)")
    ax.set_zlabel("Altitude (z)")
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Generate a drone flight plan from a GeoJSON polygon.")
    parser.add_argument("geojson", type=str, help="Path to input polygon.geojson")
    parser.add_argument("--altitude", type=float, default=100.0, help="Flight altitude in meters")
    parser.add_argument("--speed", type=float, default=5.0, help="Drone speed in m/s")
    parser.add_argument("--rows", type=int, default=6, help="Number of lawnmower passes")
    parser.add_argument("--out", type=str, default="mission.json", help="Path to output mission JSON")
    parser.add_argument("--plot", action="store_true", help="Display plot of generated waypoints")
    parser.add_argument("--3dplot", action="store_true", help="Display 3D plot of generated waypoints")


    args = parser.parse_args()

    planner = FlightPlanGenerator(
        geojson_path=args.geojson,
        altitude=args.altitude,
        speed=args.speed,
        rows=args.rows
    )

    planner.save_to_json(args.out)

    if args.plot:
        plot_waypoints(planner.generate_waypoints())

    if args.__dict__.get("3dplot"):
        plot_waypoints_3d(planner.generate_waypoints())

