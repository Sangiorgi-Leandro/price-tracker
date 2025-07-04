import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Configures the application-wide logging system.

    Sets up a console handler and a rotating file handler.
    Logs will be written to both the console and 'scraper.log'.
    The log file will rotate when it reaches 5MB, keeping 3 backup files.
    """
    # Define the log message format: timestamp [level] logger_name: message
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Configure the basic logging to output to the console.
    # Sets the default logging level to INFO, meaning INFO, WARNING, ERROR, CRITICAL messages will be shown.
    logging.basicConfig(level=logging.INFO, format=log_format)

    # Set up a RotatingFileHandler to write logs to a file.
    # 'scraper.log': The name of the log file.
    # maxBytes=5_000_000 (5 MB): The maximum size of the log file before it's rotated.
    # backupCount=3: The number of backup log files to keep (e.g., scraper.log.1, scraper.log.2, scraper.log.3).
    file_handler = RotatingFileHandler("scraper.log", maxBytes=5_000_000, backupCount=3)
    # Apply the same format to the file handler as well.
    file_handler.setFormatter(logging.Formatter(log_format))

    # Add the file handler to the root logger.
    # This ensures that all log messages throughout the application (from any logger)
    # will also be written to the rotating file.
    logging.getLogger().addHandler(file_handler)
