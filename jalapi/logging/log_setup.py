import logging

# Create logger at the module level
logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False) -> None:
    """Configure logging with consistent format and level"""
    log_level = logging.DEBUG if debug else logging.INFO

    # Remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set up logging with a single configuration
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)

    logger.debug("Logging initialized at level %s", logging.getLevelName(log_level))
