from flask import Blueprint
from app.utils import friday

sync_blueprint = Blueprint("sync", __name__)

@sync_blueprint.route('/sync', methods=['POST'])
def sync():
    context = friday.get_ai_context()

    return context