# -*- coding: utf-8 -*-
"""Loggers."""

import sys
from pathlib import Path
from typing import Any, TypedDict

from loguru import logger

LOG_FOLDER: Path = Path(__file__).parent.parent / 'logs'

if not LOG_FOLDER.exists():
    LOG_FOLDER = Path(__file__).parent / 'logs'

# paths to log files
clean_logs: list[Path] = [
    Path(LOG_FOLDER) / 'main.log',
    Path(LOG_FOLDER) / 'load.log',
]

# clean logs files
for log_file in clean_logs:
    with open(log_file, 'w', encoding='utf-8') as f:
        pass

DEFAULT_LOGGING_LEVEL: str = 'DEBUG' if 'pytest' in sys.modules else 'INFO'


# type annotation for each logger
class LoggerConfig(TypedDict):
    """Type annonation for loggers.

    Attributes:
    -----------
        logger: logger
        level: level for logger
        output: where to put logs
    """

    logger: Any
    level: str
    output: str


LoggersConfig = dict[str, LoggerConfig]

loggers: LoggersConfig = {
    'main': {
        'logger': logger.bind(type='main'),
        'level': DEFAULT_LOGGING_LEVEL,
        'output': 'file',
    },
}

# remove standard logger
logger.remove()

for name, config in loggers.items():
    # create loggers that put info into console
    if 'console' in config['output']:
        config['logger'].add(
            sink=sys.stderr,
            format='{time:mm:ss.SSS} | {level} | {message} | {function}',
            level=config['level'],
            colorize=True,
            filter=lambda record, n=name: record['extra'].get('type') == n,
        )
    # create loggers that put info into file
    if 'file' in config['output']:
        config['logger'].add(
            Path(LOG_FOLDER) / f'{name}.log',
            format='{time:mm:ss.SSS} | {level} | {message} | {function}',
            level=config['level'],
            colorize=True,
            filter=lambda record, n=name: record['extra'].get('type') == n,
        )

# create each logger
main_log = loggers['main']['logger']
