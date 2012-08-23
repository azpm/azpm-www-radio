import datetime

from django import forms
from django.forms.util import ErrorList

from libazpm.contrib.chronologia.models import Service
from libazpm.contrib.chronologia.forms import DateSelectWidget, ServiceModelChoiceField

class PrintForm(forms.Form):
    service = ServiceModelChoiceField(queryset=Service.objects.filter(active=True, typing="radio"), label="Service")
    start_date = forms.DateField(label="Start", widget=DateSelectWidget)
    end_date = forms.DateField(label="End", widget=DateSelectWidget)

    def clean(self):
        cleaned_data = self.cleaned_data

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if type(start_date) is type(end_date) is datetime.date:
            if not start_date <= end_date:
                self._errors['start_date'] = ErrorList(['Please enter a valid start'])
                self._errors['end_date'] = ErrorList(['Please enter a valid end'])

                del cleaned_data['start_date']
                del cleaned_data['end_date']
        elif type(end_date) is datetime.date is not type(start_date):
            self._errors['start_date'] = ErrorList(['Start is required for and End'])


        return cleaned_data



