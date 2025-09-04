from app.extensions import db
from datetime import datetime

class WhatsappMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text)
    text = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.Text, nullable=True)
    is_received = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
