from fastapi import FastAPI
from data_loader import load_data
from queries import *
from cache import get_or_set
from metrics import log, compute

app = FastAPI()

data = load_data()
area_km2 = {"Z1":10, "Z2":12, "Z3":15, "Z4":8, "Z5":20}

@app.get("/q1")
def endpoint(zone: str, conf: float = 0.0):
    key = f"q1:{zone}:{conf}"

    result, hit, latency = get_or_set(
        key,
        lambda: q1(data, zone, conf)
    )

    log(hit, latency)
    return result

@app.get("/metrics")
def get_metrics():
    return compute()
