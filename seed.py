"""
Seed script: populates the database with demo KPI sources and metrics.
Usage: python seed.py
"""
import random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash
from app.db import execute, query
from app.db_init import SCHEMA

# Initialize tables
for statement in SCHEMA.strip().split(";"):
    stmt = statement.strip()
    if stmt:
        execute(stmt + ";")

print("Tables created.")

# Users
demo_users = [
    ("Administrador", "admin@kpiplatform.com", "admin123", "admin"),
    ("Editor KPI", "editor@kpiplatform.com", "editor123", "editor"),
    ("Viewer Demo", "viewer@kpiplatform.com", "viewer123", "viewer"),
]
for name, email, password, role in demo_users:
    existing = query("SELECT id FROM kpi_users WHERE email = %s", (email,))
    if not existing:
        pw_hash = generate_password_hash(password)
        execute(
            "INSERT INTO kpi_users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (name, email, pw_hash, role),
        )
print(f"Created {len(demo_users)} demo users.")

# Sources
sources = [
    ("NovaTech Tienda", "etl", "https://smb-commerce-platform.vercel.app/api/products"),
    ("NovaTech Inventario", "etl", "https://retail-inventory-platform-gamma.vercel.app/api/products"),
    ("NovaTech Docs", "etl", "https://saas-auth-service.vercel.app/api/documents"),
    ("NovaTech Ops", "etl", "https://realtime-ops-dashboard.vercel.app/api/metrics"),
    ("Equipo NovaTech", "manual", None),
]

source_ids = {}
for name, stype, url in sources:
    existing = query("SELECT id FROM kpi_sources WHERE name = %s", (name,))
    if existing:
        source_ids[name] = existing[0]["id"]
    else:
        execute(
            "INSERT INTO kpi_sources (name, source_type, url) VALUES (%s, %s, %s)",
            (name, stype, url),
        )
        rows = query("SELECT id FROM kpi_sources WHERE name = %s", (name,))
        source_ids[name] = rows[0]["id"]

print(f"Inserted {len(sources)} sources.")

# Metrics — generate 30 days of data
today = date.today()
metrics_config = {
    "NovaTech Tienda": [
        ("Ingresos Diarios", 800, 3500, "Bs."),
        ("Pedidos", 5, 40, "count"),
        ("Ticket Promedio", 80, 250, "Bs."),
        ("Tasa de Conversión", 1.5, 5.0, "%"),
    ],
    "NovaTech Inventario": [
        ("Productos en Stock", 120, 200, "count"),
        ("Movimientos Diarios", 10, 60, "count"),
        ("Productos Bajo Stock", 0, 15, "count"),
        ("Valor del Inventario", 15000, 45000, "Bs."),
    ],
    "NovaTech Docs": [
        ("Documentos Creados", 2, 20, "count"),
        ("Usuarios Activos", 3, 15, "count"),
        ("Sesiones Diarias", 5, 30, "count"),
        ("Documentos Totales", 50, 200, "count"),
    ],
    "NovaTech Ops": [
        ("Uptime del Sistema", 95.0, 99.99, "%"),
        ("Tiempo de Respuesta API", 80, 500, "ms"),
        ("Errores 5xx", 0, 10, "count"),
    ],
    "Equipo NovaTech": [
        ("Empleados Activos", 5, 12, "count"),
        ("Tareas Completadas", 8, 35, "count"),
        ("NPS Equipo", 60, 95, "pts"),
    ],
}

total = 0
for source_name, metrics in metrics_config.items():
    sid = source_ids[source_name]
    for metric_name, low, high, unit in metrics:
        for day_offset in range(30):
            d = today - timedelta(days=29 - day_offset)
            value = round(random.uniform(low, high), 2)
            execute(
                "INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES (%s, %s, %s, %s, %s)",
                (sid, metric_name, value, unit, str(d)),
            )
            total += 1

print(f"Inserted {total} metric records across 30 days.")
print("Seed completed successfully!")
