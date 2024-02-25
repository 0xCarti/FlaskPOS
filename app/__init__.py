from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getenv

from flask_wtf import CSRFProtect

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = getenv('SECRET_KEY', 'a_default_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///flaskpos.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CSRFProtect(app)
    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes
        from .routes import item, event, transaction, screen  # Import the blueprint

        app.register_blueprint(item)
        app.register_blueprint(event)
        app.register_blueprint(transaction)
        app.register_blueprint(screen)
        db.create_all()  # Create sql tables for our data models

    return app
