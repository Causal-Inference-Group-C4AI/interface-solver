import logging
import warnings


def suppress_warnings() -> None:
    """Suppress all warnings and logging messages."""
    warnings.filterwarnings("ignore", category=Warning)
    logging.getLogger().setLevel(logging.CRITICAL)
