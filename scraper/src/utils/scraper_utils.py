import logging
import json
import hashlib

def setup_logging():
    # Open the file in write mode ('w') to clear it before new logs are written
    logging.basicConfig(
        filename='scraper/logs/scraper.log', 
        level=logging.INFO, 
        format='%(asctime)s:%(levelname)s:%(message)s',
        filemode='w'
    )
    return logging.getLogger()

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def generate_hash(text):
    """
    Generate a SHA-256 hash from the provided text.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()