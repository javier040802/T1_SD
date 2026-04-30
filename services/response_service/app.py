from __future__ import annotations
import time
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from shared.config import settings
from shared.dataset import DatasetStore, load_dataset
from shared.query_engine import QueryEngine

class ComputeRequest(BaseModel):
    qtype: str
    zone_id: str | None = None
    zone_id_a: str | None = None
    zone_id_b: str | None = None
    confidence_min: float = 0.0
    bins: int = 5

app = FastAPI(title="response-service")
store: DatasetStore | None = None
engine: QueryEngine | None = None

@app.on_event("startup")
def startup():
    global store, engine
    dataset_path = settings.dataset_path
    store = DatasetStore(load_dataset(dataset_path))
    engine = QueryEngine(store)

@app.get("/health")
def health():
    return {"status": "ok", "dataset_rows": int(store.df.shape[0]) if store else 0}

@app.post("/compute")
def compute(req: ComputeRequest):
    start = time.perf_counter()
    payload = engine.compute(req.model_dump())
    compute_ms = (time.perf_counter() - start) * 1000
    return {"payload": payload, "compute_ms": compute_ms}
