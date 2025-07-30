"""
water_prop: Provides vapor pressure (bar) and specific gravity of water at given temperature (°C).
"""

import csv
import importlib.resources

def load_data():
    with importlib.resources.open_text(__package__, 'water_data.csv') as f:
        reader = csv.DictReader(f)
        return {float(row['Temp']): row for row in reader}

data = load_data()

def get_sg(temp_c):
    temp_c = float(temp_c)
    if temp_c in data:
        return float(data[temp_c]['SG'])
    raise ValueError(f"Temperature {temp_c}°C not found in data.")

def get_vp(temp_c):
    temp_c = float(temp_c)
    if temp_c in data:
        return float(data[temp_c]['VP_bar'])
    raise ValueError(f"Temperature {temp_c}°C not found in data.")
