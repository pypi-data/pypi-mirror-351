import logging
import re
import six
from collections import OrderedDict
from typing import Dict, List

# Log handler is configured if provided in ENV. Configured end of file (EOF)

DEBUG = "debug"
INFO = "info"
ERROR = "error"


def logfmt(props):
    def fmt(key, val):
        # Handle case where val is a bytes or bytesarray
        if six.PY3 and hasattr(val, "decode"):
            val = val.decode("utf-8")
        # Check if val is already a string to avoid re-encoding into
        # ascii. Since the code is sent through 2to3, we can't just
        # use unicode(val, encoding='utf8') since it will be
        # translated incorrectly.
        if not isinstance(val, six.string_types):
            val = six.text_type(val)
        if re.search(r"\s", val):
            val = repr(val)
        # key should already be a string
        if re.search(r"\s", key):
            key = repr(key)
        return "{key}={val}".format(key=key, val=val)

    return " ".join([fmt(key, val) for key, val in props.items()])


def _format_msg(message, **params):
    props = OrderedDict(message=message)
    props.update(params)
    return logfmt(props)


def scrub_sensitive(data: Dict, secrets: List[str]):
    return {k: v if k not in secrets else "****" for k, v in data.items()}


def silence_urllib3(warnings_only=False):
    import urllib3

    urllib3.disable_warnings()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if warnings_only:
        return

    logging.getLogger("urllib3").propagate = False


class _Logger(object):
    DEFAULT_LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] [%(message)s]"

    def __init__(self):
        self._logger = logging.getLogger("cohesivenet")
        self.format = self.DEFAULT_LOG_FORMAT

    def debug(self, message, **params):
        self._logger.debug(_format_msg(message, **params))

    def info(self, message, **params):
        self._logger.info(_format_msg(message, **params))

    def error(self, message, **params):
        self._logger.error(_format_msg(message, **params))

    def set_null(self):
        self._logger.addHandler(logging.NullHandler())

    def set_level(self, log_level):
        return self.set_stream_handler(log_level)

    def set_stream_handler(self, log_level):
        if not log_level:
            return

        valid_level = None
        log_level = str(log_level).lower()
        if log_level == "debug":
            valid_level = logging.DEBUG
        elif log_level == "info":
            valid_level = logging.INFO
        elif log_level == "error":
            valid_level = logging.ERROR

        if valid_level:
            self._logger.handlers = []
            console = logging.StreamHandler()
            console.setFormatter(logging.Formatter(self.format))
            console.setLevel(valid_level)
            self._logger.addHandler(console)
            self._logger.setLevel(valid_level)
            return True
        else:
            print(
                "!!! LOG SETUP ERROR - Level must be one of debug,info or error. No logging configured."
            )
            return False

    def silence_urllib3(self, warnings_only=False):
        silence_urllib3(warnings_only=warnings_only)


Logger = _Logger()
