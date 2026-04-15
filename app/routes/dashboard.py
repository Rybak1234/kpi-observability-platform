from flask import Blueprint, render_template
from app.db import query
from app.routes.auth import login_required

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    sources = query("SELECT * FROM kpi_sources ORDER BY name")

    latest = query("""
        SELECT m.metric_name, m.metric_value, m.unit, m.period_date, s.name as source_name
        FROM kpi_metrics m
        JOIN kpi_sources s ON s.id = m.source_id
        ORDER BY m.period_date DESC, m.metric_name
        LIMIT 50
    """)

    summary = query("""
        SELECT metric_name,
               ROUND(AVG(metric_value)::numeric, 2) as avg_val,
               ROUND(MAX(metric_value)::numeric, 2) as max_val,
               ROUND(MIN(metric_value)::numeric, 2) as min_val,
               COUNT(*) as data_points
        FROM kpi_metrics
        GROUP BY metric_name
        ORDER BY metric_name
    """)

    return render_template("dashboard.html", sources=sources, latest=latest, summary=summary)
