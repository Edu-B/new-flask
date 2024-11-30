# Native imports
import json
import socket
import logging
from typing import Union
from logging.handlers import SysLogHandler

# Project imports
from app.config import Env


def setup_logger(
    logger: logging.Logger,
    env: str,
    app_name: str,
    pt_host: str,
    pt_port: int,
):
    """
    Setup a custom logger with JSON formatting and handler
    based on application environment.
    """

    class ContextFilter(logging.Filter):
        hostname = socket.gethostname()

        def filter(self, record):
            record.hostname = ContextFilter.hostname
            return True

    class PapertrailFormatter(logging.Formatter):
        def __init__(
            self,
            fmt: Union[str, None] = ...,
            datefmt: Union[str, None] = ...,
        ) -> None:
            super().__init__(datefmt=datefmt)

        def format(self, record):
            is_text = isinstance(record.msg, (str))
            record.message = record.getMessage() if is_text else record.msg
            record.asctime = self.formatTime(record, self.datefmt)
            record.stack_info = self.formatStack(record.stack_info)
            if record.exc_info:
                if not record.exc_text:
                    record.exc_text = self.formatException(record.exc_info)

            # Prepare json logging
            data = {"msg": record.message, "level": record.levelname}
            if record.exc_text:
                data["exception"] = record.exc_text

            return f"{record.asctime} {app_name} {app_name}.{env} {json.dumps(data)}"  # noqa

    logger.setLevel(logging.DEBUG)

    context_filter = ContextFilter()
    pt_formatter = PapertrailFormatter(datefmt="%b %d %H:%M:%S")

    stream_handler = logging.StreamHandler()
    stream_handler.addFilter(context_filter)
    stream_handler.setFormatter(pt_formatter)

    pt_handler = SysLogHandler(address=(pt_host, pt_port))
    pt_handler.addFilter(context_filter)
    pt_handler.setFormatter(pt_formatter)

    if env == Env.Dev:
        logger.addHandler(stream_handler)
        logger.setLevel(logging.DEBUG)
    elif env == Env.Stg:
        logger.addHandler(stream_handler)
        logger.addHandler(pt_handler)
        logger.setLevel(logging.DEBUG)
    elif env == Env.Prd:
        logger.addHandler(pt_handler)
        logger.setLevel(logging.INFO)
