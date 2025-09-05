from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required
from models import db, Image, Tag, Article
import os, uuid

image_bp = Blueprint("image", __name__)

# -----------------------------
# LIST IMAGES
# -----------------------------
@image_bp.route('/admin/images', methods=['GET'])
@login_required
def admin_images():
    images = Image.query.order_by(Image.created_at.desc()).all()
    articles = {a.id: a for a in Article.query.all()}
    return render_template('admin/list_images.html', images=images, articles=articles)


@image_bp.route('/admin/images/list')
@login_required
def admin_list_images():
    images = Image.query.order_by(Image.created_at.desc()).all()
    articles = {a.id: a for a in Article.query.all()}
    return render_template('admin/list_images.html', images=images, articles=articles)


# -----------------------------
# SINGLE UPLOAD
# -----------------------------
@image_bp.route('/admin/images/upload', methods=['GET'])
@login_required
def admin_upload_images():
    return render_template('admin/upload_images.html')


@image_bp.route('/admin/images/upload', methods=['POST'])
@login_required
def admin_upload_image():
    file = request.files.get('image')
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[-1]
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        upload_path = os.path.join('static', 'uploads', unique_name)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        image = Image(filename=unique_name, alt_text=request.form.get('alt_text', ''))
        db.session.add(image)
        db.session.commit()
        flash("Image uploaded!", "success")
        return redirect(url_for('image.admin_list_images'))
    flash("No image selected.", "error")
    return redirect(url_for('image.admin_upload_images'))


# -----------------------------
# BULK UPLOAD + STAGING
# -----------------------------
@image_bp.route('/admin/images/bulk_upload', methods=['POST'])
@login_required
def admin_bulk_upload_images():
    files = request.files.getlist('images')
    pending = []
    for file in files:
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1]
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            upload_path = os.path.join('static', 'uploads', unique_name)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)
            pending.append(unique_name)
    session['pending_uploads'] = pending
    flash(f"{len(pending)} images staged for tagging.", "success")
    return redirect(url_for('image.admin_stage_images'))


@image_bp.route('/admin/images/stage', methods=['GET', 'POST'])
@login_required
def admin_stage_images():
    pending = session.get('pending_uploads', [])
    tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        images_data = []
        new_pending = []
        for filename in pending:
            if not request.form.get(f'remove_{filename}'):
                alt_text = request.form.get(f'alt_{filename}', '')
                tag_ids = request.form.getlist(f'tags_{filename}')
                existing_tag_ids = request.form.getlist(f'existing_tags_{filename}')
                new_tags_raw = request.form.get(f'new_tags_{filename}', '')
                new_tag_names = [t.strip() for t in new_tags_raw.split(',') if t.strip()]
                new_tag_objs = []
                for name in new_tag_names:
                    tag = Tag.query.filter_by(name=name).first()
                    if not tag:
                        tag = Tag(name=name)
                        db.session.add(tag)
                        db.session.commit()
                    new_tag_objs.append(tag)
                all_tags = [Tag.query.get(int(tid)) for tid in existing_tag_ids if tid.isdigit()] + new_tag_objs
                images_data.append((filename, alt_text, tag_ids))
                new_pending.append(filename)
            else:
                file_path = os.path.join('static', 'uploads', filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        for filename, alt_text, tag_ids in images_data:
            image = Image(filename=filename, alt_text=alt_text)
            for tag_id in tag_ids:
                tag = Tag.query.get(int(tag_id))
                if tag:
                    image.tags.append(tag)
            db.session.add(image)
        db.session.commit()
        session['pending_uploads'] = new_pending
        flash("Images uploaded and tagged!", "success")
        return redirect(url_for('image.admin_list_images'))
    return render_template('admin/stage_images.html', pending=pending, tags=tags)


# -----------------------------
# IMAGE EDIT / DELETE / LINKS
# -----------------------------
@image_bp.route('/admin/images/<int:image_id>/add_tag', methods=['GET', 'POST'])
@login_required
def admin_add_tag_to_image(image_id):
    image = Image.query.get_or_404(image_id)
    tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        tag_ids = request.form.getlist('tags')
        image.tags = [Tag.query.get(int(tid)) for tid in tag_ids if Tag.query.get(int(tid))]
        db.session.commit()
        flash("Tags added to image!", "success")
        return redirect(url_for('image.admin_list_images'))
    return render_template('admin/add_tag_to_image.html', image=image, tags=tags)


@image_bp.route('/admin/images/<int:image_id>/link_article', methods=['GET', 'POST'])
@login_required
def admin_link_article_to_image(image_id):
    image = Image.query.get_or_404(image_id)
    articles = Article.query.order_by(Article.title).all()
    if request.method == 'POST':
        article_id = request.form.get('article_id')
        image.article_id = int(article_id) if article_id and article_id.isdigit() else None
        db.session.commit()
        flash("Article linked to image!", "success")
        return redirect(url_for('image.admin_list_images'))
    return render_template('admin/link_article_to_image.html', image=image, articles=articles)


@image_bp.route('/admin/images/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_image(id):
    image = Image.query.get_or_404(id)
    tags = Tag.query.order_by(Tag.name).all()
    articles = Article.query.order_by(Article.title).all()
    current_tag_ids = [tag.id for tag in image.tags]
    current_article_id = image.article_id
    if request.method == 'POST':
        image.title = request.form.get('title', '')
        image.description = request.form.get('description', '')
        image.alt_text = request.form.get('alt_text', '')
        tag_ids = request.form.getlist('tags')
        image.tags = [Tag.query.get(int(tid)) for tid in tag_ids if Tag.query.get(int(tid))]
        article_id = request.form.get('article_id')
        image.article_id = int(article_id) if article_id and article_id.isdigit() else None
        db.session.commit()
        flash("Image updated!", "success")
        return redirect(url_for('dashboard.admin_dashboard'))
    return render_template(
        'admin/edit_image.html',
        image=image,
        tags=tags,
        articles=articles,
        current_tag_ids=current_tag_ids,
        current_article_id=current_article_id
    )


@image_bp.route('/admin/images/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_image(id):
    image = Image.query.get_or_404(id)
    file_path = os.path.join('static', 'uploads', image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(image)
    db.session.commit()
    flash("Image deleted!", "success")
    return redirect(request.referrer or url_for('image.admin_images'))

