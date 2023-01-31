import requests
from typing import Dict
from pyramid.view import view_config
from concurrent.futures import ThreadPoolExecutor, as_completed
from news_data.lib import get_url

def get_data():
    return [
        {
            "source": "",
            "url": get_url(topic="tesla"),
        },
        {
            "source": "",
            "url": get_url(topic="bitcoin"),
        },
        {
            "source": "",
            "url": get_url(topic="microsoft"),
        },
    ]


@view_config(route_name="news", renderer="json")
def news(request):
    sources = get_data()
    futures = []
    with ThreadPoolExecutor() as executor:

        for source in sources:
            futures.append(executor.submit(requests.get, url=source["url"]))

        for future in as_completed(futures):
            print(future.result())

    request.response.status = 200
    return {}


def includeme(config):
    config.add_route("news", "/")
