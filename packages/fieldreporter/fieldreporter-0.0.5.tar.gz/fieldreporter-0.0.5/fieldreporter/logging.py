# Logger subclass that reports messages via a FieldReporter object
from .reporter import FieldReporter
import logging

class FieldReporterLogHandler(logging.Handler):
    """
    A logging handler that sends log messages to a FieldReporter instance.
    """
    def __init__(self, name, reporter: FieldReporter):
        super().__init__()
        self.name = name
        self.reporter = reporter

    def emit(self, record):
        try:
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                self.reporter.error(msg)
            elif record.levelno >= logging.WARNING:
                self.reporter.warning(msg)
        except Exception:
            self.handleError(record)