import logging

from rich.logging import RichHandler


def setup_logging(verbose):
    """Setup logging configuration."""
    log_level = logging.DEBUG if verbose else logging.WARNING
    FORMAT = "%(message)s"
    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    return logging.getLogger("rich")
