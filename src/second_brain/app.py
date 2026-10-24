import sys

from loguru import logger

CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{extra[level_code]}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def configure_logging():
    """Configure loguru for console and file logging.

    Removes the default handler and sets up:
    - stderr handler at LOG_LEVEL (default: INFO, configurable via env var),
      using the compact CONSOLE_FORMAT
    - File handler at DEBUG level writing to LOG_FILE (default: app.log),
      using loguru's default format
    """
    import os

    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = os.environ.get("LOG_FILE", "app.log")
    logger.remove()
    # Expose a 3-letter level code (INF, WAR, ...) for CONSOLE_FORMAT.
    logger.configure(
        patcher=lambda record: record["extra"].update(
            level_code=record["level"].name[:3]
        )
    )
    logger.add(sys.stderr, level=log_level, format=CONSOLE_FORMAT)
    logger.add(log_file, level="DEBUG", rotation="50 KB", retention=1)


@logger.catch
def main():
    """Run the application.

    Configures logging and prints a greeting to verify the setup works.
    """
    configure_logging()
    logger.info("Hello from second_brain!")
