
def includeme(config):
    config.include('mba.views.index')
    config.include('mba.views.home')


    config.include('mba.views.meetups')
    config.include('mba.views.meetup')

    config.include('mba.views.login')
    #config.include('mba.views.logout')

    config.include('mba.views.register')
    config.include('mba.views.col_test')
    config.include('mba.views.resume')
    config.include('mba.views.job')
    config.include('mba.views.resume_edit')
    config.include('mba.views.resume_preview')
    config.include('mba.views.activity')

