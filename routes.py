from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .article_routes import article_bp
from .image_routes import image_bp
from .tag_routes import tag_bp
from .contact_routes import contact_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(article_bp, url_prefix="/articles")
    app.register_blueprint(image_bp, url_prefix="/images")
    app.register_blueprint(tag_bp, url_prefix="/tags")
    app.register_blueprint(contact_bp, url_prefix="/contacts")
