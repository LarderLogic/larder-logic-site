import os
from flask import Flask
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from models import db, User


# Import blueprints
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.article_routes import article_bp
from routes.image_routes import image_bp
from routes.tag_routes import tag_bp
from routes.contact_routes import contact_bp
from routes.public_routes import public_bp  # New import    




def create_app():
    app = Flask(__name__)


    # --- Config ---
    app.secret_key = os.environ.get("SECRET_KEY", "supersecret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    # --- Init DB ---
    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()


    # --- Flask-Login ---
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.admin_login"  # login route is in auth_routes.py


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # --- Register Blueprints ---
    app.register_blueprint(public_bp)  # Register public routes without prefix
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(contact_bp)


    # --- CKEditor ---
    ckeditor = CKEditor()
    ckeditor.init_app(app)


    return app




# Gunicorn will look for "app"
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

