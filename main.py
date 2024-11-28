import sys
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import spacy
import re
import concurrent.futures
from urllib.parse import urljoin, urlparse
import logging

app = FastAPI()

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLItem(BaseModel):
    url: str
    max_depth: int = 2  # Default maximum depth of crawling

def scrape_page(url, base_domain, visited_urls, max_depth, current_depth):
    # Set the event loop policy for Windows
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Initialize data list to hold person information from multiple pages
    person_list = []

    if current_depth > max_depth:
        return person_list

    logger.info(f"Scraping URL: {url} at depth {current_depth}")

    # Avoid revisiting the same URL
    if url in visited_urls:
        return person_list
    visited_urls.add(url)

    try:
        # Fetch the page content using Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=60000)
            content = page.content()
            browser.close()
    except Exception as e:
        logger.error(f"Failed to load {url}: {e}")
        return person_list

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Extract text for NLP processing
    text = soup.get_text(separator=' ', strip=True)
    doc = nlp(text)

    # Extract names
    names = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']

    # Extract contact information
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    phone_numbers = re.findall(r'\+?\d[\d -]{8,15}\d', text)

    # Extract images
    images = [urljoin(url, img['src']) for img in soup.find_all('img') if img.get('src')]

    # Extract sentences for further information
    sentences = [sent.text.strip() for sent in doc.sents]

    # Initialize person data
    person_data = []

    # Iterate over names and attempt to associate other information
    for name in names:
        person = {
            'name': name,
            'contact-information': None,
            'image': None,
            'family-detail': None,
            'political_party_affiliation': None
        }

        # Attempt to find contact information near the name
        for sent in sentences:
            if name in sent:
                # Check for email
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', sent)
                if email_match:
                    person['contact-information'] = email_match.group(0)

                # Check for phone number
                phone_match = re.search(r'\+?\d[\d -]{8,15}\d', sent)
                if phone_match:
                    person['contact-information'] = phone_match.group(0)

                # Check for family details
                family_keywords = ['son', 'daughter', 'wife', 'husband', 'father', 'mother', 'spouse']
                if any(keyword in sent.lower() for keyword in family_keywords):
                    person['family-detail'] = sent

                # Check for political party affiliation
                party_keywords = ['party', 'political party', 'member of', 'affiliation']
                if any(keyword in sent.lower() for keyword in party_keywords):
                    person['political_party_affiliation'] = sent

                break  # Assuming the first match is sufficient

        # Assign an image if available
        if images:
            person['image'] = images[0]  # Assigning the first image found
        else:
            person['image'] = None

        person_list.append(person)

    # Find and crawl linked pages within the same domain
    links = []
    for link_tag in soup.find_all('a', href=True):
        href = link_tag['href']
        full_url = urljoin(url, href)
        parsed_url = urlparse(full_url)

        # Only follow links within the same domain
        if parsed_url.netloc == base_domain and full_url not in visited_urls:
            links.append(full_url)

    # Recursively crawl linked pages
    for link in links:
        person_list.extend(scrape_page(link, base_domain, visited_urls, max_depth, current_depth + 1))

    return person_list

@app.post("/scrape")
def scrape_url(url_item: URLItem):
    url = url_item.url
    max_depth = url_item.max_depth

    # Extract the base domain to limit crawling to the same site
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc

    visited_urls = set()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = executor.submit(scrape_page, url, base_domain, visited_urls, max_depth, 1)
        try:
            person_list = future.result(timeout=600)  # Adjust timeout as needed
            return person_list
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise HTTPException(status_code=500, detail=str(e))
