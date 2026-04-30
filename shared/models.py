from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional, Union

ZoneId = Literal["Z1", "Z2", "Z3", "Z4", "Z5"]

class QueryRequest(BaseModel):
    qtype: Literal["Q1", "Q2", "Q3", "Q4", "Q5"]
    zone_id: Optional[ZoneId] = None
    zone_id_a: Optional[ZoneId] = None
    zone_id_b: Optional[ZoneId] = None
    confidence_min: float = Field(default=0.0, ge=0.0, le=1.0)
    bins: int = Field(default=5, ge=2, le=50)
    ttl_seconds: Optional[int] = Field(default=None, ge=1, le=86400)

class QueryResult(BaseModel):
    cache_key: str
    qtype: str
    zone_id: Optional[str] = None
    zone_id_a: Optional[str] = None
    zone_id_b: Optional[str] = None
    cache_hit: bool
    ttl_seconds: int
    response_ms: float
    compute_ms: float
    payload: Any

class MetricsEvent(BaseModel):
    timestamp: float
    request_id: str
    qtype: str
    cache_key: str
    cache_hit: bool
    latency_ms: float
    compute_ms: float
    status: str = "ok"
    evicted_keys_total: int = 0
    redis_used_memory: int = 0
    redis_keyspace_hits: int = 0
    redis_keyspace_misses: int = 0
    source: str = "cache-service"
    payload_size: int = 0
