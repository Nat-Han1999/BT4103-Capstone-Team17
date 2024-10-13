import time
import os

from scraper.src.scraper_action import scrape_and_store_data
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

def main():
    """
    Main function to run the web scraper.
    """

    try:
        print("Starting web scraper...")
        start = time.time()

        # Get URLs to scrape
        urls = [
        "https://www.svf.gov.lk/index.php?lang=en",
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=1&Itemid=115&lang=en",  # about us
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=6&Itemid=109&lang=en",  # contributions
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=7&Itemid=110&lang=en#promotion-of-the-welfare-of-the-workers",  # services
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=8&Itemid=111&lang=en",  # downloads
        "https://www.svf.gov.lk/index.php?option=com_phocagallery&view=categories&Itemid=137&lang=en",  # gallery (image gallery)
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=12&Itemid=138&lang=en",  # gallery (video gallery)
        "https://www.svf.gov.lk/index.php?option=com_content&view=category&layout=blog&id=8&Itemid=139&lang=en",  # news and events
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=13&Itemid=140&lang=en",  # donate us
        "https://www.svf.gov.lk/index.php?option=com_content&view=category&id=9&Itemid=114&lang=en",  # vacancy
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=14&Itemid=141&lang=en",  # faq
        "https://www.svf.gov.lk/index.php?option=com_contact&view=contact&id=1&Itemid=135&lang=en#",  # contact us (inquiry)
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=18&Itemid=147&lang=en",  # contact us (contact details)
        "https://www.svf.gov.lk/index.php?option=com_xmap&view=html&id=1&Itemid=142&lang=en"  # site map
        ]

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
    main()