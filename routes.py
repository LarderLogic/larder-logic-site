from flask import Blueprint, render_template, request, redirect, url_for, flash
from markupsafe import Markup
from models import db, Article, Image, Tag, User
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user
from forms.WTForm import LoginForm, EditorForm, RegistrationForm, ArticleForm, ImageUploadForm
import bleach, os

routes = Blueprint('routes', __name__)

# -----------------------------
# ENTRIES
# -----------------------------
@routes.route('/entries')
def list_entries():
    entries = Article.query.all()
    return render_template('entries/list.html', entries=entries)

@routes.route('/entries/new', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        entry = Article(title=title, content=content)
        db.session.add(entry)
        db.session.commit()

        flash("Entry created!")
        return redirect(url_for('routes.list_entries'))

    return render_template('entries/new.html')

@routes.route('/entries/<int:id>')
def view_entry(id):
    entry = Article.query.get_or_404(id)
    return render_template('entries/view.html', entry=entry)

# -----------------------------
# IMAGES
# -----------------------------
@routes.route('/images')
def list_images():
    images = Image.query.all()
    return render_template('images/list.html', images=images)

@routes.route('/images/new', methods=['GET', 'POST'])
def new_image():
    if request.method == 'POST':
        filename = request.form['filename']
        caption = request.form['caption']

        image = Image(filename=filename, caption=caption)
        db.session.add(image)
        db.session.commit()

        flash("Image uploaded!")
        return redirect(url_for('routes.list_images'))

    return render_template('images/new.html')

@routes.route('/images/<int:id>')
def view_image(id):
    image = Image.query.get_or_404(id)
    return render_template('images/view.html', image=image)

# -----------------------------
# TAGS
# -----------------------------
@routes.route('/tags')
def list_tags():
    tags = Tag.query.all()
    return render_template('tags/list.html', tags=tags)

@routes.route('/tags/new', methods=['GET', 'POST'])
def new_tag():
    if request.method == 'POST':
        name = request.form['name']

        # Prevent duplicate tags
        existing = Tag.query.filter_by(name=name).first()
        if existing:
            flash("Hey! That tag already exists, dumb dumb.")
            return redirect(url_for('routes.list_tags'))

        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()

        flash("Tag created!")
        return redirect(url_for('routes.list_tags'))

    return render_template('tags/new.html')

# -----------------------------
# LOGIN/LOGOUT
# -----------------------------
@routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("routes.admin_editor"))
        else:
            flash("Invalid username or password.", "error")
    return render_template("admin_login.html", form=form)

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("routes.login"))

@routes.route("/admin_login.html", methods=["GET", "POST"])
def admin_login():
    form = LoginForm()
    if request.method == "POST":
        # Add your login logic here
        pass
    return render_template("admin_login.html", form=form)

@routes.route("/admin_editor.html", methods=["GET", "POST"])
@login_required
def admin_editor():
    form = EditorForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        article = Article(title=title, content=content)
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
            article.tags.append(tag)
        db.session.add(article)
        db.session.commit()
        flash("Article created!")
        return redirect(url_for('routes.list_entries'))
    return render_template("admin_editor.html", form=form)

@routes.route("/admin/save", methods=["POST"])
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

        return redirect(url_for("routes.case_studies"))
    return render_template("admin_editor.html", form=form)

@routes.route("/case-studies")
def case_studies():
    files = [f for f in os.listdir("case_studies") if f.endswith(".html")]
    return render_template("case_studies.html", files=files)

@routes.route("/case-study/<name>")
def case_study(name):
    filepath = os.path.join("case_studies", f"{name}.html")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return render_template("post.html", title=name.replace("_", " "), content=Markup(content))
    return "Not found", 404

@routes.route("/admin/delete/<name>", methods=["POST"])
@login_required
def admin_delete(name):
    filepath = os.path.join("case_studies", f"{name}.html")
    if os.path.exists(filepath):
        os.remove(filepath)
        flash("Case study deleted.", "success")
    else:
        flash("Case study not found.", "error")
    return redirect(url_for("routes.case_studies"))

# For articles
@routes.route('/new_article', methods=['GET', 'POST'])
def new_article():
    form = ArticleForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        article = Article(title=title, content=content)
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
            article.tags.append(tag)
        db.session.add(article)
        db.session.commit()
        flash("Article created!")
        return redirect(url_for('routes.list_entries'))
    return render_template('new_article.html', form=form)

# For images
@routes.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    form = ImageUploadForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        upload_path = os.path.join('static', 'images', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        image_file.save(upload_path)
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        image = Image(filename=filename)
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
            image.tags.append(tag)
        db.session.add(image)
        db.session.commit()
        flash('Image uploaded and tagged!', 'success')
        return redirect(url_for('routes.upload_image'))
    return render_template('upload_image.html', form=form)

@routes.route("/mise")
def mise():
    return render_template("mise.html", title="Mise")

@routes.route("/method")
def method():
    return render_template("method.html", title="Method")

@routes.route("/mastery")
def mastery():
    return render_template("mastery.html", title="Mastery")

@routes.route("/")
def index():
    return render_template("index.html", title="Larder Logic")

# -----------------------------
# REGISTER
# -----------------------------
@routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("Username already exists.", "error")
            return redirect(url_for('routes.register'))
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form)
