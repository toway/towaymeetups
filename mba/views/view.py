import warnings

from pyramid.exceptions import NotFound
from pyramid.renderers import render
from pyramid.view import render_view_to_response
from pyramid.view import view_config

from kotti.interfaces import IContent

from kotti.views.util import search_content
from kotti.views.util import search_content_for_tags

class TemplateStructure(object):
    def __init__(self, html):
        self.html = html

    def __html__(self):
        return self.html
    __unicode__ = __html__

    def __getattr__(self, key):
        return getattr(self.html, key)

class MbaTemplateAPI(object):
    def __init__(self, context, request, bare=None, **kwargs):
        self.context, self.request = context, request

        if getattr(request, 'template_api', None) is None:
            request.template_api = self

    def render_template(self, renderer, **kwargs):
        return TemplateStructure(render(renderer, kwargs, self.request))

@view_config()
def view_content_default(context, request):
    """This view is always registered as the default view for any Content.

    Its job is to delegate to a view of which the name may be defined
    per instance.  If a instance level view is not defined for
    'context' (in 'context.defaultview'), we will fall back to a view
    with the name 'view'.
    """
    print 'mba view_content_default'
    view_name = context.default_view or 'view'
    response = render_view_to_response(context, request, name=view_name)
    if response is None:  # pragma: no coverage
        warnings.warn("Failed to look up default view called %r for %r." %
                      (view_name, context))
        raise NotFound()
    return response

def view_node(context, request):  # pragma: no coverage
    return {}  # BBB


@view_config(name='search-results', permission='view',
             renderer='kotti:templates/view/search-results.pt')
def search_results(context, request):
    results = []
    if u'search-term' in request.POST:
        search_term = request.POST[u'search-term']
        results = search_content(search_term, request)
    return {'results': results}


@view_config(name='search-tag', permission='view',
             renderer='kotti:templates/view/search-results.pt')
def search_results_for_tag(context, request):
    results = []
    if u'tag' in request.GET:
        # Single tag searching only, is allowed in default Kotti. Add-ons can
        # utilize search_content_for_tags(tags) to enable multiple tags
        # searching, but here it is called with a single tag.
        tags = [request.GET[u'tag'].strip()]
        results = search_content_for_tags(tags, request)
    return {'results': results}


@view_config(name='search', permission='view',
             renderer='kotti:templates/view/search.pt')
@view_config(name='folder_view', context=IContent, permission='view',
             renderer='kotti:templates/view/folder.pt')
@view_config(name='view', context=IContent, renderer='test_view.jinja2')
def view(context, request):
    print 'mba views view'
    api = MbaTemplateAPI(context, request)
    return {'api': api, 'context':context}

def includeme(config):
    print 'hear'
    config.scan(__name__)
