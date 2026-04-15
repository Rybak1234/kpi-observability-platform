"""One-time DB initialization endpoint for Vercel deployment."""
from flask import jsonify
from werkzeug.security import generate_password_hash
from app.db import execute, query
from app.db_init import SCHEMA


def init_db():
    """Initialize tables and seed default users."""
    # Create tables
    for statement in SCHEMA.strip().split(";"):
        stmt = statement.strip()
        if stmt:
            execute(stmt + ";")

    # Seed default users if none exist
    existing = query("SELECT COUNT(*) as cnt FROM kpi_users")
    if existing and existing[0]["cnt"] == 0:
        users = [
            ("Administrador", "admin@kpiplatform.com", "admin123", "admin"),
            ("Editor KPI", "editor@kpiplatform.com", "editor123", "editor"),
            ("Viewer Demo", "viewer@kpiplatform.com", "viewer123", "viewer"),
        ]
        for name, email, password, role in users:
            pw_hash = generate_password_hash(password)
            execute(
                "INSERT INTO kpi_users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                (name, email, pw_hash, role),
            )
        return True
    return False
