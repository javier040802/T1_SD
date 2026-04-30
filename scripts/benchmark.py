from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from shared.traffic import generate_requests

def run_series(url: str, distribution: str, n: int, seed: int, ttl: int, label: str):
    rows = []
    for i, req in enumerate(generate_requests(n, distribution=distribution, seed=seed)):
        req["ttl_seconds"] = ttl
        t0 = time.perf_counter()
        resp = requests.post(url, json=req, timeout=20)
        elapsed = (time.perf_counter() - t0) * 1000
        resp.raise_for_status()
        data = resp.json()
        rows.append({
            "label": label,
            "distribution": distribution,
            "ttl": ttl,
            "idx": i,
            "qtype": req["qtype"],
            "cache_hit": data["cache_hit"],
            "latency_ms": data["response_ms"],
            "elapsed_ms": elapsed,
            "compute_ms": data["compute_ms"],
        })
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000/query")
    parser.add_argument("--outdir", default="/data/benchmark")
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    frames = []
    for dist in ["zipf", "uniform"]:
        frames.append(run_series(args.url, dist, args.n, args.seed, ttl=60, label=f"{dist}-ttl60"))
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(outdir / "benchmark_runs.csv", index=False)

    summary = df.groupby("label").agg(
        hit_rate=("cache_hit", "mean"),
        p50=("latency_ms", lambda s: float(s.quantile(0.5))),
        p95=("latency_ms", lambda s: float(s.quantile(0.95))),
        mean_latency=("latency_ms", "mean"),
    ).reset_index()
    summary.to_csv(outdir / "summary.csv", index=False)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for label, g in df.groupby("label"):
        hits = g["cache_hit"].astype(int).rolling(20, min_periods=1).mean()
        ax.plot(hits.values, label=label)
    ax.set_title("Rolling hit rate")
    ax.set_xlabel("request")
    ax.set_ylabel("hit rate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "hit_rate.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.boxplot([df[df["distribution"]=="zipf"]["latency_ms"], df[df["distribution"]=="uniform"]["latency_ms"]], labels=["zipf", "uniform"])
    ax.set_title("Latency by distribution")
    ax.set_ylabel("ms")
    fig.tight_layout()
    fig.savefig(outdir / "latency_boxplot.png", dpi=200)
    plt.close(fig)

    print(json.dumps({"rows": len(df), "outdir": str(outdir)}))

if __name__ == "__main__":
    main()
