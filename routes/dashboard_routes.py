from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, Article, Image, Tag, ContactMessage
from datetime import datetime, timedelta

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    cutoff = datetime.utcnow() - timedelta(days=60)
    old_msgs = ContactMessage.query.filter(ContactMessage.created_at < cutoff).all()
    for msg in old_msgs:
        db.session.delete(msg)
    db.session.commit()

    article_count = Article.query.count()
    image_count = Image.query.count()
    tag_count = Tag.query.count()
    new_message_count = ContactMessage.query.filter_by(reviewed=False).count()

    ticker_messages = ContactMessage.query.filter_by(reviewed=False)\
        .order_by(ContactMessage.created_at.desc()).limit(10).all()
    latest_articles = Article.query.order_by(Article.timestamp.desc()).limit(5).all()
    latest_images = Image.query.order_by(Image.created_at.desc()).limit(5).all()
    tags = Tag.query.all()

    return render_template(
        "admin/admin_dashboard.html",
        article_count=article_count,
        image_count=image_count,
        tag_count=tag_count,
        new_message_count=new_message_count,
        ticker_messages=ticker_messages,
        latest_articles=latest_articles,
        latest_images=latest_images,
        tags=tags,
        current_user=current_user
    )
