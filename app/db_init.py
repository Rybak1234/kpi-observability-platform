"""Initialize database tables."""
from app.db import execute

SCHEMA = """
CREATE TABLE IF NOT EXISTS kpi_users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kpi_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) DEFAULT 'manual',
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kpi_metrics (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES kpi_sources(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    unit VARCHAR(30) DEFAULT '',
    period_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_source ON kpi_metrics(source_id);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON kpi_metrics(period_date);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON kpi_metrics(metric_name);
"""

if __name__ == "__main__":
    for statement in SCHEMA.strip().split(";"):
        stmt = statement.strip()
        if stmt:
            execute(stmt + ";")
    print("Database tables created successfully.")
