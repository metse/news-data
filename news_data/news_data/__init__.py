from pyramid.config import Configurator


def main(global_config, **settings):
    with Configurator(settings=settings) as config:
        config.include('.app')
        config.scan()
    return config.make_wsgi_app()
