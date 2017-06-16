from flask import Flask
from model import db
from views import api


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    app.register_blueprint(api)
    return app
