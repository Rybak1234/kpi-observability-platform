"""Admin routes: dashboard, user management, sources, metrics."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app.db import query, execute
from app.routes.auth import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def dashboard():
    users = query("SELECT id, name, email, role, created_at, last_login FROM kpi_users ORDER BY created_at")
    sources = query("SELECT * FROM kpi_sources ORDER BY name")
    total_metrics = query("SELECT COUNT(*) as cnt FROM kpi_metrics")
    total_sources = len(sources)
    total_users = len(users)

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

    recent_metrics = query("""
        SELECT m.metric_name, m.metric_value, m.unit, m.period_date, s.name as source_name
        FROM kpi_metrics m
        JOIN kpi_sources s ON s.id = m.source_id
        ORDER BY m.created_at DESC
        LIMIT 10
    """)

    metrics_by_source = query("""
        SELECT s.name, COUNT(*) as cnt
        FROM kpi_metrics m
        JOIN kpi_sources s ON s.id = m.source_id
        GROUP BY s.name
        ORDER BY cnt DESC
    """)

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_sources=total_sources,
        total_metrics=total_metrics[0]["cnt"] if total_metrics else 0,
        total_kpis=len(summary),
        summary=summary,
        recent_metrics=recent_metrics,
        metrics_by_source=metrics_by_source,
        users=users,
    )


@bp.route("/users")
@admin_required
def users():
    all_users = query("SELECT id, name, email, role, created_at, last_login FROM kpi_users ORDER BY created_at")
    return render_template("admin/users.html", users=all_users)


@bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def update_role(user_id):
    role = request.form.get("role")
    if role in ("admin", "editor", "viewer"):
        execute("UPDATE kpi_users SET role = %s WHERE id = %s", (role, user_id))
        flash("Role updated", "success")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    execute("DELETE FROM kpi_users WHERE id = %s", (user_id,))
    flash("User deleted", "success")
    return redirect(url_for("admin.users"))


@bp.route("/sources")
@admin_required
def sources():
    all_sources = query("""
        SELECT s.*, COUNT(m.id) as metric_count
        FROM kpi_sources s
        LEFT JOIN kpi_metrics m ON m.source_id = s.id
        GROUP BY s.id, s.name, s.source_type, s.url, s.created_at
        ORDER BY s.name
    """)
    return render_template("admin/sources.html", sources=all_sources)


@bp.route("/sources/add", methods=["POST"])
@admin_required
def add_source():
    name = request.form.get("name", "").strip()
    source_type = request.form.get("source_type", "manual")
    url = request.form.get("url", "").strip() or None
    if name:
        execute("INSERT INTO kpi_sources (name, source_type, url) VALUES (%s, %s, %s)", (name, source_type, url))
        flash("Source added", "success")
    return redirect(url_for("admin.sources"))


@bp.route("/sources/<int:source_id>/delete", methods=["POST"])
@admin_required
def delete_source(source_id):
    execute("DELETE FROM kpi_sources WHERE id = %s", (source_id,))
    flash("Source deleted", "success")
    return redirect(url_for("admin.sources"))


@bp.route("/metrics")
@admin_required
def metrics():
    source_id = request.args.get("source_id")
    metric_name = request.args.get("metric_name")

    sql = """
        SELECT m.id, m.metric_name, m.metric_value, m.unit, m.period_date, s.name as source_name
        FROM kpi_metrics m
        JOIN kpi_sources s ON s.id = m.source_id
        WHERE 1=1
    """
    params = []
    if source_id:
        sql += " AND m.source_id = %s"
        params.append(int(source_id))
    if metric_name:
        sql += " AND m.metric_name = %s"
        params.append(metric_name)
    sql += " ORDER BY m.period_date DESC LIMIT 100"

    rows = query(sql, params)
    sources_list = query("SELECT id, name FROM kpi_sources ORDER BY name")
    metric_names = query("SELECT DISTINCT metric_name FROM kpi_metrics ORDER BY metric_name")

    return render_template(
        "admin/metrics.html",
        metrics=rows,
        sources=sources_list,
        metric_names=metric_names,
        selected_source=source_id,
        selected_metric=metric_name,
    )
