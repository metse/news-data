from pyramid.view import view_config

@view_config(route_name="news", renderer="json")
def news(request):
    request.response.status = 200
    return {"success": "true"}


def includeme(config):
    config.add_route("news", "/")
