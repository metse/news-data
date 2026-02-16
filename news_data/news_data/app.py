import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from pyramid.view import view_config

NEWS_API_URL = "https://newsapi.org/v2/everything"
TOPICS = ["tesla", "bitcoin", "microsoft"]
REQUEST_TIMEOUT = 10


def fetch_topic(topic, api_key):
    response = requests.get(
        NEWS_API_URL,
        params={"q": topic, "sortBy": "publishedAt", "apiKey": api_key},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


@view_config(route_name="news", renderer="json")
def news(request):
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        request.response.status = 503
        return {"error": "API key missing"}

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(fetch_topic, topic, api_key): topic
            for topic in TOPICS
        }

        response = {}
        for future in as_completed(futures):
            topic = futures[future]
            try:
                response[topic] = future.result()
            except requests.RequestException as exc:
                response[topic] = {"error": str(exc)}

    return response


def includeme(config):
    config.add_route("news", "/")
