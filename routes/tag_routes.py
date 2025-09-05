from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db, Tag, Article, Image
from forms.WTForm import TagForm

tag_bp = Blueprint("tag", __name__)

@tag_bp.route('/admin/tags/list')
@login_required
def admin_list_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    form = TagForm()
    return render_template('admin/tags_list.html', tags=tags, form=form)

@tag_bp.route('/admin/tags/new', methods=['GET', 'POST'])
@login_required
def admin_new_tag():
    form = TagForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        if Tag.query.filter_by(name=name).first():
            flash("That tag already exists.", "error")
            return redirect(url_for('tag.admin_new_tag'))
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        flash("Tag created!", "success")
        return redirect(url_for('dashboard.admin_dashboard'))
    return render_template('admin/tags_new.html', form=form)

@tag_bp.route('/admin/tags/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_tag(id):
    tag = Tag.query.get_or_404(id)
    form = TagForm(obj=tag)
    articles_with_tag = Article.query.filter(Article.tags.any(id=id)).all()
    images_with_tag = Image.query.filter(Image.tags.any(id=id)).all()
    if form.validate_on_submit():
        tag.name = form.name.data.strip()
        db.session.commit()
        flash("Tag updated successfully.", "success")
        return redirect(url_for('dashboard.admin_dashboard'))
    return render_template(
        'admin/tags_edit.html',
        form=form,
        tag=tag,
        articles_with_tag=articles_with_tag,
        images_with_tag=images_with_tag
    )

@tag_bp.route('/admin/tags/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash("Tag deleted!", "success")
    return redirect(url_for('tag.admin_list_tags'))

@tag_bp.route('/admin/tags/<int:tag_id>/add', methods=['POST'])
@login_required
def admin_add_tag_to_items(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    # Logic to add the tag to items
    flash(f"Tag '{tag.name}' added to items!", "success")
    return redirect(url_for('tag.admin_list_tags'))

@tag_bp.route('/admin/tags/<int:tag_id>/link_articles', methods=['GET', 'POST'])
@login_required
def admin_link_articles_to_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    articles = Article.query.order_by(Article.title.asc()).all()
    if request.method == 'POST':
        selected_ids = request.form.getlist('article_ids')
        tag.articles = [Article.query.get(int(aid)) for aid in selected_ids if Article.query.get(int(aid))]
        db.session.commit()
        flash("Articles linked to tag!", "success")
        return redirect(url_for('tag.admin_list_tags'))
    linked_ids = [a.id for a in tag.articles]
    return render_template(
        'admin/link_articles_to_tag.html',
        tag=tag,
        articles=articles,
        linked_ids=linked_ids
    )

@tag_bp.route('/admin/tags/<int:tag_id>/linked_articles')
@login_required
def admin_view_linked_articles(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    articles = tag.articles
    return render_template('admin/linked_articles.html', tag=tag, articles=articles)

@tag_bp.route('/admin/tags/<int:tag_id>/linked_images')
@login_required
def admin_view_linked_images(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    images = tag.images
    return render_template('admin/linked_images.html', tag=tag, images=images)
