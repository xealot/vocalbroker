from logging import getLogger
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from phonenumbers import NumberParseException
from lib.decorators import twiml_response
from lib.phone import convert_to_e164
from twilio.util import TwilioCapability
#from django.http import HttpResponse
#from twilio import twiml

from models import Call, Caller

log = getLogger()

twilio_call_mapping = dict(
    call_sid='CallSid',
    account_sid='AccountSid',
    call_from='From',
    call_to='To',
    status='CallStatus',
    direction='Direction',
    forwarded='ForwardedFrom',
    caller_name='CallerName',
    from_city='FromCity',
    from_state='FromState',
    from_zip='FromZip',
    from_country='FromCountry',
    to_city='ToCity',
    to_state='ToState',
    to_zip='ToZip',
    to_country='ToCountry',
    duration='CallDuration'
)

def test_client(request):
    capability = TwilioCapability(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    capability.allow_client_outgoing(settings.TWILIO_APP_SID)
    capability.allow_client_incoming('test')
    token = capability.generate()

    return render(request, 'client.html', {
        'token': token
    })


@require_http_methods(['GET', 'POST'])
@twiml_response
def begin(request, response):
    """
    Begin makes sure we have a caller with SOME identification. If we can't detect the number we just
    ask them for one.
    """
    r = request.REQUEST
    call_from = r.get('From', None)
    if request.method == 'POST':
        call_from = r.get('Digits', None) #Digits from <Gather>

    log.debug('Initialize Call from: %s' % (call_from or 'Unknown'))

    if call_from is None:
        with response.gather(method='POST', timeout=10, numDigits=10) as g:
            g.say('Enter your ten digit US phone number starting with area code.', voice='woman')
    else:
        try:
            #This block will move into begin() when a valid phone is required
            call_from = convert_to_e164(call_from).strip('+') #The + causes URL trouble.
        except NumberParseException:
            log.warning('Failed to convert phone number %s' % call_from)
            #response.hangup() #Right now I'm not requiring an ACTUAL phone number.

        response.redirect(reverse(init, args=[call_from]), method='POST')
    return response

@require_POST
def update(request):
    r = request.REQUEST
    Call.objects.filter(call_sid=r.get('CallSid'))\
        .update(**dict([(k, r.get(v)) for k,v in twilio_call_mapping.items() if v in r]))
    return HttpResponse('')

@require_POST
@twiml_response
def init(request, response, number):
    """
    Load the caller from the db or create one if necessary
    """
    r = request.REQUEST

    #Create caller if one doesn't exist.
    caller, created = Caller.objects.get_or_create(number=number)

    #Log call SID in database
    call = Call.objects.create(caller=caller, **dict([(k, r.get(v)) for k, v in twilio_call_mapping.items() if v in r]))

    log.info('Created call entry for call: %s', call.call_sid)

    response.redirect(reverse(account, args=[number]), method='GET')

@require_http_methods(['GET', 'POST'])
def account(request, response):
    return response.say('GOODBYE')



@require_GET
@twiml_response
def lookup(request, response):
    """
    Lookup will find the digits from either the FROM or DIGITS variables and check the
    new caller to see if they exist in our database and if not direct them to the correct location.
    """
    # in begin()

    if digits is None:
        log.debug('No digits passed to lookup')
        response.hangup()
    else:
        try:
            #This block will move into begin() when a valid phone is required
            phone_number = convert_to_e164(digits).strip('+') #The + causes URL trouble.
        except NumberParseException:
            log.critical('Failed to convert phone number %s' % digits)
            phone_number = digits
            #response.hangup() #Right now I'm not requiring an ACTUAL phone number.

        try:
            caller = Caller.objects.get(number=phone_number)
            response.redirect(self.reverse_url('verify', caller.number), method='GET')
        except Caller.DoesNotExist:
            response.redirect(reverse(account, phone_number), method='GET')

    return response

