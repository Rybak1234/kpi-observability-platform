"""Authentication routes: login, register, logout."""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import query, execute

bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("user_role") != "admin":
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return wrapper


def get_current_user():
    if "user_id" in session:
        users = query("SELECT id, name, email, role, created_at FROM kpi_users WHERE id = %s", (session["user_id"],))
        return users[0] if users else None
    return None


@bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        users = query("SELECT * FROM kpi_users WHERE email = %s", (email,))
        if users and check_password_hash(users[0]["password_hash"], password):
            user = users[0]
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]
            execute("UPDATE kpi_users SET last_login = NOW() WHERE id = %s", (user["id"],))
            return redirect(url_for("dashboard.index"))
        flash("Invalid email or password", "error")

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("All fields are required", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters", "error")
        elif query("SELECT id FROM kpi_users WHERE email = %s", (email,)):
            flash("Email already registered", "error")
        else:
            pw_hash = generate_password_hash(password)
            execute(
                "INSERT INTO kpi_users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                (name, email, pw_hash, "viewer"),
            )
            users = query("SELECT * FROM kpi_users WHERE email = %s", (email,))
            user = users[0]
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]
            return redirect(url_for("dashboard.index"))

    return render_template("register.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
