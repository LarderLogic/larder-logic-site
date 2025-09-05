from flask import Blueprint
from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
# Add other blueprints as you split up your routes
# from .article_routes import article_bp
# from .tag_routes import tag_bp
# from .image_routes import image_bp
# from .contact_routes import contact_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    # Register other blueprints here as you create them
    # app.register_blueprint(article_bp)
    # app.register_blueprint(tag_bp)
    # app.register_blueprint(image_bp)
    # app.register_blueprint(contact_bp)