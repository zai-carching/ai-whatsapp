import logging

from app import create_app
from app.extensions import db


app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Initializing database...")

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=5000)