import time
import os
import traceback

from scraper.src.scraper_action import scrape_and_store_data, get_all_links
from scraper.src.utils.scraper_utils import setup_logging, load_json_file
from dotenv import load_dotenv
from datetime import datetime
from scraper.backend.mongo_utils import get_database

logger, log_stream = setup_logging()

# Load environment variables from the .env file
load_dotenv()

# Global Variables
username = os.getenv("MONGO_DB_USERNAME")
password = os.getenv("MONGO_DB_PASSWORD")
    
def main():
    """
    Main function to run the web scraper.
    """
    logger, log_stream = setup_logging()
    logger.info("Starting web scraper...")

    try:

        start = time.time()

        config_file = 'scraper/config.json'
        config = load_json_file(config_file)
        base_url = "https://www.svf.gov.lk/index.php?lang=en" 
                    
        collection_all_domain_links = get_database("shrama_vasana_fund", "all_domain_links", username, password)

        # Query to find all documents where scrape_flag is True and extract URLs
        urls_with_true_flag = collection_all_domain_links.find(
            {"scrape_flag": True},  # Filter condition where scrape_flag is True
            {"url": 1, "_id": 0}    # Projection to include only the 'url' field, excluding '_id'
        )

        # Extract the URLs into a list
        url_list = [doc['url'] for doc in urls_with_true_flag]
        url_list = url_list[0:2]

        # MongoDB connection
        collection_scraped_data = get_database("shrama_vasana_fund", "scraped_data", username, password)
        collection_url_hashed = get_database("shrama_vasana_fund", "url_hashed", username, password)

        # Scrape URLs and store data
        scrape_and_store_data(url_list, collection_scraped_data, collection_url_hashed, config, base_url)

        end = time.time()
        print(f"Done with web scraping. Time taken: {end - start}.")
    
    except Exception as e:
        trace_info = traceback.format_exc()
        logger.error(f"An error occurred: {e}\nTraceback: {trace_info}")

    finally:
        log_collection = get_database("shrama_vasana_fund", "all_logs", username, password)
        logs_content = log_stream.getvalue()
        log_document = {"session_logs": logs_content, "timestamp": datetime.now()}
        log_collection.insert_one(log_document)
        log_stream.close()


if __name__ == "__main__":
    main()