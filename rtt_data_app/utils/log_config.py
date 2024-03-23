# log_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_global_logging(log_path):
    log_directory = log_path  # Adjust the path as necessary
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = os.path.join(log_directory, 'flask_app.log')

    # Create a rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=3)
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Get the root logger and set the handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logger.addHandler(handler)

    # If you want to also print to console, uncomment the following lines:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
