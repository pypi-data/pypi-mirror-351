"""
Contains the core of $package: ... , etc.

NOTE: this module is private. All functions and objects are available in the main
`$package` namespace - use that instead.

"""

import logging
import sys
from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, NOTSET, WARN, WARNING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import _Level

    from hintwith import hintwith

__all__ = [
    "get_logger",
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "FATAL",
    "INFO",
    "NOTSET",
    "WARN",
    "WARNING",
    "critical",
    "debug",
    "error",
    "fatal",
    "info",
    "warn",
    "warning",
]


def get_logger(
    name: str | None = None, level: "_Level | None" = None
) -> logging.Logger:
    """
    Return a logger with the specified name, creating it and adding a
    default handler if necessary.

    Parameters
    ----------
    name : str | None, optional
        Logger name, by default None. If not specified, use `__name__`
        of the calling function's module.
    level : _Level | None, optional
        Specifies logging level of the logger.

    Returns
    -------
    logging.Logger
        Logger with the specified name.

    """

    if name is None:
        name = __get_module_name()
    if name == "__main__":
        name = None
    logger = logging.getLogger(name)
    logger.propagate = False
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    if level is not None:
        logger.setLevel(level)
    return logger


if TYPE_CHECKING:

    @hintwith(logging.critical, True)
    def critical():
        """Log a message with severity 'CRITICAL' on the module logger."""

    @hintwith(logging.debug, True)
    def debug():
        """Log a message with severity 'DEBUG' on the module logger."""

    @hintwith(logging.error, True)
    def error():
        """Log a message with severity 'ERROR' on the module logger."""

    @hintwith(logging.critical, True)
    def fatal():
        """Log a message with severity 'CRITICAL' on the module logger."""

    @hintwith(logging.info, True)
    def info():
        """Log a message with severity 'INFO' on the module logger."""

    @hintwith(logging.warning, True)
    def warn():
        """Log a message with severity 'WARNING' on the module logger."""

    @hintwith(logging.warning, True)
    def warning():
        """Log a message with severity 'WARNING' on the module logger."""

else:

    def critical(*args, **kwargs):
        """Magic happens."""
        return get_logger(__get_module_name()).critical(*args, **kwargs)

    def debug(*args, **kwargs):
        """Magic happens."""
        return get_logger(__get_module_name()).debug(*args, **kwargs)

    def error(*args, **kwargs):
        """Magic happens."""
        return get_logger(__get_module_name()).error(*args, **kwargs)

    def fatal(*args, **kwargs):
        """Magic happens."""
        return get_logger(__get_module_name()).critical(*args, **kwargs)

    def info(*args, **kwargs):
        """Magic happens."""
        return get_logger(__get_module_name()).info(*args, **kwargs)

    def warn(*args, **kwargs):
        """Magic happens."""
        return get_logger(__get_module_name()).warning(*args, **kwargs)

    def warning(*args, **kwargs):
        """Magic happens."""
        return get_logger(__get_module_name()).warning(*args, **kwargs)


def __get_module_name() -> str:
    frame = sys._getframe(2)  # pylint: disable=protected-access
    return frame.f_globals["__name__"]
