import logging
import sys

from app.core.config import settings


RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"

LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",
    logging.INFO: "\033[32m",
    logging.WARNING: "\033[33m",
    logging.ERROR: "\033[31m",
    logging.CRITICAL: "\033[35m",
}

LOGGER_COLORS = {
    "api": "\033[94m",
    "worker": "\033[96m",
}


class ColorFormatter(logging.Formatter):
    def __init__(self, service_name: str, use_color: bool) -> None:
        super().__init__()
        self.service_name = service_name
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, datefmt="%H:%M:%S")
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()

        if self.use_color:
            level = f'{LEVEL_COLORS.get(record.levelno, "")}{BOLD}{level:<8}{RESET}'
            logger_color = LOGGER_COLORS.get(self.service_name, "\033[90m")
            service_name = f"{logger_color}{self.service_name.upper()}{RESET}"
            logger_name = f"{DIM}{logger_name}{RESET}"
            timestamp = f"{DIM}{timestamp}{RESET}"
        else:
            level = f"{level:<8}"
            service_name = self.service_name.upper()

        formatted = f"{timestamp} {level} [{service_name}] {logger_name} {message}"

        if record.exc_info:
            formatted = f"{formatted}\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging(service_name: str) -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    handler = logging.StreamHandler()
    use_color = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
    handler.setFormatter(ColorFormatter(service_name=service_name, use_color=use_color))
    root_logger.addHandler(handler)

    logging.getLogger("uvicorn").handlers.clear()
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.error").handlers.clear()
