import pandas as pd

def load_data():
    df = pd.read_csv("data/buildings.csv")

    zones = {
        "Z1": (-33.445, -33.420, -70.640, -70.600),
        "Z2": (-33.420, -33.390, -70.600, -70.550),
        "Z3": (-33.530, -33.490, -70.790, -70.740),
        "Z4": (-33.460, -33.430, -70.670, -70.630),
        "Z5": (-33.470, -33.430, -70.810, -70.760),
    }

    data = {}
    for z, (lat_min, lat_max, lon_min, lon_max) in zones.items():
        data[z] = df[
            (df.latitude >= lat_min) &
            (df.latitude <= lat_max) &
            (df.longitude >= lon_min) &
            (df.longitude <= lon_max)
        ]

    return data
