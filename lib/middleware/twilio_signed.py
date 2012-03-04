from logging import getLogger
from django.conf import settings
from django.http import HttpResponse
from twilio.util import RequestValidator
from twilio import twiml

log = getLogger()

SIG_HEADER = 'HTTP_X_TWILIO_SIGNATURE'
SIG_FLAG = 'TWILIO-SIG'

response = twiml.Response()
response.say('Sorry, Bad Signature')
response.hangup()

class TwilioSignedRequest(object):
    def process_request(self, request):
        if SIG_HEADER in request.META and not check_signature(request):
            log.critical('BAD SIGNATURE')
            return HttpResponse(str(response))

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_kwargs.pop(SIG_FLAG, False) and not SIG_HEADER in request.META:
            log.critical('NO SIGNATURE, BUT REQUIRED')
            return HttpResponse(str(response))


def check_signature(request):
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    if validator.validate(request.build_absolute_uri(), request.POST, request.META[SIG_HEADER]):
        return True
    return False