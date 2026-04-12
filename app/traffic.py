import numpy as np
import random

zones = ["Z1", "Z2", "Z3", "Z4", "Z5"]

def zipf_choice():
    weights = np.random.zipf(2, len(zones))
    probs = weights / sum(weights)
    return np.random.choice(zones, p=probs)

def uniform_choice():
    return random.choice(zones)
