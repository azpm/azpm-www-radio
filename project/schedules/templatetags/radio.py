from django.template import   Library
from project.schedules.forms import PrintForm

register = Library()

def print_form_js():
    t = PrintForm()
    return u"%s" % (t.media['js'])

def print_form_css():
    t = PrintForm()
    return u"%s" % (t.media['css'])

def print_form(context):
    service = context.get('service', None)

    if service:
        form = PrintForm(prefix="printcc", initial={'service': service})
    else:
        form = PrintForm(prefix="printcc")

    return {"form": form}

register.simple_tag(print_form_js)
register.simple_tag(print_form_css)

register.inclusion_tag("schedules/forms/print.html", takes_context=True)(print_form)