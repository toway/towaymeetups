from pyramid.i18n import TranslationStringFactory
from pyramid.config import Configurator
import kotti
import sqlalchemy

_ = TranslationStringFactory('mba')

def includeme(config):
    settings = config.get_settings()
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.include('kotti')
    #config.include('kotti.views.login')
    config.include('mba.views')
    #config.add_route('home', '/')
    #config.add_route('register','/register')
    #config.scan(__name__)

default_settings = {
    #'pyramid.includes': 'mba mba.views',
    'kotti.authn_policy_factory': 'kotti.authtkt_factory',
    'kotti.base_includes': (
        'kotti kotti.views kotti.views.login kotti.views.users'),
    'kotti.use_tables': 'principals',
    'kotti.populators': 'kotti.populate.populate',
    'kotti.principals_factory': 'kotti.security.Principals',
    'kotti.root_factory': 'kotti.resources.default_get_root',
    'kotti.site_title': 'MBA',
    }

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings2 = default_settings.copy()
    settings2.update(settings)
    config = kotti.base_configure(global_config, **settings2)

    #config.add_static_view('static', 'static', cache_max_age=3600)
    #config.add_route('home', '/')
    #config.add_route('register','/register')

    engine = sqlalchemy.engine_from_config(config.registry.settings, 'sqlalchemy.')
    kotti.resources.initialize_sql(engine)
    return config.make_wsgi_app()
    
    '''
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('register','/register')
    config.scan()
    return config.make_wsgi_app()
    '''

# def kotti_configure(settings):
#     settings['kotti.fanstatic.view_needed'] +=\
#         ' mba.fanstatic.mba_group'
