from functools import wraps
from flask import jsonify, request
import logging
import hashlib
import hmac
import config


def validate_whatsapp_signature(payload, signature):
    """
    Validate the incoming payload's signature against our expected signature
    """
    try:
        app_secret = config.WHATSAPP_APP_SECRET
        expected_signature = hmac.new(
            bytes(app_secret, "latin-1"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        logging.debug(f"Payload: {payload[:100]}...")  # Log first 100 chars
        logging.debug(f"Expected signature: {expected_signature}")
        logging.debug(f"Received signature: {signature}")

        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logging.error(f"Signature validation error: {str(e)}")
        return False


def whatsapp_signature_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        raw_signature = request.headers.get("X-Hub-Signature-256", "")
        logging.debug(f"Raw signature header: {raw_signature}")

        if not raw_signature.startswith("sha256="):
            logging.error("Missing sha256= prefix in signature")
            return jsonify({"status": "error", "message": "Invalid signature format"}), 403

        signature = raw_signature[7:]  # Remove 'sha256='
        if not validate_whatsapp_signature(request.data.decode("utf-8"), signature):
            logging.error("Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403

        return f(*args, **kwargs)

    return decorated_function