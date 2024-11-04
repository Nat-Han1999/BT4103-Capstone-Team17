import logging
import json
import hashlib
import os

import logging
from io import StringIO

# Global in-memory log storage
log_stream = StringIO()

def setup_logging():
    """
    Set up logging to capture logs in memory. Only setup once.
    """
    logger = logging.getLogger("scraper_logger")
    if not logger.handlers:  # Ensure we add the handler only once
        logger.setLevel(logging.INFO)  # Set the default logging level
        stream_handler = logging.StreamHandler(log_stream)
        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger, log_stream

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_website_conditions(base_url, config):
    for website in config['websites']:
        if base_url == website['base_url']:
            return website['conditions']
    return None

def get_ignore_xpaths(base_url, config):
    for website in config['websites']:
        if base_url == website['base_url']:
            return website['conditions']['ignore_xpaths']
        
    return None

def load_json_file(filename): 
    with open(filename, 'r') as f:
        return json.load(f)

def generate_hash(text):
    """
    Generate a SHA-256 hash from the provided text.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()