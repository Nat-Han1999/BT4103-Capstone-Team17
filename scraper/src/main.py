import time
import os

from scraper.src.scraper_action import fetch_page, parse_content, fetch_page_with_selenium
from scraper.src.utils import setup_logging, save_to_json
from dotenv import load_dotenv

from scraper.backend.utils import get_database, insert_many_documents

logger = setup_logging()

# Load environment variables from the .env file
load_dotenv()

# Global Variables
username = os.getenv("MONGO_DB_USERNAME")
password = os.getenv("MONGO_DB_PASSWORD")
ca_file = os.getenv("CA_FILE_PATH")

def main():
    print("Starting webscraper...")
    start = time.time()

    #TODO: Need to upupgrade to crawler to get all relevant websites
    urls = [
    "https://www.svf.gov.lk/index.php?lang=en",  # home
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

    # save_to_json(all_data_requests, '../scraped_data/data_requests.json')

    logger.info("Fetching page content using Selenium...")
    for url in urls:
        logger.info(f"Fetching page content from {url} using Selenium...")
        html_content = fetch_page_with_selenium(url)
        if html_content:
            data = parse_content(html_content, url)
            all_data_selenium.append(data)

    # Insert the scraped data into MongoDB
    collection = get_database("shrama_vasana_fund_uat", "scraped_data", username, password, ca_file)
    inserted_ids = insert_many_documents(collection, all_data_selenium)

    logger.info(f"Inserted {len(inserted_ids)} documents into MongoDB.")
        
    end = time.time()
    print(f"Done with webs scraping, time taken: {end-start}.")

if __name__ == "__main__":
    main()
