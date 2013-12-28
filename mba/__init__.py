from pyramid.i18n import TranslationStringFactory
from pyramid.config import Configurator


_ = TranslationStringFactory('mba')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()

# def kotti_configure(settings):
#     settings['kotti.fanstatic.view_needed'] +=\
#         ' mba.fanstatic.mba_group'
