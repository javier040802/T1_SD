from __future__ import annotations
from pathlib import Path
import json

import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title='SD T1 Dashboard', layout='wide')
st.title('Dashboard de métricas - Tarea 1 Sistemas Distribuidos')
st.caption('Se actualiza automáticamente para mostrar hits, misses, latencia y eventos recientes.')

METRICS_URL = 'http://metrics-service:8002'
metrics_path = Path('/data/metrics.jsonl')


@st.cache_data(ttl=3)
def fetch_summary() -> dict:
    try:
        r = requests.get(f'{METRICS_URL}/summary', timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        if metrics_path.exists():
            rows = []
            with metrics_path.open('r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
            if rows:
                df = pd.DataFrame(rows)
                hits = int(df['cache_hit'].sum())
                misses = int((~df['cache_hit']).sum())
                lat = df['latency_ms'].astype(float)
                return {
                    'count': int(df.shape[0]),
                    'hits': hits,
                    'misses': misses,
                    'hit_rate': float(hits / max(1, hits + misses)),
                    'miss_rate': float(misses / max(1, hits + misses)),
                    'latency_p50_ms': float(lat.quantile(0.50)),
                    'latency_p95_ms': float(lat.quantile(0.95)),
                    'throughput_qps': float(df.shape[0] / max(1.0, df['timestamp'].max() - df['timestamp'].min())),
                    'eviction_rate_per_min': 0.0,
                    'cache_efficiency': 0.0,
                    'evicted_keys_total': int(df.get('evicted_keys_total', pd.Series([0])).max()),
                }
        return {'count': 0}


@st.cache_data(ttl=3)
def fetch_events(limit: int = 200) -> pd.DataFrame:
    try:
        r = requests.get(f'{METRICS_URL}/events?limit={limit}', timeout=5)
        r.raise_for_status()
        payload = r.json().get('events', [])
        return pd.DataFrame(payload)
    except Exception:
        if metrics_path.exists():
            rows = []
            with metrics_path.open('r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
            return pd.DataFrame(rows[-limit:])
        return pd.DataFrame()


summary = fetch_summary()
df = fetch_events()

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=3000, key='dashboard_refresh')
except Exception:
    pass

if summary.get('count', 0) == 0:
    st.info('Aún no hay tráfico registrado. Levanta el generador o envía consultas manuales para poblar el dashboard.')
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Requests', f"{summary.get('count', 0)}")
    c2.metric('Hit rate', f"{summary.get('hit_rate', 0.0):.2%}")
    c3.metric('P95 latency', f"{summary.get('latency_p95_ms', 0.0):.2f} ms")
    c4.metric('Throughput', f"{summary.get('throughput_qps', 0.0):.2f} req/s")

    c5, c6 = st.columns(2)
    with c5:
        st.subheader('Hit rate acumulado')
        if not df.empty and 'cache_hit' in df:
            x = df.index
            y = df['cache_hit'].astype(int).expanding().mean()
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_xlabel('request')
            ax.set_ylabel('hit rate')
            ax.set_ylim(0, 1)
            st.pyplot(fig, clear_figure=True)
        else:
            st.caption('Sin datos para mostrar.')

    with c6:
        st.subheader('Latencia por tipo de consulta')
        if not df.empty and 'qtype' in df:
            order = sorted(df['qtype'].dropna().unique())
            data = [df[df['qtype'] == q]['latency_ms'] for q in order]
            fig, ax = plt.subplots()
            ax.boxplot(data, labels=order)
            ax.set_ylabel('ms')
            st.pyplot(fig, clear_figure=True)
        else:
            st.caption('Sin datos para mostrar.')

    st.subheader('Eventos recientes')
    st.dataframe(df.tail(100), use_container_width=True)

st.sidebar.caption('La página puede actualizarse manualmente con F5 si tu versión de Streamlit no refresca sola.')
