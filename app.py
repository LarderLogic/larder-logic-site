import os
from flask import Flask, render_template, request, redirect, url_for, flash
from markupsafe import Markup
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms.WTForm import LoginForm, EditorForm
import bleach
from models import db, Article, Image, Tag, User
from routes import routes   # <-- import the Blueprint

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # <-- Only once, right after config

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Remove any hardcoded users dictionary!

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Register blueprint
app.register_blueprint(routes)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

