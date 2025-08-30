from flask import Flask
import logging
import sys

from app.routes.whatsapp import whatsapp_blueprint
from app.routes.sync import sync_blueprint


def create_app():
    app = Flask(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    app.register_blueprint(whatsapp_blueprint)
    app.register_blueprint(sync_blueprint)

    return  app
