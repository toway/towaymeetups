from pyramid.i18n import TranslationStringFactory
from pyramid.config import Configurator
import kotti
import sqlalchemy


_ = TranslationStringFactory('mba')


def includeme(config):
    settings = config.get_settings()

    #confic with kotti gallery
    #config.add_static_view('mba_static', 'mba_static', cache_max_age=3600)
    #config.add_static_view('static', 'deform:static')
    config.add_static_view('static', 'static')

    config.include('kotti')
    #config.include('kotti.views.login')
    config.include('mba.views')

    config.include('mba.override')
    #config.add_route('home', '/')
    #config.add_route('register','/register')
    #config.scan(__name__)


default_settings = {
    #'pyramid.includes': 'mba mba.views',
    'kotti.authn_policy_factory': 'kotti.authtkt_factory',
    #'kotti.base_includes': (
    #    'kotti kotti.views kotti.views.login kotti.views.users'),
    #TODO add all? 15/01/14 11:51:20
    'kotti.base_includes': ' '.join([
        'kotti',
        'kotti.events',
        'kotti.views',
        'kotti.views.cache',
        #'kotti.views.view',
        'kotti.views.edit',
        'kotti.views.edit.actions',
        #'kotti.views.edit.content',
        'kotti.views.edit.default_views',
        'kotti.views.edit.upload',
        'kotti.views.file',
        #'kotti.views.image',
        'kotti.views.login',
        'kotti.views.navigation',
        'kotti.views.users',
        ]),
    'kotti.fanstatic.edit_needed': '',
    'kotti.fanstatic.view_needed': '',
    'kotti.use_tables': '',
    'kotti.populators': 'kotti.populate.populate mba.populate.populate', 
    'kotti.principals_factory': 'mba.security.principals_factory',
    'kotti.root_factory': 'kotti.resources.default_get_root',
    'kotti.site_title': 'MBA',

    'mba.avatar_prefix': '/fanstatic/mba/img/avatars',
    'mba.register.group': 'viewer', #TODO: format alright ?
    'mba.register.role': '',
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

    engine = sqlalchemy.engine_from_config(config.registry.settings
            , 'sqlalchemy.')
    kotti.resources.initialize_sql(engine)
    return config.make_wsgi_app()

    '''
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('register','/register')
    config.add_route('resume_edit','/resume_edit')
    config.add_route('resume_preview','/resume_preview')
    config.add_route('job','/job')
    
    config.scan()
    return config.make_wsgi_app()
    '''


# def kotti_configure(settings):
#     settings['kotti.fanstatic.view_needed'] +=\
#         ' mba.fanstatic.mba_group'
