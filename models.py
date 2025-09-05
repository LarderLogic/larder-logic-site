from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

# Association table for many-to-many relationship between Articles and Tags
article_tags = db.Table(
    'article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

# Association table for many-to-many relationship between Images and Tags
image_tags = db.Table(
    'image_tags',
    db.Column('image_id', db.Integer, db.ForeignKey('image.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    tags = db.relationship("Tag", secondary=article_tags, backref="articles")
    images = db.relationship("Image", backref="article", lazy=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    alt_text = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    tags = db.relationship("Tag", secondary=image_tags, backref="images")
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))  # <-- Add this line

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="admin")

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    reviewed = db.Column(db.Boolean, default=False)
