'''
Configuration settings like base URLs, headers, timeouts, etc.import requests
'''
import requests
from bs4 import BeautifulSoup
from utils import setup_logging
from selenium import webdriver

logger = setup_logging()

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
        return None

def fetch_page_with_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html_content = driver.page_source
    driver.quit()
    return html_content

def parse_content(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract the page title
    page_title = soup.title.text if soup.title else "No title found"
    logger.info("Page Title: " + page_title)

    # Extract text from paragraphs, divs, and spans
    logger.info("Extracting text from paragraphs, divs, and spans")
    texts = [] 
    div_tag = soup.find('div')
    tags = soup.find_all(['p', 'div', 'span'])

    # Check whether current tag is nested within any other tags
    for tag in tags:
        if not any(parent in tag.parents for parent in tags): # condition is true only if current tag is not a child of other tags
            for string in tag.stripped_strings:  # extracts text node by node
                text = ' '.join(string.split())
                if text:  # check if the text is not empty
                    texts.append(text)  

    texts_ls_length = len(texts)  
    logger.info("Texts found: " + ', '.join(texts[:5]))  # Only log the first 5 for brevity

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

    # Collect data into a dictionary
    data = {
        "url": url,
        "title": page_title,
        "texts": texts,
        "images": images,
        "pdf_links": pdf_links
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
