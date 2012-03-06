from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('broker.views',
    url(r'^test/', 'test_client', {'TWILIO-SIG': False}),
    url(r'^update/', 'update'),
    url(r'^begin/', 'begin'),
    url(r'^init/(?P<number>[^/]+)/', 'init'),
    url(r'^(?P<number>[^/]+)/account/', 'account'),
)
