import time

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.db import transaction, router
from django.db.utils import IntegrityError
from django.utils.cache import patch_vary_headers
from django.utils.encoding import force_unicode
from django.utils.http import cookie_date
from django.utils.importlib import import_module
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.backends.base import CreateError, SessionBase

from broker.models import Call

KEY_PREFIX = "call_session_cache"


class SessionMiddleware(object):
    """
    This is a copy of the Django session middleware except it is based on a
    calls SID instead of a cookie.
    """
    def process_request(self, request):
        try:
            request.session = CachedCallSessionStore(request.REQUEST.get('CallSid', None))
        except ValueError:
            request.session = None

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        try:
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                request.session.save()
        return response



class CallSessionStore(SessionBase):
    """
    Implements database session store.
    """
    def __init__(self, session_key=None):
        if session_key is None:
            raise ValueError('Cannot create a new session for Calls')
        super(CallSessionStore, self).__init__(session_key)

    def load(self):
        try:
            s = Call.objects.get(call_sid=self.session_key)
            return self.decode(force_unicode(s.session_data))
        except (Call.DoesNotExist, SuspiciousOperation):
            raise ValueError('No Session')

    def exists(self, session_key):
        try:
            Call.objects.get(session_key=session_key)
        except Call.DoesNotExist:
            return False
        return True

    def save(self):
        obj = Call(
            call_sid = self.session_key,
            session_data = self.encode(self._get_session())
        )
        using = router.db_for_write(Call, instance=obj)
        try:
            obj.save(using=using)
        except IntegrityError:
            raise

    def delete(self, session_key=None):
        raise NotImplementedError('CallSession does not support deletion')

    def flush(self):
        raise NotImplementedError('CallSession does not support deletion')


class CachedCallSessionStore(CallSessionStore):
    """
    Copy of django cache_db session backend with one notable exception. This
    backend does not support the created and generation of session ids. Session
    ids are based on callsids.
    """

    def __init__(self, session_key=None):
        super(CachedCallSessionStore, self).__init__(session_key)

    def load(self):
        data = cache.get(KEY_PREFIX + self.session_key, None)
        if data is None:
            data = super(CachedCallSessionStore, self).load()
            cache.set(KEY_PREFIX + self.session_key, data,
                settings.SESSION_COOKIE_AGE)
        return data

    def save(self):
        super(CachedCallSessionStore, self).save()
        cache.set(KEY_PREFIX + self.session_key, self._session,
            settings.SESSION_COOKIE_AGE)
