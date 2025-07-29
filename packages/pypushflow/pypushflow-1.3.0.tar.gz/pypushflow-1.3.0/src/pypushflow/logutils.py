import os
import sys
import warnings
import logging
import logging.handlers
from pathlib import Path

DEFAULT_FORMAT = "%(levelname)-8s %(asctime)s [%(threadName)s] %(message)s"
DEFAULT_LOGDIR = os.path.join(os.path.sep, "tmp_14_days")


class PyPushflowLoggedObject:
    """This object owns a logger which adds workflow related context to the logs"""

    def __init__(self, log_metadata=None, parent=None):
        if log_metadata:
            if "class" not in log_metadata:
                log_metadata["class"] = type(self).__name__
        else:
            log_metadata = {"class": type(self).__name__}
        if parent:
            logger = parent.logger
        else:
            logger = logging.getLogger("pypushflow")
        self.logger = _PypushflowLoggerAdapter(logger, log_metadata)


def basicConfig(filename=None, logdir=None, user=None, initiator=None, **kwargs):
    """Basic configuration for the root logger. By default:
        * set log level to INFO
        * add STDOUT stream handler

    Has no effect when there are already handlers unless `force=True`.
    Note: pytest installs handlers.
    """
    warnings.warn(
        "logging configuration in pypushflow is deprecated", DeprecationWarning
    )
    kwargs.setdefault("format", DEFAULT_FORMAT)
    kwargs.setdefault("level", logging.INFO)
    kwargs.setdefault("stream", sys.stdout)

    user = user or "unknown"
    initiator = initiator or "unknown"
    force = kwargs.setdefault("force", False)

    logging.basicConfig(**kwargs)
    logger = logging.getLogger()
    for handler in logger.handlers:
        if isinstance(handler, _PyPushflowLogFile):
            logger.removeHandler(handler)
    if (len(logger.handlers) == 0 or force) and filename:
        if logdir is None:
            logdir = DEFAULT_LOGDIR
        filename = os.path.join(logdir, filename)
        handler = _PyPushflowLogFile.factory(filename, user, initiator)
        logger.addHandler(handler)


class _PypushflowLoggerAdapter(logging.LoggerAdapter):
    """Log adapter which adds workflow related context (if any) to the log messages"""

    def process(self, msg, kwargs):
        kwargs["extra"] = self.extra

        if self.extra:
            if "workflow" in self.extra:
                ctx = "[%s]" % (self.extra["workflow"],)
            elif "actor" in self.extra:
                ctx = "[<%s> %s]" % (
                    self.extra["class"],
                    self.extra["actor"],
                )
            else:
                ctx = None
            if ctx:
                msg = "%s %s" % (ctx, msg)
        return msg, kwargs


class _PyPushflowLogFile(logging.handlers.RotatingFileHandler):
    MAXBYTES = 10 << 20
    BACKUPCOUNT = 10
    SUFFIX = ".log"

    @classmethod
    def factory(cls, filename: str, user: str, initiator: str):
        log_file_path = cls.__getLogFile(filename)
        if log_file_path is None:
            return None
        handler = cls(log_file_path, maxBytes=cls.MAXBYTES, backupCount=cls.BACKUPCOUNT)
        formatter = logging.Formatter(DEFAULT_FORMAT)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        return handler

    @classmethod
    def __getLogFile(cls, filename: str, user: str, initiator: str):
        if not filename:
            return None

        filename = Path(filename).with_suffix(cls.SUFFIX)
        directory = filename.parent / user / initiator
        try:
            directory.mkdir(mode=0o755, parents=True, exist_ok=True)
        except Exception:
            return None
        return directory / filename.name
