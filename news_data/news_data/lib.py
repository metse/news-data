import os

BASE_URL = "https://newsapi.org/v2"

def get_url(topic: str):
    api_key = os.environ.get("NEWS_API_KEY") or ""
    if not api_key:
        return

    return f"{BASE_URL}/everything?q={topic}sortBy=publishedAt&apiKey={api_key}"
