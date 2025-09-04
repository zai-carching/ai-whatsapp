from flask import Flask
import logging
import sys

import config
from app.routes.whatsapp import whatsapp_blueprint
from app.routes.sync import sync_blueprint
from app.extensions import db

def create_app():
    app = Flask(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(whatsapp_blueprint)
    app.register_blueprint(sync_blueprint)

    return  app
