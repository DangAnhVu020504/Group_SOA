from flask import Flask, redirect, url_for
from config import Config
from models.database import db
from routes import book_bp
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from service_registry import ServiceRegistry


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(book_bp)

    # Trang chủ chuyển sang danh sách sách
    @app.route('/')
    def home():
        return redirect(url_for('book_bp.list_books'))

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    service_registry = ServiceRegistry('book-service', 5002)
    service_registry.register()
    try:
        app.run(host='127.0.0.1', port=5002, debug=True)
    finally:
        service_registry.deregister()
