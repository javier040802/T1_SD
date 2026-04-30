from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
STORE_PATH = Path('/data/metrics.jsonl')
SUMMARY_PATH = Path('/data/metrics_summary.json')
class Event(BaseModel):
    timestamp: float
    request_id: str
    qtype: str
    cache_key: str
    cache_hit: bool
    latency_ms: float
    compute_ms: float
    status: str = 'ok'
    evicted_keys_total: int = 0
    redis_used_memory: int = 0
    redis_keyspace_hits: int = 0
    redis_keyspace_misses: int = 0
    source: str = 'cache-service'
    payload_size: int = 0

app = FastAPI(title='metrics-service')
events: list[dict[str, Any]] = []

def _ensure_store() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

def _append_event(event: dict[str, Any]) -> None:
    _ensure_store()
    with STORE_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')

def _summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            'count': 0,
            'hits': 0,
            'misses': 0,
            'hit_rate': 0.0,
            'miss_rate': 0.0,
            'latency_p50_ms': 0.0,
            'latency_p95_ms': 0.0,
            'throughput_qps': 0.0,
            'eviction_rate_per_min': 0.0,
            'cache_efficiency': 0.0,
            'evicted_keys_total': 0,
        }

    hits = int(df['cache_hit'].sum())
    misses = int((~df['cache_hit']).sum())
    lat = df['latency_ms'].astype(float)
    duration = max(1.0, float(df['timestamp'].max()) - float(df['timestamp'].min()))
    evictions = int(df['evicted_keys_total'].max())
    tcache = float(df.loc[df['cache_hit'], 'latency_ms'].mean()) if hits else 0.0
    tdb = float(df.loc[~df['cache_hit'], 'compute_ms'].mean()) if misses else 0.0
    cache_efficiency = float((hits * tcache) - (misses * tdb))

    return {
        'count': int(df.shape[0]),
        'hits': hits,
        'misses': misses,
        'hit_rate': float(hits / max(1, hits + misses)),
        'miss_rate': float(misses / max(1, hits + misses)),
        'latency_p50_ms': float(lat.quantile(0.50)),
        'latency_p95_ms': float(lat.quantile(0.95)),
        'throughput_qps': float(df.shape[0] / duration),
        'eviction_rate_per_min': float(evictions / max(duration / 60.0, 1e-6)),
        'cache_efficiency': cache_efficiency,
        'evicted_keys_total': evictions,
    }


@app.post('/event')
def add_event(event: Event):
    payload = event.model_dump()
    events.append(payload)
    _append_event(payload)
    SUMMARY_PATH.write_text(json.dumps(_summary(pd.DataFrame(events)), indent=2), encoding='utf-8')
    return {'status': 'accepted', 'buffered': len(events)}


@app.get('/summary')
def summary():
    if STORE_PATH.exists():
        parts = []
        with STORE_PATH.open('r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    parts.append(json.loads(line))
        df = pd.DataFrame(parts)
    else:
        df = pd.DataFrame(events)
    s = _summary(df)
    SUMMARY_PATH.write_text(json.dumps(s, indent=2), encoding='utf-8')
    return s


@app.get('/events')
def get_events(limit: int = 100):
    if STORE_PATH.exists():
        parts = []
        with STORE_PATH.open('r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    parts.append(json.loads(line))
        return {'events': parts[-limit:]}
    return {'events': events[-limit:]}


@app.get('/health')
def health():
    return {'status': 'ok', 'buffered': len(events)}
