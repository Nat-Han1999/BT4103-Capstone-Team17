import time
import os
import asyncio

from scraper.src.scraper_action import scrape_and_store_data, get_all_links
from scraper.src.utils.scraper_utils import setup_logging
from dotenv import load_dotenv
from datetime import datetime
from scraper.backend.mongo_utils import get_database

logger = setup_logging()

# Load environment variables from the .env file
load_dotenv()

# Global Variables
username = os.getenv("MONGO_DB_USERNAME")
password = os.getenv("MONGO_DB_PASSWORD")
ca_file = os.path.join(os.path.dirname(__file__), './backend/isrgrootx1.pem')

async def main():
    """
    Main function to run the web scraper.
    """

    try:
        print("Starting web scraper...")
        start = time.time()

        base_url = "https://www.svf.gov.lk/index.php?lang=en" 
        max_depth = 2  # Set the max depth limit here

        # Fetch URLs asynchronously
        urls = await get_all_links(base_url, 'scraper/config.json', max_depth, delay=1) 

        # MongoDB setup
        collection_scraped_data = get_database("shrama_vasana_fund", "scraped_data", username, password, ca_file)
        collection_url_hashed = get_database("shrama_vasana_fund", "url_hashed", username, password, ca_file)

        # Scrape URLs and store data
        scrape_and_store_data(urls, collection_scraped_data, collection_url_hashed)

        end = time.time()
        print(f"Done with web scraping. Time taken: {end - start}.")
    
    except Exception as e:
        raise

if __name__ == "__main__":
    asyncio.run(main())