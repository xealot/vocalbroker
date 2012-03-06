from django.http import HttpResponse
from django.utils.decorators import available_attrs
from django.utils.functional import wraps
from twilio import twiml

def twiml_response(func):
    def inner(request, *args, **kwargs):
        return HttpResponse(str(func(request, twiml.Response(), *args, **kwargs)))
    return wraps(func, assigned=available_attrs(func))(inner)