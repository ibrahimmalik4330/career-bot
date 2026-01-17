import requests
from config.settings import PUSHOVER_TOKEN, PUSHOVER_USER

def push(message: str) -> None:
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        return

    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            timeout=5,
            data={
                "token": PUSHOVER_TOKEN,
                "user": PUSHOVER_USER,
                "message": message,
            },
        )
    except requests.RequestException:
        pass
