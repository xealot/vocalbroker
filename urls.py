from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    #url(r'^$', 'vocalbroker.views.home', name='home'),
    url(r'^call/', include('broker.urls'), {'TWILIO-SIG': True}),
)
