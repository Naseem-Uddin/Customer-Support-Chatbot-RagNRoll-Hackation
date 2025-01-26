# Created by Naseem Uddin
# This parse.py file is a simple web crawler and site parser in Python. I just needed it to create a table of data that I could then upload into Snowflake for data embedding and retrieval. For more information refer to this link: https://snowflake-mistral-rag.devpost.com/


import csv
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from collections import deque
import os


def fetch_html(url):
    """Fetch the HTML content of a URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_page_to_csv(url, csv_writer):
    """Parse a single page and write content to CSV."""
    html = fetch_html(url)
    if not html:
        return

    soup = BeautifulSoup(html, 'lxml')
    processed_texts = set()  # To track already processed text

    # Extract content based on headings
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        heading_text = heading.get_text(strip=True)
        sibling = heading.find_next_sibling()
        
        # Collect paragraphs under the heading
        while sibling and sibling.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if sibling.name == 'p':
                text = sibling.get_text(strip=True)
                if text and text not in processed_texts:
                    csv_writer.writerow([url, heading_text, text])
                    processed_texts.add(text)
            sibling = sibling.find_next_sibling()

    # Fallback: Add all unprocessed paragraphs without headings
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text and text not in processed_texts:
            csv_writer.writerow([url, "No Specific Heading", text])
            processed_texts.add(text)

def crawl_website(base_url, output_file, max_pages=50):
    """Crawl the website and parse all pages, saving content to a CSV."""
    visited = set()
    to_visit = deque([base_url])

    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write CSV header
        csv_writer.writerow(["URL", "Header", "Paragraph"])

        while to_visit and len(visited) < max_pages:
            current_url = to_visit.popleft()
            if current_url in visited:
                continue

            print(f"Visiting: {current_url}")
            visited.add(current_url)

            # Parse the current page and write to CSV
            parse_page_to_csv(current_url, csv_writer)

            # Fetch and parse the HTML to find new links
            html = fetch_html(current_url)
            if html:
                soup = BeautifulSoup(html, 'lxml')
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    full_url = urljoin(base_url, href)
                    
                    # Ensure the link is within the same domain
                    if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in visited:
                        to_visit.append(full_url)

# Example usage
start_url = "https://www.nbcuniversal.com/"
output_file = "parsed_content.csv"

crawl_website(start_url, output_file, max_pages=50)
print(f"Content saved to {output_file}")
