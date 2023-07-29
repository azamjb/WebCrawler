import logging
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import re
from collections import deque
import time

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, urls=[], max_urls_to_visit=None, max_depth=None, delay=1):
        self.visited_urls = set()
        self.urls_to_visit = deque([(url, 0) for url in urls])
        self.max_urls_to_visit = max_urls_to_visit
        self.max_depth = max_depth
        self.delay = delay


    def download_url(self, url): # Downloads the HTML content of a URL and returns it
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        return requests.get(url, headers=headers).text


    def get_linked_urls(self, url, html): # Extracts and yields all absolute linked URLs found in the HTML content of a URL
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            if path and (urlparse(path).scheme in ['http', 'https']):
                yield path


    def add_url_to_visit(self, url, current_depth): # Adds a URL to the list of URLs to visit if it hasn't been visited or queued for visiting
        if url and (url.startswith('http://') or url.startswith('https://')):
            if url not in self.visited_urls and url not in [url_depth[0] for url_depth in self.urls_to_visit]:
                self.urls_to_visit.append((url, current_depth))


    def process_html(self, url, html): # Processes the HTML content of a URL and prints movie titles found using a CSS selector
        soup = BeautifulSoup(html, 'html.parser')

        movie_titles = soup.select('.titleColumn a')
        if movie_titles:
            print(f"Movie titles found on {url}:")
            for title in movie_titles:
                print(title.get_text())
            print()
        else:
            print(f"No movie titles found on {url}\n")


    def crawl(self, url, current_depth): # Downloads the HTML content of a URL, processes it, and adds linked URLs to the list of URLs to visit
        html = self.download_url(url)
        self.process_html(url, html)

        if self.max_depth is None or current_depth < self.max_depth:
            for linked_url in self.get_linked_urls(url, html):
                self.add_url_to_visit(linked_url, current_depth + 1)


    def run(self): # Continues crawling until there are no more URLs to visit or the maximum number of URLs to visit is reached
        crawled_count = 0
        while self.urls_to_visit:
            url, current_depth = self.urls_to_visit.popleft()
            logging.info(f'Crawling: {url}')
            try:
                self.crawl(url, current_depth)
                crawled_count += 1
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.add(url)

            if self.max_urls_to_visit is not None and crawled_count >= self.max_urls_to_visit:
                break

            time.sleep(self.delay)


if __name__ == '__main__': # Initializes a Crawler instance with the starting URL, calls the run method to begin the crawling process
    Crawler(urls=['https://www.imdb.com/'], max_urls_to_visit=10, max_depth=2, delay=1).run()