import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://fashion-studio.dicoding.dev"


def scrape_page(url: str) -> BeautifulSoup:
    """Fetch and parse a single page."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching {url}: {e}")
        raise
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout fetching {url}: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching {url}: {e}")
        raise


def parse_products(soup: BeautifulSoup, timestamp: str) -> list[dict]:
    """Parse product cards from a BeautifulSoup object."""
    try:
        products = []
        cards = soup.find_all("div", class_="collection-card")

        if not cards:
            logger.warning("No product cards found on page.")
            return products

        for card in cards:
            try:
                title = card.find("h3", class_="product-title")
                title = title.text.strip() if title else None

                price = card.find("span", class_="price")
                price = price.text.strip() if price else None

                rating_tag = card.find("p", string=lambda s: s and "Rating:" in s)
                rating = rating_tag.text.strip() if rating_tag else None

                colors_tag = card.find("p", string=lambda s: s and "Colors" in s)
                colors = colors_tag.text.strip() if colors_tag else None

                size_tag = card.find("p", string=lambda s: s and "Size:" in s)
                size = size_tag.text.strip() if size_tag else None

                gender_tag = card.find("p", string=lambda s: s and "Gender:" in s)
                gender = gender_tag.text.strip() if gender_tag else None

                products.append({
                    "Title": title,
                    "Price": price,
                    "Rating": rating,
                    "Colors": colors,
                    "Size": size,
                    "Gender": gender,
                    "timestamp": timestamp,
                })
            except Exception as e:
                logger.warning(f"Error parsing a product card: {e}")
                continue

        return products
    except Exception as e:
        logger.error(f"Error parsing products: {e}")
        raise


def scrape_main(base_url: str = BASE_URL, total_pages: int = 50) -> list[dict]:
    """Scrape all pages of the fashion studio website."""
    try:
        all_products = []
        timestamp = datetime.now().isoformat()
        logger.info(f"Starting scrape of {total_pages} pages from {base_url}")

        for page in range(1, total_pages + 1):
            url = base_url if page == 1 else f"{base_url}/page{page}"
            logger.info(f"Scraping page {page}: {url}")
            try:
                soup = scrape_page(url)
                products = parse_products(soup, timestamp)
                all_products.extend(products)
                logger.info(f"Page {page}: found {len(products)} products (total: {len(all_products)})")
                time.sleep(0.3)
            except Exception as e:
                logger.warning(f"Skipping page {page} due to error: {e}")
                continue

        logger.info(f"Scraping complete. Total products extracted: {len(all_products)}")
        return all_products
    except Exception as e:
        logger.error(f"Critical error in scrape_main: {e}")
        raise
