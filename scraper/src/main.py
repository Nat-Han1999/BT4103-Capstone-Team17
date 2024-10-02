import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.src.scraper_action import get_urls, fetch_page, parse_content, fetch_page_with_selenium
from scraper.src.scraper_utils import setup_logging, save_to_json
from dotenv import load_dotenv

from scraper.backend.mongo_utils import get_database, insert_many_documents

logger = setup_logging()

# Load environment variables from the .env file
load_dotenv()

# Global Variables
username = os.getenv("MONGO_DB_USERNAME")
password = os.getenv("MONGO_DB_PASSWORD")
ca_file = os.path.join(os.path.dirname(__file__), '../backend/isrgrootx1.pem')

def main():
    print("Starting scraper...")
    start = time.time()

    # Website url
    url = "https://www.svf.gov.lk"

    # Get all relevant websites under mainMenu class (navigation bar)
    urls = get_urls(url, "mainMenu")

    logger.info("Fetching page content using requests...")
    all_data_requests = []  # to hold all scraped data using requests
    all_data_selenium = []  # to hold all scraped data using Selenium

    logger.info("Fetching page content using requests...")
    for url in urls:
        logger.info(f"Fetching page content from {url} using requests...")
        html_content = fetch_page(url)
        if html_content:
            data = parse_content(html_content, url)
            all_data_requests.append(data)

    save_to_json(all_data_requests, 'scraper/scraped_data/data_requests.json') # to remove
    # Insert the scraped data into MongoDB
    collection = get_database("shrama_vasana_fund_uat", "scraped_data_requests", username, password, ca_file)
    inserted_ids = insert_many_documents(collection, all_data_requests)

    logger.info(f"Inserted requests data, {len(inserted_ids)} documents into MongoDB.")

    logger.info("Fetching page content using Selenium...")
    for url in urls:
        logger.info(f"Fetching page content from {url} using Selenium...")
        html_content = fetch_page_with_selenium(url)
        if html_content:
            data = parse_content(html_content, url)
            all_data_selenium.append(data)
    
    save_to_json(all_data_selenium, 'scraper/scraped_data/data_selenium.json') # to remove

    # Insert the scraped data into MongoDB
    collection = get_database("shrama_vasana_fund_uat", "scraped_data_selenium", username, password, ca_file)
    inserted_ids = insert_many_documents(collection, all_data_selenium)

    logger.info(f"Inserted selenium data, {len(inserted_ids)} documents into MongoDB.")
        
    end = time.time()
    print(f"Done with webs scraping, time taken: {end-start}.")

if __name__ == "__main__":
    main()
