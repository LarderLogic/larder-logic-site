from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Association table for many-to-many relationship between Articles and Tags
article_tags = db.Table(
    'article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# Association table for many-to-many relationship between Images and Tags
image_tags = db.Table(
    'image_tags',
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Many-to-many with Tag
    tags = db.relationship(
        'Tag',
        secondary=article_tags,
        backref=db.backref('articles', lazy='dynamic')
    )

    # Relationship to Images (one-to-many)
    images = db.relationship('Image', backref='article', lazy=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # stored in /static/images or uploads
    alt_text = db.Column(db.String(255))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)

    # Many-to-many with Tag
    tags = db.relationship(
        'Tag',
        secondary=image_tags,
        backref=db.backref('images', lazy='dynamic')
    )

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="admin")
