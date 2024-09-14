import logging
import json

def setup_logging():
    logging.basicConfig(filename='../logs/scraper.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
    return logging.getLogger()

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)