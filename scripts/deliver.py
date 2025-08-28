import asyncio
import requests
import config

RECIPIENT_ID = "959987304010"

async def deliver_test_message():
    url = f"https://graph.facebook.com/{config.WHATSAPP_API_VERSION}/{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_ID,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }
    }
    response = await asyncio.to_thread(
        requests.post, url, json=payload, headers=headers, timeout=10
    )
    print(response.status_code, response.text)

if __name__ == "__main__":
    asyncio.run(deliver_test_message())