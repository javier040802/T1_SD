metrics = []

def log(hit, latency):
    metrics.append({
        "hit": hit,
        "latency": latency
    })

def compute():
    hits = sum(1 for m in metrics if m["hit"])
    total = len(metrics)

    latencies = [m["latency"] for m in metrics]

    return {
        "hit_rate": hits / total if total else 0,
        "p50": sorted(latencies)[int(0.5 * total)],
        "p95": sorted(latencies)[int(0.95 * total)]
    }
