import requests
import os
from pyramid.view import view_config
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = os.environ.get("NEWS_API_KEY")
SOURCES = [
    {
        "name": "tesla",
        "url": f"https://newsapi.org/v2/everything?q=tesla&sortBy=publishedAt&apiKey={API_KEY}",
    },
    {
        "name": "bitcoin",
        "url": f"https://newsapi.org/v2/everything?q=bitcoin&sortBy=publishedAt&apiKey={API_KEY}",
    },
    {
        "name": "microsoft",
        "url": f"https://newsapi.org/v2/everything?q=microsoft&sortBy=publishedAt&apiKey={API_KEY}",
    },
]


@view_config(route_name="news", renderer="json")
def news(request):
    if not API_KEY:
        return {"error": "API key missing"}

    with ThreadPoolExecutor() as executor:
        future_to_news_data = {
            executor.submit(requests.get, url=source["url"]): source
            for source in SOURCES
        }

        response = {
            future_to_news_data[future]["name"]: future.result().json()
            for future in as_completed(future_to_news_data)
        }

    request.response.status = 200
    return response


def includeme(config):
    config.add_route("news", "/")
