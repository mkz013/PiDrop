from flask import Flask
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .extensions import db
    db.init_app(app)

    from .models import file_record

    with app.app_context():
        db.create_all()

    from .routes.upload import upload_bp
    from .routes.dashboard import dashboard_bp
    from .routes.browser import browser_bp
    from .routes.download import download_bp
    
    app.register_blueprint(upload_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(browser_bp)
    app.register_blueprint(download_bp)

    return app