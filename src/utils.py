import logging
import os

def setup_logger(name, log_file="app.log"):
    """
    Logger to print in the console and save in file
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler for writing in the file
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Handler to print in the console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Set the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) # Καταγράφουμε από INFO και πάνω (όχι DEBUG)
    
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger