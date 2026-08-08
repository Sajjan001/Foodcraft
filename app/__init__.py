import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    os.makedirs(app.instance_path, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "foodcraft.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit
    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.config["INSTITUTE_PHONE_1"] = os.environ.get("INSTITUTE_PHONE_1", "8435766076")
    app.config["INSTITUTE_PHONE_2"] = os.environ.get("INSTITUTE_PHONE_2", "9201881729")
    app.config["INSTITUTE_EMAIL"] = os.environ.get("INSTITUTE_EMAIL", "principal.fcirewa@mp.gov.in")

    db.init_app(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    from app.data import get_courses
    app.jinja_env.globals["get_courses"] = get_courses

    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from app.i18n import translate

        lang = session.get("lang", "en")

        def t(key):
            return translate(key, lang)

        return {
            "institute_phone_1": app.config["INSTITUTE_PHONE_1"],
            "institute_phone_2": app.config["INSTITUTE_PHONE_2"],
            "institute_email": app.config["INSTITUTE_EMAIL"],
            "current_year": datetime.now().year,
            "t": t,
            "current_lang": lang,
        }

    return app


# Module-level Flask instance so `gunicorn app:app` (Render's auto-detected
# default command) resolves correctly, in addition to the `run:app` target
# used by run.py / passenger_wsgi.py / render.yaml.
app = create_app()
