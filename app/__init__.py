from flask import Flask
import logging
import sys

from app.routes import webhook_blueprint


def create_app():
    app = Flask(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    app.register_blueprint(webhook_blueprint)

    return  app
