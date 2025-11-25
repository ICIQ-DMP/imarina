import logging
import logging.handlers
import os

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """Configure and return a logger instance."""

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent double logging

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler (with rotation)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5_000_000, backupCount=5
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger