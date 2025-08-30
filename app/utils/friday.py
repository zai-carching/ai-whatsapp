import config
import requests


def get_ai_context():
    url = f"{config.FRIDAY_API_URL}/api/ai-context"
    response = requests.get(url)
    return response.json()

