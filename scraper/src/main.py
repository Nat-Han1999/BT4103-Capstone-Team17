from scraper_action import fetch_page, parse_content, fetch_page_with_selenium
from utils import setup_logging, save_to_json

logger = setup_logging()

def main():
    urls = [
        "https://www.svf.gov.lk/index.php?lang=en",
        "https://www.svf.gov.lk/index.php?option=com_content&view=article&id=1&Itemid=115&lang=en"
    ]

    logger.info("Fetching page content using requests...")
    all_data_requests = []  # to hold all scraped data using requests
    all_data_selenium = []  # to hold all scraped data using Selenium

    for url in urls:
        logger.info(f"Fetching page content from {url} using requests...")
        html_content = fetch_page(url)
        if html_content:
            data = parse_content(html_content, url)
            all_data_requests.append(data)

    save_to_json(all_data_requests, 'scraped_data/data_requests.json')

    logger.info("Fetching page content using Selenium...")
    for url in urls:
        logger.info(f"Fetching page content from {url} using Selenium...")
        html_content = fetch_page_with_selenium(url)
        if html_content:
            data = parse_content(html_content, url)
            all_data_selenium.append(data)

    save_to_json(all_data_selenium, 'scraped_data/data_selenium.json')

if __name__ == "__main__":
    main()
