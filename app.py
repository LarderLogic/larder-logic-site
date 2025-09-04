import os
from flask import Flask
from flask_login import LoginManager
from models import db, User  # import db and User for login manager
from routes import routes     # import Blueprint

def create_app():
    app = Flask(__name__)

    # --- Config ---
    app.secret_key = os.environ.get("SECRET_KEY", "supersecret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- Init DB ---
    db.init_app(app)
    with app.app_context():
        db.create_all()  # ✅ runs every time so DB isn’t left at 0 bytes

    # --- Flask-Login ---
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "routes.login"  # blueprint endpoint

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Register Blueprints ---
    app.register_blueprint(routes)

    return app


# Gunicorn will look for "app"
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
