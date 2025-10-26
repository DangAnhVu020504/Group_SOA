from flask import Flask, redirect, url_for
from config import Config
from models.database import db
from routes import borrow_bp
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from service_registry import ServiceRegistry


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(borrow_bp)

    # Route cho trang chủ chuyển sang trang giới thiệu
    @app.route('/')
    def home():
        return redirect(url_for('borrow_bp.home'))

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    service_registry = ServiceRegistry('borrow-service', 5003)
    service_registry.register()
    try:
        app.run(host='127.0.0.1', port=5003, debug=True)
    finally:
        service_registry.deregister()
