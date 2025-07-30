import logging
import os
import sys


_COLORS = {
    'GRAY': '90',
    'RED': '31',
    'GREEN': '32',
    'YELLOW': '93',
    'BLUE': '34',
    'PURPLE': '35',
    'CYAN': '96',
}

log = logging.getLogger()
supports_color = os.getenv('TERM') and sys.stderr.isatty()


def color(s: str, color: str) -> str:
    if not supports_color:
        return s
    color = _COLORS.get(color.upper(), color)
    return f'\033[0;{color}m{s}\033[0m'


def init_logging(loglevel: int):
    handler = logging.StreamHandler()
    handler.setLevel(loglevel)
    if supports_color:
        formatter = logging.Formatter(color('%(message)s', 'gray'))
        handler.setFormatter(formatter)
    log.setLevel(logging.NOTSET)
    log.addHandler(handler)
