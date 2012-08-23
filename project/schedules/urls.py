from django.conf.urls import *

urlpatterns = patterns('project.schedules.views',
    #url(r"^search/$", 'search', name="search"),
    url(r'^print/$', 'print_schedules', name="print"),
    url(r'^(?P<service>[\w\.\-]+)/nowplaying/$', 'now_playing', name="now-playing"),
    url(r'^(?P<service>[\w\.\-]+)/w/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d+)/$', 'service_week', name="service-week"),
    url(r'^(?P<service>[\w\.\-]+)/d/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d+)/$', 'service', name="service-date"),
    url(r"^(?P<service>[\w\.\-]+)/$", 'service', name="service"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d+)/$', 'index', name="index-date"),
    url(r'^$', 'index', name="index"),
)