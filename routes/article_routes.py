from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db, Article, Tag, Image
from forms.WTForm import ArticleForm
from datetime import datetime

article_bp = Blueprint("article", __name__)

# -----------------------------
# List Articles
# -----------------------------
@article_bp.route('/admin/articles/list')
@login_required
def admin_list_articles():
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template('admin/list_articles.html', articles=articles)


# -----------------------------
# Create New Article
# -----------------------------
@article_bp.route('/admin/articles/new', methods=['GET', 'POST'])
@login_required
def admin_new_article():
    form = ArticleForm()
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        article = Article(title=title, content=content, timestamp=datetime.utcnow())

        # Tags from multi-select
        selected_tag_ids = form.tags.data if hasattr(form, 'tags') else []
        article.tags = [Tag.query.get(int(tid)) for tid in selected_tag_ids if Tag.query.get(int(tid))]

        # Tags from comma-separated input
        extra_tags = request.form.get("extra_tags", "")
        if extra_tags:
            for name in [t.strip() for t in extra_tags.split(",") if t.strip()]:
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name)
                    db.session.add(tag)
                article.tags.append(tag)

        db.session.add(article)
        db.session.commit()

        flash("Article created!", "success")
        return redirect(url_for('dashboard.admin_dashboard'))

    return render_template('admin/new_article.html', form=form)


# -----------------------------
# Edit Article
# -----------------------------
@article_bp.route('/admin/articles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_article(id):
    article = Article.query.get_or_404(id)
    form = ArticleForm(obj=article)

    all_tags = Tag.query.order_by(Tag.name).all()
    linked_tag_ids = [tag.id for tag in article.tags]
    unlinked_tags = [tag for tag in all_tags if tag.id not in linked_tag_ids]
    form.tags.choices = [(tag.id, tag.name) for tag in unlinked_tags]
    form.tags.data = []

    # Only run update logic if this is NOT a remove_tag POST
    if request.method == 'POST' and 'remove_tag' not in request.form:
        article.title = form.title.data
        article.content = form.content.data

        # Tags from multi-select
        selected_tag_ids = request.form.getlist('tags')
        selected_tags = [Tag.query.get(int(tid)) for tid in selected_tag_ids if tid.isdigit()]

        # New tags from comma-separated input
        extra_tags_raw = request.form.get('extra_tags', '')
        extra_tag_names = [t.strip() for t in extra_tags_raw.split(',') if t.strip()]

        added_tags = []
        already_present = []

        for tag_name in extra_tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.flush()
                added_tags.append(tag_name)
            else:
                already_present.append(tag_name)
            selected_tags.append(tag)

        # Assign combined tags
        article.tags = selected_tags

        db.session.commit()

        if added_tags:
            flash(f"Added tags: {', '.join(added_tags)}", "success")
        if already_present:
            flash(f"Already present: {', '.join(already_present)}", "info")
        return redirect(url_for('dashboard.admin_dashboard'))

    return render_template('admin/edit_article.html', form=form, article=article)


# -----------------------------
# Delete Article
# -----------------------------
@article_bp.route('/admin/articles/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash("Article deleted!", "success")
    return redirect(url_for('article.admin_list_articles'))


# -----------------------------
# Link Images to Article
# -----------------------------
@article_bp.route('/admin/articles/<int:article_id>/link_images', methods=['GET', 'POST'])
@login_required
def admin_link_images_to_article(article_id):
    article = Article.query.get_or_404(article_id)
    images = Image.query.order_by(Image.created_at.desc()).all()

    if request.method == 'POST':
        selected_image_ids = request.form.getlist('image_ids')

        # Reset links and add new ones
        article.images = []
        for image_id in selected_image_ids:
            image = Image.query.get(int(image_id))
            if image:
                article.images.append(image)

        db.session.commit()
        flash("Images linked to article!", "success")
        return redirect(url_for('article.admin_list_articles'))

    linked_ids = [img.id for img in article.images]
    return render_template('admin/link_images.html', article=article, images=images, linked_ids=linked_ids)


# -----------------------------
# Remove Tag from Article
# -----------------------------
@article_bp.route('/admin/articles/<int:article_id>/remove-tag/<int:tag_id>', methods=['POST'])
@login_required
def admin_remove_tag_from_article(article_id, tag_id):
    article = Article.query.get_or_404(article_id)
    tag = Tag.query.get_or_404(tag_id)
    if tag in article.tags:
        article.tags.remove(tag)
        db.session.commit()
        flash(f"Tag '{tag.name}' removed from article.", "success")
    return redirect(url_for('article.admin_edit_article', id=article_id))
