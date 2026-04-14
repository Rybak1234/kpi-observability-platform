# KPI Observability Platform

Plataforma para consolidar datos y visualizar indicadores clave de gestión con flujo ETL, API REST y dashboards en Grafana.

## Tech Stack

- **Backend:** Python + Flask
- **Base de datos:** Neon PostgreSQL (psycopg2)
- **ETL:** Requests + BeautifulSoup
- **Visualización:** Grafana (configuración incluida)
- **Despliegue:** Vercel (Flask) / Docker (Grafana)

## Estructura

```
app/              → Flask application
  routes/         → API endpoints
  services/       → Business logic
  models/         → Database models
  templates/      → Jinja2 HTML templates
  static/css/     → Estilos
etl/              → Scripts de extracción y carga
grafana/          → Dashboards y provisioning de Grafana
```

## Comenzar

```bash
pip install -r requirements.txt
cp .env.example .env
# Configurar DATABASE_URL de Neon
python -m app.db_init
python seed.py              # Carga datos demo (5 fuentes, 30 días de métricas)
python -m flask --app app.main run --debug
```

## ETL

```bash
python -m etl.scraper     # Extrae datos de fuente configurada
python -m etl.loader      # Carga datos limpios a PostgreSQL
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/sources` | Lista fuentes de datos |
| POST | `/api/sources` | Crea nueva fuente |
| GET | `/api/metrics?source_id=&metric=&limit=` | Consulta métricas |
| POST | `/api/metrics` | Registra nueva métrica |
| GET | `/api/metrics/summary` | Resumen estadístico por métrica |
| GET | `/api/export/csv` | Exporta métricas a CSV |
