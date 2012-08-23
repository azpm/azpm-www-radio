import logging

from libazpm.contrib.chronologia.models import Service
from django.shortcuts import get_object_or_404, get_list_or_404

logger = logging.getLogger('project.schedules.views.mixins')

class RadioServiceMixin(object):
    service = None
    services = None

    def get(self, request, *args, **kwargs):
        if 'service' in kwargs:
            keyname = kwargs.pop('service')
            self.service = get_object_or_404(Service, typing="radio", active=True, keyname=keyname)

        self.services = get_list_or_404(Service, typing="radio", active=True)

        return super(RadioServiceMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(RadioServiceMixin, self).get_context_data(*args, **kwargs)

        c = {
            'service': self.service,
            'services': self.services
        }

        context.update(c)

        return context