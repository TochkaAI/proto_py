from flask import Flask
from flask_login import LoginManager

from .routes import routes as blueprint_routes
from .auth import auth as blueprint_auth
from .database import db
from .models import *


def create_app():
    """Construct the core application."""
    app = Flask(__name__,
                static_url_path='',
                static_folder='web/static',
                template_folder='web/templates'
                )
    app.config.from_pyfile('config.py')
    app.secret_key = "super secret key"

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    app.config.from_object('rest_service.config')
    app.register_blueprint(blueprint_auth)
    app.register_blueprint(blueprint_routes)

    @app.cli.command("init-db")
    def init_db():
        db.create_all()

        new_user = User(name='admin', pswd='admin')
        db.session.add(new_user)
        db.session.commit()

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    return app