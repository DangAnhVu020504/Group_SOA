import requests

GATEWAY_URL = "http://127.0.0.1:8000"

def get_user(user_id):
    try:
        r = requests.get(f"{GATEWAY_URL}/users/{user_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def get_book(book_id):
    try:
        r = requests.get(f"{GATEWAY_URL}/books/{book_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None
