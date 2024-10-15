'''
Configuration settings like base URLs, headers, timeouts, etc.import requests
'''
import requests
import time

import pdfplumber
import pytesseract

from bs4 import BeautifulSoup
from scraper.src.processing import remove_duplicates, process_texts, process_extracted_texts
from scraper.src.utils.scraper_utils import setup_logging, generate_hash
from selenium import webdriver
from PIL import Image
from io import BytesIO
from urllib.request import Request, urlopen
from datetime import datetime, timedelta, timezone
from scraper.backend.mongo_utils import insert_many_documents, update_one_document, insert_one_document
from scraper.src.diff import render_diff
from selenium.common.exceptions import TimeoutException, WebDriverException
import concurrent
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import asyncio
import logging
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser
import heapq
from scraper.backend.mongo_utils import insert_many_documents, update_one_document, insert_one_document
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from datetime import datetime, timedelta, timezone
import concurrent
from concurrent.futures import ThreadPoolExecutor
import requests
from io import BytesIO
from PIL import Image
import pytesseract
import pdfplumber

logger = setup_logging()

# Set up a robots.txt parser
def can_fetch(url):
    rp = urllib.robotparser.RobotFileParser()
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch("*", url)
    except:
        return True  # If there's an issue with robots.txt, allow by default

def normalize_url(url):
    parsed_url = urlparse(url)
    return parsed_url._replace(fragment="").geturl()

# Fetch page asynchronously
async def fetch_page_for_crawler(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None

def is_valid_webpage(url, domain):
    # Check for valid domain and valid URL format
    parsed_url = urlparse(url)
    if parsed_url.netloc != domain:
        return False
    
    # Skip non-webpage files (e.g., .pdf, .jpg, .png)
    file_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx']
    return not any(url.lower().endswith(ext) for ext in file_extensions)

def hash_content(content):
    """ Create a hash for the page content to avoid duplicates """
    return hashlib.md5(content.encode()).hexdigest()

async def get_all_links(base_url, max_depth=2, delay=1):
    visited_links = set()
    content_hashes = set()
    priority_queue = []
    heapq.heappush(priority_queue, (0, base_url))  # (priority, url)
    base_domain = urlparse(base_url).netloc

    async with aiohttp.ClientSession() as session:
        while priority_queue:
            depth, current_url = heapq.heappop(priority_queue)
            normalized_url = normalize_url(current_url)

            if normalized_url in visited_links or depth > max_depth or not can_fetch(current_url):
                continue

            page_content = await fetch_page_for_crawler(current_url, session)
            print(f"Fetching: {current_url}")
            if page_content:
                visited_links.add(normalized_url)

                # Avoid duplicate content
                content_hash = hash_content(page_content)
                if content_hash in content_hashes:
                    continue
                content_hashes.add(content_hash)

                soup = BeautifulSoup(page_content, 'html.parser')

                # Extract all valid webpage links
                for a_tag in soup.find_all('a', href=True):
                    full_url = urljoin(base_url, a_tag['href'])
                    normalized_full_url = normalize_url(full_url)
                    if normalized_full_url not in visited_links and is_valid_webpage(normalized_full_url, base_domain):
                        heapq.heappush(priority_queue, (depth + 1, normalized_full_url))  # Increase depth by 1
            
            # Respect politeness, add delay
            await asyncio.sleep(delay)

    return visited_links

def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
       
def fetch_page_with_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    remote_webdriver = 'http://localhost:4444/wd/hub'  # Remote URL for ChromeDriver
    try:
        # Use remote Selenium ChromeDriver
        driver = webdriver.Remote(remote_webdriver, options=options)
        driver.set_page_load_timeout(30)  # Timeout after 30 seconds if the page doesn't load
        driver.set_script_timeout(30)  # Timeout for script execution
        
        logger.info(f"Fetching {url} using Selenium...")
        driver.get(url)
        html_content = driver.page_source
        logger.info(f"Successfully fetched content from {url}")
    except TimeoutException:
        logger.error(f"Timeout while loading page {url}")
        html_content = None
    except WebDriverException as e:
        logger.error(f"WebDriver error occurred for {url}: {str(e)}")
        html_content = None
    except Exception as e:
        if "Connection refused" in str(e):
            logger.error(f"Failed to connect to Selenium: {str(e)}.")
            logger.error("Ensure the Selenium Docker container is running.")
            raise
        else:
            logger.error(f"Error fetching {url} with Selenium: {str(e)}")
        html_content = None
    finally:
        if driver:
            try:
                driver.quit()  # Ensure that the driver quits to free up resources
            except Exception as e:
                logger.error(f"Error quitting Selenium driver: {str(e)}")
    return html_content

# TODO: Should remove using predefined xpaths

# def remove_elements_by_classes(soup, classes, footers = None): 
#     """
#     Remove all elements from a BeautifulSoup object that contain any class in the classes list.
#     Removes footer if specified.
#     Args:
#         soup: BeautifulSoup object representing the parsed html.
#         classes: List of strings (class names) to be removed.
#         footer: Specified footer to be removed.
#     Returns:
#         A BeautifulSoup object representing the parsed html.
#     """
#     for class_ in classes:
#         elements = soup.find_all(class_= class_)
#         for element in elements: 
#             element.decompose() # remove element
#         # Remove all <footer> tags
    
#     for footer in footers:
#         footer.decompose()  # remove footer tags

#     return soup

def parse_content(html, url):
    soup = BeautifulSoup(html, 'html.parser')

    # TODO: Should not use own pre-defined classes
    # ignore_classes = ["twobannersLg", "nav menu", "mm-menu mm-offcanvas", "breadcrumb", "foot-1col commonFoot"] # lotteries, navBar, footer
    # footers = soup.find_all('footer') # ignore footers
    # soup = remove_elements_by_classes(soup, ignore_classes, footers)

    # Extract the page title
    page_title = soup.title.text if soup.title else "No title found"
    logger.info("Page Title: " + page_title)

    # Extract text from paragraphs, divs, and spans
    logger.info("Extracting text from paragraphs, divs, and spans")
    texts = [] 
    tags = soup.find_all(['p', 'div', 'span'])

    # Check whether current tag is nested within any other tags
    for tag in tags:
        if not any(parent in tag.parents for parent in tags): # condition is true only if current tag is not a child of other tags
            for string in tag.stripped_strings:  # extracts text node by node
                text = ' '.join(string.split())
                if text:  # check if the text is not empty
                    texts.append(text)

    logger.info("Processing texts")
    texts = process_texts(remove_duplicates(texts)) # process texts

    # Extract images
    logger.info("Extracting images from the page")
    images = extract_images(soup)
    if images:
        logger.info("Images found: " + ', '.join(images))
    else:
        logger.info("No images found")

    # Extract PDF links
    logger.info("Extracting PDF links from the page")
    pdf_links = extract_pdf_links(soup)
    if pdf_links:
        logger.info("PDF Links found: " + ', '.join(pdf_links))
    else:
        logger.info("No PDF links found")
    
    # Extract text from PDF links
    pdf_extracted = {}
    for pdf_link in pdf_links: 
        if pdf_link:
            pdf_file = download_pdf(pdf_link)
            logger.info(f"Downloading file from PDF link: {pdf_file}")
            extracted_text = extract_pdf_text(pdf_file)
            pdf_extracted[pdf_link] = extracted_text
        else:
            logger.info(f"Failed to retrieve or extract the PDF text: {pdf_link}")
    logger.info("Processing extracted pdf texts")
    pdf_extracted = process_extracted_texts(pdf_extracted)

    # Extract text from images
    image_extracted = {}
    for image in images: 
        if image: 
            text = extract_image_text(image)
            image_extracted[image] = text
        else:
            logger.info(f"Failed to retrieve or extract the image text: {image}")
    logger.info("Processing extracted pdf texts")
    image_extracted = process_extracted_texts(image_extracted)

    # Collect data into a dictionary
    scraped_time = datetime.now(timezone(timedelta(hours=8)))

    data = {
        "url": url,
        "title": page_title,
        "texts": texts,
        "images": images,
        "pdf_links": pdf_links,
        "pdf_extracted": pdf_extracted,
        "image_extracted": image_extracted,
        "scraped_at": scraped_time
    }
    return data

def extract_images(soup):
    images = []
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url:
            # Handle relative URLs
            if img_url.startswith('/'):
                img_url = 'https://www.svf.gov.lk' + img_url
            images.append(img_url)
    return images

def extract_pdf_links(soup):
    pdf_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.pdf'):
            # Handle relative URLs
            if href.startswith('/'):
                href = 'https://www.svf.gov.lk' + href
            pdf_links.append(href)
    return pdf_links

def download_pdf(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # check for errors
        return BytesIO(response.content)  # file-like object
    except Exception as e:
        logger.error(f"Failed to download PDF: {e}")
        return None

def extract_pdf_text(pdf_file): 
    text = ""
    if not pdf_file:
        logger.error("No PDF file to extract text from.")
        return text
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    # extract text directly
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text += extracted_text
                    else:
                        # If no text found, attempt OCR
                        logger.info(f"Extracting pdf text... Performing OCR on page {page_num + 1}")
                        page_image = page.to_image(resolution=300)
                        ocr_text = pytesseract.image_to_string(page_image.original)
                        text += ocr_text
                except Exception as e:
                    logger.error(f"Extracting pdf text... Error on page {page_num + 1}: {e}")
    except Exception as e: 
        logger.error(f"Failed to open PDF: {e}")
    return text

def extract_image_text(image): 
    try:        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(image, headers=headers)
        image_data = BytesIO(response.content)
        image = Image.open(image_data)
        text = pytesseract.image_to_string(image)
        logger.info(f"Extracting text from image using OCR: , {text}")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from image: {e}")
        return None

def process_and_hash_text(data):
    """
    Concatenate and hash the text content from the scraped data.
    """

    if 'texts' in data and isinstance(data['texts'], list):
        concatenated_text = ' '.join(data['texts'])
        return generate_hash(concatenated_text)
    return None

def update_or_insert_document(collection_url_hashed, collection_scraped_data, url, text_hash, newly_scraped_data):
    """
    Update or insert URL hash and metadata in MongoDB.
    """
    current_time = datetime.now(timezone(timedelta(hours=0)))

    query = {"url": url}
    existing_doc = collection_url_hashed.find_one(query)
    content_scraped_previously = collection_scraped_data.find_one(query, sort=[('scraped_at', -1)])

    if existing_doc !=  None and content_scraped_previously != None:
        last_hash = existing_doc.get("latest_hash", "")
        last_text_content = content_scraped_previously.get("texts", [""]) # Get the previous text for comparison

        if text_hash != last_hash:
            
            new_text_list = newly_scraped_data["texts"]
            new_text = "\n".join(new_text_list)
            last_text = "\n".join(last_text_content)

            # TODO: need to update scraped_data collection too. Need to render difference and send notification
            diff = render_diff(
                previous_version_file_contents=last_text, 
                newest_version_file_contents=new_text,
                include_equal=False  # Show only differences
            )
            
            print(url, "DIFFERENCE --------------------------")
            print(diff)

            update_hash_data = {
                "last_updated_at": current_time,
                "latest_hash": text_hash,
                "scrape_count": existing_doc.get("scrape_count", 1) + 1
            }
            update_one_document(collection_url_hashed, query, update_hash_data)
            
            update_scraped_data = newly_scraped_data
            update_one_document(collection_scraped_data, query, update_scraped_data)

        # need to update the content scraped previously also
    else:
        # Scraped data and hash does not exist in MongoDB. Load them in.
        if existing_doc == None:
            new_hash_data = {
                "url": url,
                "created_at": current_time,
                "last_updated_at": current_time,
                "first_hash": text_hash,
                "latest_hash": text_hash,
                "scrape_count": 1
            }
            insert_one_document(collection_url_hashed, new_hash_data)
            logger.info(f"Inserted {url} into hash_url collection.")

        if content_scraped_previously == None:
            insert_one_document(collection_scraped_data, newly_scraped_data)
            logger.info(f"Inserted {url} into scraped_data collection.")

def fetch_and_process(url):
    """
    Fetch page content using Selenium, process the html content, and return the processed data.
    """
    logger.info(f"Fetching page content from {url} using Selenium...")
    html_content = fetch_page_with_selenium(url)
    if not html_content:
        logger.info(f"No content scraped from {url}")
        return None

    data = parse_content(html_content, url)
    text_hash = process_and_hash_text(data)
    return url, text_hash, data

def scrape_and_store_data(urls, collection_scraped_data, collection_url_hashed):
    """
    Fetch content for each URL, process it, and store or update in MongoDB.
    """
    
    all_data_selenium = []

    with ThreadPoolExecutor() as executor: 
        futures = {executor.submit(fetch_and_process, url): url for url in urls}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                url, text_hash, data = result 
                logger.info(f"Data scraped: {data}")
                logger.info(f"Text hashed: {text_hash}")

                # Update or insert the hash and metadata in MongoDB
                update_or_insert_document(collection_url_hashed, collection_scraped_data, url, text_hash, data)
                all_data_selenium.append(data)

        all_data_selenium.append(data)

    # Check if there's any data to insert
    if not all_data_selenium:
        logger.error("No data scraped, nothing to insert.")