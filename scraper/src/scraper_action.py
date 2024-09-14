'''
Configuration settings like base URLs, headers, timeouts, etc.import requests
'''
import requests
from bs4 import BeautifulSoup
from scraper.src.utils import setup_logging
from selenium import webdriver
import pdfplumber
from PIL import Image
import pytesseract
from io import BytesIO
from urllib.request import Request, urlopen

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

    # Extract text from images
    image_extracted = {}
    for image in images: 
        if image: 
            text = extract_image_text(image)
            image_extracted[image] = text
        else:
            logger.info(f"Failed to retrieve or extract the image text: {image}")

    # Collect data into a dictionary
    data = {
        "url": url,
        "title": page_title,
        "texts": texts,
        "images": images,
        "pdf_links": pdf_links,
        "pdf_extracted": pdf_extracted,
        "image_extracted": image_extracted
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
        req = Request(image, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})  # accepts any image type
        response = urlopen(req)
        # load image data
        image_data = response.read()
        # open image
        image = Image.open(BytesIO(image_data))
        # extract text from image url using pytesseract
        text = pytesseract.image_to_string(image)
        logger.info(f"Extracting text from image using OCR: , {text}")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from image: {e}")
        return ""
