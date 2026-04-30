# Tarea 1 - Sistemas Distribuidos

Arquitectura

- `traffic-generator`: produce tráfico Zipf o uniforme y puede repetir ciclos de carga.
- `cache-service`: recibe consultas, consulta Redis, aplica TTL y reporta métricas.
- `response-service`: procesa Q1 a Q5 en memoria.
- `metrics-service`: almacena eventos, publica resumen y persiste el log en cada request.
- `dashboard`: visualiza resultados desde Streamlit con actualización automática.
- `redis`: caché con política de remoción configurable.

Consultas

- Q1: conteo por zona
- Q2: área promedio y total
- Q3: densidad por km²
- Q4: comparación entre dos zonas
- Q5: distribución de confianza

Requisitos

- Docker y Docker Compose

Ejecución

1. Construir y levantar servicios

```bash
docker compose up --build
```

2. Probar un request

```bash
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"qtype":"Q1","zone_id":"Z1","confidence_min":0.2}'
```

3. Abrir dashboard

- Streamlit: `http://localhost:8501`

4. Ver métricas

- `http://localhost:8002/summary`
- `http://localhost:8002/events`

Configuración

Variables útiles:

- `CACHE_TTL_SECONDS`
- `REDIS_MAXMEMORY`
- `REDIS_MAXMEMORY_POLICY`
- `DATASET_PATH`

Generar tráfico manual

Zipf:

```bash
docker compose run --rm traffic-generator python -m services.traffic_generator.app --distribution zipf --requests 200 --delay-ms 20
```

Uniforme:

```bash
docker compose run --rm traffic-generator python -m services.traffic_generator.app --distribution uniform --requests 200 --delay-ms 20
```

Benchmark

Ejecutar:

```bash
python scripts/benchmark.py --url http://localhost:8000/query --outdir ./report/figures
```

Esto genera CSV y figuras para el informe.

Dataset

Si no existe `data/buildings_sample.csv`, el servicio de respuesta genera un subconjunto sintético reproducible con las columnas requeridas por la rúbrica.

