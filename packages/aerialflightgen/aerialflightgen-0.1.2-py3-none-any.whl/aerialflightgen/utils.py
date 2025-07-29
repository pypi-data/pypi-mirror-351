# Utility functions for coordinate math or file IO

def meters_to_time(distance_m: float, speed_mps: float) -> float:
    return round(distance_m / speed_mps, 2)

def print_banner():
    print("Aerial Flight Generator is active.")
