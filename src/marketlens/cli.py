import logging

from marketlens.config import LogLevel, get_settings


def configure_logger(level: LogLevel) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    configure_logger(settings.log_level)
    print(settings.model_dump_json(indent=2))
    logger.info("config loaded")
