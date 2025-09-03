import os
from flask import Flask, render_template, request, redirect, url_for, flash
from markupsafe import Markup
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms.WTForm import LoginForm, EditorForm
import bleach
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")  # Use env var
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# --- User Model ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Remove any hardcoded users dictionary!

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("admin_editor"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("admin_login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/admin_login.html", methods=["GET", "POST"])
def admin_login():
    form = LoginForm()
    if request.method == "POST":
        # Add your login logic here
        pass
    return render_template("admin_login.html", form=form)

@app.route("/admin_editor.html", methods=["GET", "POST"])
@login_required
def admin_editor():
    form = EditorForm()
    return render_template("admin_editor.html", form=form)

@app.route("/admin/save", methods=["POST"])
@login_required
def admin_save():
    form = EditorForm()
    if form.validate_on_submit():
        title = form.title.data.strip().replace(" ", "_")
        # Sanitize Quill HTML
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union([
    "p", "br", "span", "div", "b", "i", "u", "strong", "em", "ul", "ol", "li", "a", "img", "h1", "h2", "h3", "blockquote"
])
        allowed_attrs = {
            "*": ["style", "class"],
            "a": ["href", "title", "target"],
            "img": ["src", "alt", "width", "height"],
        }
        content = bleach.clean(form.content.data, tags=allowed_tags, attributes=allowed_attrs, strip=True)

        filepath = os.path.join("case_studies", f"{title}.html")
        os.makedirs("case_studies", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return redirect(url_for("case_studies"))
    return render_template("admin_editor.html", form=form)

@app.route("/case-studies")
def case_studies():
    files = [f for f in os.listdir("case_studies") if f.endswith(".html")]
    return render_template("case_studies.html", files=files)

@app.route("/case-study/<name>")
def case_study(name):
    filepath = os.path.join("case_studies", f"{name}.html")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return render_template("post.html", title=name.replace("_", " "), content=Markup(content))
    return "Not found", 404

@app.route("/admin/delete/<name>", methods=["POST"])
@login_required
def admin_delete(name):
    filepath = os.path.join("case_studies", f"{name}.html")
    if os.path.exists(filepath):
        os.remove(filepath)
        flash("Case study deleted.", "success")
    else:
        flash("Case study not found.", "error")
    return redirect(url_for("case_studies"))

@app.route("/admin/upload_image", methods=["POST"])
@login_required
def upload_image():
    image = request.files.get('image')
    if image:
        filename = image.filename.replace(" ", "_")
        filepath = os.path.join("static", "images", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        image.save(filepath)
        url = url_for('static', filename=f"images/{filename}")
        return {"url": url}
    return {"error": "No image uploaded"}, 400

@app.route("/mise")
def mise():
    return render_template("mise.html", title="Mise")

@app.route("/method")
def method():
    return render_template("method.html", title="Method")

@app.route("/mastery")
def mastery():
    return render_template("mastery.html", title="Mastery")

@app.route("/")
def index():
    return render_template("index.html", title="Larder Logic")

if __name__ == "__main__":
    app.run(debug=True)

