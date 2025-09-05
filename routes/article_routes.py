from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db, Article, Tag
from forms.WTForm import ArticleForm

article_bp = Blueprint("article", __name__)

@article_bp.route('/admin/articles/list')
@login_required
def admin_list_articles():
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template('admin/list_articles.html', articles=articles)


@article_bp.route('/admin/articles/new', methods=['GET', 'POST'])
@login_required
def admin_new_article():
    form = ArticleForm()
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        article = Article(title=title, content=content)
        article.timestamp = datetime.utcnow()
        selected_tag_ids = form.tags.data if hasattr(form, 'tags') else []
        article.tags = [Tag.query.get(int(tid)) for tid in selected_tag_ids if Tag.query.get(int(tid))]
        db.session.add(article)
        db.session.commit()
        flash("Article created!", "success")
        return redirect(url_for('dashboard.admin_dashboard'))
    return render_template('admin/new_article.html', form=form)


@article_bp.route('/admin/articles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_article(id):
    article = Article.query.get_or_404(id)
    form = ArticleForm(obj=article)
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]
    if form.tags.data is None:
        form.tags.data = [tag.id for tag in article.tags]

    if request.method == 'POST':
        article.title = form.title.data
        article.content = form.content.data

        # Existing tags from select
        selected_tag_ids = request.form.getlist('tags')
        selected_tags = [Tag.query.get(int(tid)) for tid in selected_tag_ids if Tag.query.get(int(tid))]

        # New tags from comma-separated input
        new_tags_raw = request.form.get('new_tags', '')
        new_tag_names = [t.strip() for t in new_tags_raw.split(',') if t.strip()]
        added_tags = []
        already_present = []

        for tag_name in new_tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                if tag in selected_tags or tag in article.tags:
                    already_present.append(tag_name)
                else:
                    selected_tags.append(tag)
                    added_tags.append(tag_name)
            else:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.commit()
                selected_tags.append(tag)
                added_tags.append(tag_name)

        article.tags = selected_tags
        db.session.commit()

        msg = []
        if added_tags:
            msg.append(f"Added tags: {', '.join(added_tags)}.")
        if already_present:
            msg.append(f"Already present: {', '.join(already_present)}.")
        flash(" ".join(msg) or "No tag changes.", "success")

        return redirect(url_for('dashboard.admin_dashboard'))

    return render_template('admin/edit_article.html', form=form, article=article)


@article_bp.route('/admin/articles/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash("Article deleted!", "success")
    return redirect(request.referrer or url_for('article.admin_list_articles'))


@article_bp.route('/admin/articles/<int:article_id>/add_tag', methods=['GET', 'POST'])
@login_required
def admin_add_tag_to_article(article_id):
    article = Article.query.get_or_404(article_id)
    tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        tag_ids = request.form.getlist('tags')
        article.tags = [Tag.query.get(int(tid)) for tid in tag_ids if Tag.query.get(int(tid))]
        db.session.commit()
        flash("Tags added to article!", "success")
        return redirect(url_for('article.admin_list_articles'))
    return render_template('admin/add_tag_to_article.html', article=article, tags=tags)


@article_bp.route('/admin/articles/<int:article_id>/link_images', methods=['GET', 'POST'])
@login_required
def admin_link_images_to_article(article_id):
    article = Article.query.get_or_404(article_id)
    images = Image.query.order_by(Image.created_at.desc()).all()
    if request.method == 'POST':
        image_ids = request.form.getlist('images')
        for image in images:
            if str(image.id) in image_ids:
                image.article_id = article.id
            elif image.article_id == article.id:
                image.article_id = None
        db.session.commit()
        flash("Images linked to article!", "success")
        return redirect(url_for('article.admin_list_articles'))
    return render_template('admin/link_images_to_article.html', article=article, images=images)
