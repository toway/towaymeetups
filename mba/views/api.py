__author__ = 'sunset'

from pyramid.view import view_config

from kotti import  DBSession

from mba.resources import Interest
from mba.utils import RetDict

@view_config(route_name='ajax_interests', renderer='json', xhr=True)
def ajax_interests(request):

    all = DBSession.query(Interest).all()
    retval = [i.name for i in all ]

    return RetDict(retval=retval)




def includeme(config):
    config.add_route('ajax_interests','/api/interests.json')
    config.scan(__name__)