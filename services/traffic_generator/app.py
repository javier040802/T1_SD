from __future__ import annotations
import argparse
import json
import time
from pathlib import Path

import requests
from shared.config import settings
from shared.traffic import generate_requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--distribution', choices=['zipf', 'uniform'], default='zipf')
    parser.add_argument('--requests', type=int, default=200)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--delay-ms', type=float, default=25.0)
    parser.add_argument('--output', type=str, default='/data/traffic_log.jsonl')
    parser.add_argument('--url', type=str, default=settings.cache_service_url + '/query')
    parser.add_argument('--cycles', type=int, default=1, help='Número de rondas completas del patrón de tráfico')
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    ok = 0

    for cycle in range(args.cycles):
        for req in generate_requests(args.requests, distribution=args.distribution, seed=args.seed + cycle):
            t0 = time.perf_counter()
            r = requests.post(args.url, json=req, timeout=settings.request_timeout_seconds)
            elapsed = (time.perf_counter() - t0) * 1000
            r.raise_for_status()
            ok += 1
            with out.open('a', encoding='utf-8') as f:
                f.write(json.dumps({'request': req, 'response': r.json(), 'elapsed_ms': elapsed, 'cycle': cycle}, ensure_ascii=False) + '\n')
            if args.delay_ms > 0:
                time.sleep(args.delay_ms / 1000.0)

    print(json.dumps({'sent': args.requests * args.cycles, 'ok': ok, 'output': str(out)}))


if __name__ == '__main__':
    main()
