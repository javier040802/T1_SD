from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    response_service_url: str = os.getenv("RESPONSE_SERVICE_URL", "http://response-service:8001")
    metrics_service_url: str = os.getenv("METRICS_SERVICE_URL", "http://metrics-service:8002")
    cache_service_url: str = os.getenv("CACHE_SERVICE_URL", "http://cache-service:8000")
    dataset_path: str = os.getenv("DATASET_PATH", "/app/data/buildings_sample.csv")
    ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    request_timeout_seconds: int = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    default_cache_maxmemory: str = os.getenv("REDIS_MAXMEMORY", "256mb")
    default_cache_policy: str = os.getenv("REDIS_MAXMEMORY_POLICY", "allkeys-lru")
    app_port: int = int(os.getenv("PORT", "8000"))

settings = Settings()
