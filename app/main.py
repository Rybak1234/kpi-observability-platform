import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-key")

    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.api import bp as api_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp)

    # Initialize database on first request
    with app.app_context():
        try:
            from app.init_seed import init_db
            init_db()
        except Exception:
            pass  # DB might not be ready during build

    return app

app = create_app()
