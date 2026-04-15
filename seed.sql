-- Create tables
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

-- Seed sources
INSERT INTO kpi_sources (name, source_type, url) VALUES
  ('NovaTech Tienda', 'etl', 'https://smb-commerce-platform.vercel.app/api/products'),
  ('NovaTech Inventario', 'etl', 'https://retail-inventory-platform-gamma.vercel.app/api/products'),
  ('NovaTech Docs', 'etl', 'https://saas-auth-service.vercel.app/api/documents'),
  ('NovaTech Ops', 'etl', 'https://realtime-ops-dashboard.vercel.app/api/metrics'),
  ('Equipo NovaTech', 'manual', NULL);

-- Seed metrics (sample data for 30 days)
DO $$
DECLARE
  s_tienda INT;
  s_inventario INT;
  s_docs INT;
  s_ops INT;
  s_equipo INT;
  d DATE;
BEGIN
  SELECT id INTO s_tienda FROM kpi_sources WHERE name = 'NovaTech Tienda';
  SELECT id INTO s_inventario FROM kpi_sources WHERE name = 'NovaTech Inventario';
  SELECT id INTO s_docs FROM kpi_sources WHERE name = 'NovaTech Docs';
  SELECT id INTO s_ops FROM kpi_sources WHERE name = 'NovaTech Ops';
  SELECT id INTO s_equipo FROM kpi_sources WHERE name = 'Equipo NovaTech';

  FOR i IN 0..29 LOOP
    d := CURRENT_DATE - (29 - i);
    -- Tienda
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_tienda, 'Ingresos Diarios', round((random() * 2700 + 800)::numeric, 2), 'Bs.', d),
      (s_tienda, 'Pedidos', round((random() * 35 + 5)::numeric, 0), 'count', d),
      (s_tienda, 'Ticket Promedio', round((random() * 170 + 80)::numeric, 2), 'Bs.', d),
      (s_tienda, 'Tasa de Conversión', round((random() * 3.5 + 1.5)::numeric, 2), '%', d);
    -- Inventario
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_inventario, 'Productos en Stock', round((random() * 80 + 120)::numeric, 0), 'count', d),
      (s_inventario, 'Movimientos Diarios', round((random() * 50 + 10)::numeric, 0), 'count', d),
      (s_inventario, 'Productos Bajo Stock', round((random() * 15)::numeric, 0), 'count', d),
      (s_inventario, 'Valor del Inventario', round((random() * 30000 + 15000)::numeric, 2), 'Bs.', d);
    -- Docs
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_docs, 'Documentos Creados', round((random() * 18 + 2)::numeric, 0), 'count', d),
      (s_docs, 'Usuarios Activos', round((random() * 12 + 3)::numeric, 0), 'count', d),
      (s_docs, 'Sesiones Diarias', round((random() * 25 + 5)::numeric, 0), 'count', d),
      (s_docs, 'Documentos Totales', round((random() * 150 + 50)::numeric, 0), 'count', d);
    -- Ops
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_ops, 'Uptime del Sistema', round((random() * 4.99 + 95)::numeric, 2), '%', d),
      (s_ops, 'Tiempo de Respuesta API', round((random() * 420 + 80)::numeric, 0), 'ms', d),
      (s_ops, 'Errores 5xx', round((random() * 10)::numeric, 0), 'count', d);
    -- Equipo
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_equipo, 'Empleados Activos', round((random() * 7 + 5)::numeric, 0), 'count', d),
      (s_equipo, 'Tareas Completadas', round((random() * 27 + 8)::numeric, 0), 'count', d),
      (s_equipo, 'NPS Equipo', round((random() * 35 + 60)::numeric, 0), 'pts', d);
  END LOOP;
END $$;
