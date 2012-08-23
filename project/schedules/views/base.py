import logging
import calendar

from datetime import datetime, date, timedelta

from django.db.models import Q, Max
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import FormView, View

from libazpm.contrib.calendar.legacy.helpers import generate_calendars
from libazpm.contrib.chronologia.models import Service as RadioService, RadioAir, Song, Special, Episode

from libscampi.contrib.cms.views.base import Page
from libscampi.contrib.cms.communism.models import *

from .mixins import RadioServiceMixin
from project.schedules.forms import PrintForm

logger = logging.getLogger('project.schedules')

__all__ = ['Index','Service','ServiceWeek','Print','Search','NowPlaying']

class RadioSchedulesPage(Page):
    base_title = u"Radio Schedules"
    cached_css_key = "radio:schedules:css"
    cached_js_key = "radio:schedules:js"

    #the static files intensifier css for schedules, not included in app because it comes from TV schedules
    schedules_css = {
        'url': "%sintensifier/css/schedules.css" % settings.STATIC_URL,
        'media': "screen",
        'for_ie': False
    }

    def get_static_styles(self):
        return [self.schedules_css]

    def get_theme(self):
        try:
            theme = Theme.objects.get(keyname="intensifier")
        except Theme.DoesNotExist:
            theme = Theme.objects.none()

        return theme

    def get_page_title(self):
        return self.base_title

    def get_context_data(self, *args, **kwargs):
        context = super(RadioSchedulesPage, self).get_context_data(*args, **kwargs)

        c = {
            'rightnow': datetime.now()
        }

        context.update(c)

        return context

class Index(RadioServiceMixin, RadioSchedulesPage):
    template_name = "schedules/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(Index, self).get_context_data(*args, **kwargs)

        try:
            year, month, day = self.kwargs['year'], self.kwargs['month'], self.kwargs['day']
        except (ValueError, KeyError):
            day = date.today()
        else:
            try:
                day = date(int(year), int(month), int(day))
            except (ValueError, TypeError):
                raise Http404

        today = date.today()
        future_date = day + timedelta(days=14) #get a date 14 days out

        airs = RadioAir.objects.filter(service__in=self.services, date=day).select_related('service').prefetch_related('airing').order_by('service','date','time')
        if not airs.exists():
            raise Http404("Nothing Airing on %s" % day.strftime("%m/%d/%Y"))


        calendars = generate_calendars(today, future_date)

        c = {
            'airing': airs,
            'today': today,
            'idealised_day': day,
            'calendars': calendars,
            'max_days': future_date
        }

        context.update(c)
        return context

class Service(RadioServiceMixin, RadioSchedulesPage):
    def get_context_data(self, *args, **kwargs):
        context = super(Service, self).get_context_data(*args, **kwargs)

        try:
            year, month, day = self.kwargs['year'], self.kwargs['month'], self.kwargs['day']
        except (ValueError, KeyError):
            day = date.today()
        else:
            try:
                day = date(int(year), int(month), int(day))
            except (ValueError, TypeError):
                raise Http404

        today = date.today()

        airs = RadioAir.objects.filter(service=self.service, date=day).prefetch_related('airing').order_by('date','time')
        if not airs.exists():
            raise Http404("Nothing Airing on %s" % day.strftime("%m/%d/%Y"))

        last_time = RadioAir.objects.filter(service = self.service).aggregate(latest = Max('date'))
        if last_time['latest'] == None:
            latest = today + datetime.timedelta(14)
        else:
            latest = last_time['latest']

        calendars = generate_calendars(today, latest)

        c = {
            'airing': airs,
            'today': today,
            'idealised_day': day,
            'calendars': calendars,
            'max_days': latest
        }

        context.update(c)
        return context

    def get_page_title(self):
        return u"%s Schedule | %s" % (self.service.name, self.base_title)

    def get_template_names(self):
        return "schedules/service/%s.html" % self.service.keyname

class ServiceWeek(RadioServiceMixin, RadioSchedulesPage):
    basedate = None

    def get(self, request, *args, **kwargs):
        try:
            year, month, day = self.kwargs['year'], self.kwargs['month'], self.kwargs['day']
        except (ValueError, KeyError):
            raise Http404
        else:
            try:
                self.basedate =  date(int(year), int(month), int(day))
            except (TypeError, ValueError):
                raise Http404

        return super(ServiceWeek, self).get(request, *args, **kwargs)


    def get_page_title(self):
        return u"Weekly Schedule for %s | %s" % (self.service.name, self.base_title)

    def get_context_data(self, *args, **kwargs):
        context = super(ServiceWeek, self).get_context_data(*args, **kwargs)

        c = calendar.Calendar(6)
        cal = c.monthdatescalendar(self.basedate.year, self.basedate.month)
        # this bit of fucking sexy code gives me the week I want
        week = [i for i in cal if self.basedate in i][0]
        actual_base = week[0] # actual first day of week -- probably self.basedate, but good to be sure

        airs = RadioAir.objects.select_related('service').prefetch_related('airing').filter(service=self.service, date__range=[week[0],week[len(week)-1]]).order_by('start')
        last_time = RadioAir.objects.filter(service = self.service).aggregate(latest = Max('date'))
        if last_time['latest'] == None:
            latest = today + datetime.timedelta(14)
        else:
            latest = last_time['latest']

        calendars = generate_calendars(date.today(), latest)

        c = {
            'airing': airs,
            'today': date.today(),
            'idealised_day': actual_base,
            'calendars': calendars,
            'max_days': latest,
            'week': week,
        }

        context.update(c)

        return context

    def get_template_names(self):
        return "schedules/service/week/%s.html" % self.service.keyname


class Print(RadioSchedulesPage, FormView):
    form_class = PrintForm
    template_name = "schedules/service/print/index.html"

    def get(self, request, *args, **kwargs):
        return super(Print, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(Print, self).post(request, *args, **kwargs)

    def get_page_title(self):
        return u"Print | %s" % self.base_title

    def get_form_kwargs(self):
        kwargs = super(Print, self).get_form_kwargs()
        kwargs.update({"prefix": "printcc"})

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Print, self).get_context_data(**kwargs)

        form = kwargs.get('form', None)
        results = kwargs.get('results', None)

        c = {
            'form': form,
            'results': results,
            'rightnow': datetime.now()
        }

        context.update(c)
        return context

    def form_valid(self, form):
        start_date = form.cleaned_data['start_date'] or date.today()
        end_date = form.cleaned_data['end_date'] or start_date + timedelta(days=1)
        service = form.cleaned_data['service']

        date_range = [start_date,end_date]
        airs = RadioAir.objects.filter(service = service, date__range = date_range).select_related('service__keyname').prefetch_related('airing')

        results = {
            'service': service,
            'start_date': start_date,
            'end_date': end_date,
            'airing': airs.order_by('start'),
            }

        c = {
            'form': form,
            'results': results
        }

        return self.render_to_response(self.get_context_data(**c))

    def form_invalid(self, form):
        c = {
            'form': form,
            'results': None,
            }

        return self.render_to_response(self.get_context_data(**c))

class Search(RadioSchedulesPage):
    pass

class NowPlaying(View):
    def get(self, request, *args, **kwargs):
        if 'service' in kwargs:
            keyname = kwargs.pop('service')
            service = get_object_or_404(RadioService, typing="radio", active=True, keyname=keyname)


            response = HttpResponse(mimetype="text/html")

            now = datetime.now()
            today = date.today()

            #start the query
            qs = RadioAir.objects.filter(Q(start__lte=now) & Q(end__gte=now), service=service, date=today).order_by('start')

            try:
                air = qs[0]
            except IndexError:
                if service.keyname == "kuatfm":
                    response.write("Classical24 Programming")
                else:
                    response.write("Unknown")
                return response

            if type(air.airing) is Song:
                if air.airing.composer:
                    response.write(u"%s - %s" % (air.airing.composer, air.airing.name))
                else:
                    response.write(u"%s" % air.airing.name)
            elif type(air.airing) is Special:
                response.write(u"%s" % air.airing.name)
            elif type(air.airing) is Episode:
                response.write(u"%s" % air.airing.series.name)

            return response

        else:
            return Http404("Nothing on")
