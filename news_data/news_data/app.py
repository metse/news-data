import requests
from pyramid.view import view_config
from concurrent.futures import ThreadPoolExecutor, as_completed
from news_data.lib import get_url

SOURCES = [
    {
        "name": "tesla",
        "url": get_url(topic="tesla"),
    },
    {
        "name": "bitcoin",
        "url": get_url(topic="bitcoin"),
    },
    {
        "name": "microsoft",
        "url": get_url(topic="microsoft"),
    },
]


@view_config(route_name="news", renderer="json")
def news(request):

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
