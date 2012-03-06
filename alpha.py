#ssh -R *:5672:localhost:8888 ubuntu@ec2-50-19-175-110.compute-1.amazonaws.com

import site, os
site.addsitedir('./thirdparty')

import logging, lib.log
import tornado.ioloop, tornado.web, tornado.template
import tornado.autoreload
from tornado.web import url
from tornado.escape import parse_qs_bytes
from pymongo import Connection
from twilio.util import TwilioCapability, RequestValidator
from twilio import twiml
from lib.restnado import RestHandler
from lib.phone import convert_to_e164, NumberParseException

logger = logging.getLogger(__name__)

TWILIO_AUTH_TOKEN = '62a6300ce1272134fbbd10ae45d218c0'

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    'debug': True,
    #"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    #"login_url": "/login",
    #"xsrf_cookies": True,
}

loader = tornado.template.Loader("./templates")

#DB Init
conn = Connection('ubuntu.local', 27017)
db = conn.vocal_broker

def initialize_system():
    db.callers.ensure_index('number', unique=True)
    db.calls.ensure_index('CallSid', unique=True)
initialize_system()


class Call(object):
    def __init__(self):
        


class TwimlRest(RestHandler):
    def prepare(self):
        #Security
        validator = RequestValidator(TWILIO_AUTH_TOKEN)
        # the POST variables attached to the request (eg "From", "To")
        post_vars = dict([(k, v[0]) for k,v in parse_qs_bytes(self.request.body, True).items()])
        signature = self.request.headers.get('X-Twilio-Signature', '') # X-Twilio-Signature header value

        if not validator.validate(self.request.full_url(), post_vars, signature):
            logger.critical('BAD SIGNATURE')
            response = twiml.Response()
            response.say('Sorry')
            response.hangup()
            self.finish(str(response))
            return

        #Session: Each call is somewhat like a session.
        self.session = None

    def handle_response(self, f, *a, **k):
        self.write(str(f(*a, **k))) #TWIML RESPONSE

    def on_finish(self):
        conn.end_request()


class CallInitialize(TwimlRest):
    #:TODO: get lookup
    def post(self, *a, **kw):
        response = twiml.Response()

        logger.debug('Initialize Call from: %s' % self.get_argument('From', 'Unknown'))

        if self.get_argument('From', None) is None:
            with response.gather(action=self.reverse_url('lookup'), method='GET', timeout=10, numDigits=10) as g:
                g.say('Enter your ten digit US phone number starting with area code.', voice='woman')
            logger.debug('NEW INIT: %s', response)
        else:
            response.redirect(self.reverse_url('lookup'), method='GET')
        return response


class CallLookup(TwimlRest):
    def get(self, *a, **kw):
        response = twiml.Response()

        digits = self.get_argument('Digits', self.get_argument('From', None))

        if digits is None:
            logger.debug('No digits passed to lookup')
            response.hangup()
        else:
            try:
                phone_number = convert_to_e164(digits).strip('+') #The + causes URL trouble.
            except NumberParseException:
                logger.debug('Failed to convert phone number %s' % digits)
                phone_number = digits
                #response.hangup()
            caller = db.callers.find_one({'number': phone_number})

            if caller is None:
                response.redirect(self.reverse_url('new', phone_number))
            else:
                response.redirect(self.reverse_url('verify', caller['number']), method='GET')

        return response


class CallNew(TwimlRest):
    def post(self, phone_number, *a, **kw):
        logger.debug('NEW CALLER %s' % phone_number)

        caller = db.callers.find_one({'number': phone_number})

        response = twiml.Response()

        if caller is not None:
            response.redirect('begin')
        else:
            db.callers.insert(dict(
                number=phone_number
            ))
            response.say('Welcome, I need to get to know you', voice='woman')
            response.redirect(self.reverse_url('attach_name', phone_number), method="GET")
        return response


class CallVerify(TwimlRest):
    def get(self, phone_number, *a, **kw):
        logger.debug('Verify Caller')

        caller = db.callers.find_one({'number': phone_number})

        response = twiml.Response()

        with response.gather(action='/call/verify/', timeout=10, finishOnKey="*") as g:
            g.say('Hello', voice='woman')
            g.play(caller['name_rec'])
            g.say('If this is you, Press 1. Otherwise press 2', voice='woman')

        return response


class CallAttachName(TwimlRest):
    def get(self, phone_number, *a, **kw):
        logger.debug('Check name attachment')

        caller = db.callers.find_one({'number': phone_number})

        digits = self.get_argument('Digits', None)

        response = twiml.Response()

        if 'name_rec' not in caller:
            response.say('Please say your full name after the beep', voice='woman')
            response.record(
                playBeep=True,
                transcribe=True,
                maxLength=10,
                action=self.reverse_url('attach_name', phone_number),
                method="POST",
                transcribeCallback=self.reverse_url('attach_name_text', phone_number))
            response.redirect(self.reverse_url('attach_name', phone_number), method="GET")
        elif digits is not None:
            #This is us confirming a name
            print digits
            response.hangup()
        else:
            with response.gather(
                action=self.reverse_url('attach_name', phone_number),
                method="GET",
                timeout=10,
                finishOnKey="*") as g:

                g.say('The name associated with your is')
                g.play(caller['name_rec'])
                g.say('Press 1 if this is ok, or 2 to change')

            response.redirect(self.reverse_url('attach_name', phone_number), method="POST")
        return response

    def post(self, phone_number, *a, **kw):
        logger.debug('Attach Name Rec')

        caller = db.callers.find_one({'number': phone_number})

        db.callers.update({'number': phone_number}, {'$set':
            dict(
                name='Awaiting Transcription',
                name_rec=self.get_argument('RecordingUrl'),
                name_rec_dur=self.get_argument('RecordingDuration'),
                name_rec_digits=self.get_argument('Digits')
            )}
        )

        response = twiml.Response()
        response.redirect(self.reverse_url('attach_name', phone_number), method='GET')

        return response


class CallAttachNameText(TwimlRest):
    def post(self, phone_number, *a, **kw):
        logger.debug('Attach Name Text')

        if self.get_argument('TranscriptionStatus') == 'completed':
            db.callers.update({'number': phone_number}, {'$set':
                dict(
                    name=self.get_argument('TranscriptionText'),
                    name_trans_url=self.get_argument('TranscriptionUrl'),
                    name_trans_rec=self.get_argument('RecordingUrl')
                )}
            )


class CallAttachBilling(TwimlRest):
    def get(self, phone_number, *a, **kw):
        response = twiml.Response()
        response.say('billing')
        response.hangup()
        return response


class CallStatus(TwimlRest):
    def post(self, *a, **kw):
        logger.debug('CALL STATUS')
        #print self.request.arguments


class ClientCaller(tornado.web.RequestHandler):
    def get(self, *a, **kw):
        # Find these values at twilio.com/user/account
        account_sid = "ACd61a084824884699a1413e71f40a3b5a"
        auth_token = TWILIO_AUTH_TOKEN

        capability = TwilioCapability(account_sid, auth_token)
        capability.allow_client_outgoing('AP1812e773105345a397a849121138359a')
        capability.allow_client_incoming('test')
        token = capability.generate()

        self.render("templates/client.html", token=token)

application = tornado.web.Application([
    url(r"/client/", ClientCaller),
    url(r"/call/begin/", CallInitialize, {}, 'begin'),
    url(r"/call/lookup/", CallLookup, {}, 'lookup'),
    url(r"/call/([\+0-9a-z\:]+)/verify/", CallVerify, {}, 'verify'),
    url(r"/call/([\+0-9a-z\:]+)/new/", CallNew, {}, 'new'),
    url(r"/call/([\+0-9a-z\:]+)/name/", CallAttachName, {}, 'attach_name'),
    url(r"/call/([\+0-9a-z\:]+)/name-text/", CallAttachNameText, {}, 'attach_name_text'),

    url(r"/call/([\+0-9a-z\:]+)/billing/", CallAttachBilling, {}, 'attach_billing'),

    url(r"/call/update/", CallStatus),
    url(r"/(favicon\.ico)", tornado.web.StaticFileHandler, {'path': settings['static_path']}),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
