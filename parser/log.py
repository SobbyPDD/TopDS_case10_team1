import logging
import sys
from typing import Optional


def configure_logging(
        debug: bool = False,
        log_file: Optional[str] = None
) -> None:
    # Очищаем предыдущие обработчики
    for handler in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(handler)

    fmt_str = '%(asctime)s %(levelname)s %(name)s - %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    # Основной обработчик для stdout
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        fmt=fmt_str,
        datefmt=datefmt,
    )
    handler.setFormatter(formatter)

    logging.getLogger().addHandler(handler)

    # Устанавливаем уровень логирования
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)

    logging.info(f'Logging configured successfully')
    if debug:
        logging.debug('Debug logging is enabled')