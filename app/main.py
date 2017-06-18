from flask import Flask
from app.views.user_routes import user_route

from app.model import db
from app.views.turn_routes import turn_routes


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    app.register_blueprint(user_route)
    app.register_blueprint(turn_routes)

    @app.route('/')
    def index():
        return "Here will be usage instructions for api"

    return app
