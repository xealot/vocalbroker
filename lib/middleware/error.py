import socket
import traceback
from logging import getLogger
#from hashlib import md5

log = getLogger('exception')

class ErrorLogMiddleware(object):
    def process_exception(self, request, exception):
        server_name = socket.gethostname()
        tb_text     = traceback.format_exc()
        class_name  = exception.__class__.__name__
        #checksum    = md5.new(tb_text).hexdigest()

        defaults = dict(
            class_name  = class_name,
            url         = request.build_absolute_uri(),
            server_name = server_name,
            traceback   = tb_text,
        )

        log.error(exception.message, extra=defaults)