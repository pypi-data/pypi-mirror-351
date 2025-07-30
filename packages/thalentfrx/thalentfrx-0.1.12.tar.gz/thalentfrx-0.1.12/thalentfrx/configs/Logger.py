import os
from datetime import datetime, timedelta, timezone
import logging
from enum import Enum
import logging.config
import logging.handlers
import re
import sys
from typing import AbstractSet, Dict, Mapping, Optional

from thalentfrx.configs import Environment


class LogLevel(Enum):
    DEBUG = logging.DEBUG  # 10
    INFO = logging.INFO  # 20
    WARNING = logging.WARNING  # 30
    ERROR = logging.ERROR  # 40
    CRITICAL = logging.CRITICAL  # 50
    
class DatetimeFormatter(logging.Formatter):
    """A logging formatter which formats record with
    :func:`datetime.datetime.strftime` formatter instead of
    :func:`time.strftime` in case of microseconds in format string.
    """

    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        if datefmt and "%f" in datefmt:
            ct = self.converter(record.created)
            tz = timezone(timedelta(seconds=ct.tm_gmtoff), ct.tm_zone)
            # Construct `datetime.datetime` object from `struct_time`
            # and msecs information from `record`
            # Using int() instead of round() to avoid it exceeding 1_000_000 and causing a ValueError (#11861).
            dt = datetime(*ct[0:6], microsecond=int(record.msecs * 1000), tzinfo=tz)
            return dt.strftime(datefmt)
        # Use `logging.Formatter` for non-microsecond formats
        return super().formatTime(record, datefmt)
    
class ColoredLevelFormatter(DatetimeFormatter):
    """A logging formatter which colorizes the %(levelname)..s part of the
    log format passed to __init__."""
    
    _esctable = dict(
        black=30,
        red=31,
        green=32,
        yellow=33,
        blue=34,
        purple=35,
        cyan=36,
        white=37,
        Black=40,
        Red=41,
        Green=42,
        Yellow=43,
        Blue=44,
        Purple=45,
        Cyan=46,
        White=47,
        bold=1,
        light=2,
        blink=5,
        invert=7,
    )

    LOGLEVEL_COLOROPTS: Mapping[int, AbstractSet[str]] = {
        logging.CRITICAL: {"red"},
        logging.ERROR: {"red", "bold"},
        logging.WARNING: {"yellow"},
        logging.WARN: {"yellow"},
        logging.INFO: {"green"},
        logging.DEBUG: {"purple"},
        logging.NOTSET: set(),
    }
    LEVELNAME_FMT_REGEX = re.compile(r"%\(levelname\)([+-.]?\d*(?:\.\d+)?s)")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)        
        self._original_fmt = self._style._fmt
        self._level_to_fmt_mapping: Dict[int, str] = {}

        for level, color_opts in self.LOGLEVEL_COLOROPTS.items():
            self.add_color_level(level, *color_opts)

    def markup(self, text: str, **markup: bool) -> str:
        for name in markup:
            if name not in self._esctable:
                raise ValueError(f"unknown markup: {name!r}")
        # if self.hasmarkup:
        esc = [self._esctable[name] for name, on in markup.items() if on]
        if esc:
            text = "".join("\x1b[%sm" % cod for cod in esc) + text + "\x1b[0m"
        return text

    def add_color_level(self, level: int, *color_opts: str) -> None:
        """Add or update color opts for a log level.

        :param level:
            Log level to apply a style to, e.g. ``logging.INFO``.
        :param color_opts:
            ANSI escape sequence color options. Capitalized colors indicates
            background color, i.e. ``'green', 'Yellow', 'bold'`` will give bold
            green text on yellow background.

        .. warning::
            This is an experimental API.
        """
        assert self._fmt is not None
        levelname_fmt_match = self.LEVELNAME_FMT_REGEX.search(self._fmt)
        if not levelname_fmt_match:
            return
        levelname_fmt = levelname_fmt_match.group()

        formatted_levelname = levelname_fmt % {"levelname": logging.getLevelName(level)}

        # add ANSI escape sequences around the formatted levelname
        color_kwargs = {name: True for name in color_opts}
        colorized_formatted_levelname = self.markup(
            formatted_levelname, **color_kwargs
        )
        self._level_to_fmt_mapping[level] = self.LEVELNAME_FMT_REGEX.sub(
            colorized_formatted_levelname, self._fmt
        )

    def format(self, record: logging.LogRecord) -> str:
        fmt = self._level_to_fmt_mapping.get(record.levelno, self._original_fmt)
        self._style._fmt = fmt
        return super().format(record)
    

def get_logger(name: str = __name__, level: LogLevel = LogLevel.DEBUG) -> logging.Logger:
    env = Environment.get_environment_variables()

    # Create a named logger
    logger = logging.getLogger(name=name)
    logger.setLevel(level.value)  # Set logger level using enum value
    
    path = f'./logs'
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)

    # CONSOLE
    if env.LOG_CLI:
        # Create handlers
        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setLevel(level=env.LOG_CLI_LEVEL)
        # Create formatters and add it to handlers
        # c_format = logging.Formatter(fmt=env.LOG_CLI_FORMAT, datefmt=env.LOG_CLI_DATE_FORMAT)
        c_color_format = ColoredLevelFormatter(fmt=env.LOG_CLI_FORMAT, datefmt=env.LOG_CLI_DATE_FORMAT)
        c_handler.setFormatter(fmt=c_color_format)        
        # Add handlers to the logger
        logger.addHandler(hdlr=c_handler)
        
    # # FILE
    # if env_ext.LOG_FILE or len(env_ext.LOG_FILE) > 0:
    #     # Create handlers
    #     f_handler = logging.FileHandler(filename=env_ext.LOG_FILE, mode=env_ext.LOG_FILE_MODE)
    #     f_handler.setLevel(level=env_ext.LOG_FILE_LEVEL)
    #     # Create formatters and add it to handlers
    #     f_format = logging.Formatter(fmt=env_ext.LOG_FILE_FORMAT, datefmt=env_ext.LOG_FILE_DATE_FORMAT)
    #     f_handler.setFormatter(fmt=f_format)        
    #     # Add handlers to the logger
    #     logger.addHandler(hdlr=f_handler)
        
    
    # FILE ROTATING (GENERAL)
    if env.LOG_FILE or len(env.LOG_FILE) > 0:
        # Create handlers
        f_handler = logging.handlers.RotatingFileHandler(filename=env.LOG_FILE, mode=env.LOG_FILE_MODE, maxBytes=env.LOG_FILE_MAX_BYTES, backupCount=env.LOG_FILE_BACKUP_COUNT)
        f_handler.setLevel(level=env.LOG_FILE_LEVEL)
        # Create formatters and add it to handlers
        f_format = logging.Formatter(fmt=env.LOG_FILE_FORMAT, datefmt=env.LOG_FILE_DATE_FORMAT)
        f_handler.setFormatter(fmt=f_format)        
        # Add handlers to the logger
        logger.addHandler(hdlr=f_handler)
        
    
    # FILE ROTATING (DEBUG)
    if env.LOG_FILE_DEBUG_PATH or len(env.LOG_FILE_DEBUG_PATH) > 0:
        # Create handlers
        fd_handler = logging.handlers.RotatingFileHandler(filename=env.LOG_FILE_DEBUG_PATH, mode=env.LOG_FILE_MODE, maxBytes=env.LOG_FILE_MAX_BYTES, backupCount=env.LOG_FILE_BACKUP_COUNT)
        fd_handler.setLevel(level=LogLevel.DEBUG.value)
        # Create formatters and add it to handlers
        fd_format = logging.Formatter(fmt=env.LOG_FILE_FORMAT, datefmt=env.LOG_FILE_DATE_FORMAT)
        fd_handler.setFormatter(fmt=fd_format)        
        # Add handlers to the logger
        logger.addHandler(hdlr=fd_handler)
        
    
    # FILE ROTATING (WARNING)
    if env.LOG_FILE_WARNING_PATH or len(env.LOG_FILE_WARNING_PATH) > 0:
        # Create handlers
        fw_handler = logging.handlers.RotatingFileHandler(filename=env.LOG_FILE_WARNING_PATH, mode=env.LOG_FILE_MODE, maxBytes=env.LOG_FILE_MAX_BYTES, backupCount=env.LOG_FILE_BACKUP_COUNT)
        fw_handler.setLevel(level=LogLevel.WARNING.value)
        # Create formatters and add it to handlers
        fw_format = logging.Formatter(fmt=env.LOG_FILE_FORMAT, datefmt=env.LOG_FILE_DATE_FORMAT)
        fw_handler.setFormatter(fmt=fw_format)        
        # Add handlers to the logger
        logger.addHandler(hdlr=fw_handler)
    
    
    return logger

