from flask import Flask
from views.turn_routes import turn_routes

from model import db
from views.user_routes import user_route


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    app.register_blueprint(user_route)
    app.register_blueprint(turn_routes)
    return app
