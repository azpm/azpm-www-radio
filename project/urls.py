from django.conf.urls import *
from django.contrib import admin
from libscampi.contrib import cms

admin.autodiscover()

urlpatterns = patterns('',
    (r'^schedules/', include('project.schedules.urls', namespace='radio', app_name='schedules'), {'keyname': 'schedules'}),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'', include(cms.site.urls)),
)
