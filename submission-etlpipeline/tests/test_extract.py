import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.extract import scrape_page, parse_products, scrape_main


SAMPLE_HTML = """
<html><body>
  <div class="collection-card">
    <h3 class="product-title">Cool T-Shirt</h3>
    <span class="price">$29.99</span>
    <p>Rating: 4.5 / 5</p>
    <p>3 Colors</p>
    <p>Size: M</p>
    <p>Gender: Men</p>
  </div>
  <div class="collection-card">
    <h3 class="product-title">Summer Pants</h3>
    <span class="price">$49.99</span>
    <p>Rating: 4.0 / 5</p>
    <p>2 Colors</p>
    <p>Size: L</p>
    <p>Gender: Women</p>
  </div>
</body></html>
"""

EMPTY_HTML = "<html><body></body></html>"


class TestScrapePage:
    @patch("utils.extract.requests.get")
    def test_scrape_page_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_HTML
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        soup = scrape_page("https://example.com")
        assert soup is not None
        assert isinstance(soup, BeautifulSoup)

    @patch("utils.extract.requests.get")
    def test_scrape_page_http_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.HTTPError("404 Not Found")
        with pytest.raises(req.exceptions.HTTPError):
            scrape_page("https://example.com/bad")

    @patch("utils.extract.requests.get")
    def test_scrape_page_connection_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError("Connection refused")
        with pytest.raises(req.exceptions.ConnectionError):
            scrape_page("https://example.com")

    @patch("utils.extract.requests.get")
    def test_scrape_page_timeout(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.Timeout("Timed out")
        with pytest.raises(req.exceptions.Timeout):
            scrape_page("https://example.com")


class TestParseProducts:
    def test_parse_products_returns_list(self):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        products = parse_products(soup, "2024-01-01T00:00:00")
        assert isinstance(products, list)

    def test_parse_products_correct_count(self):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        products = parse_products(soup, "2024-01-01T00:00:00")
        assert len(products) == 2

    def test_parse_products_fields_present(self):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        products = parse_products(soup, "2024-01-01T00:00:00")
        required_keys = {"Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"}
        for product in products:
            assert required_keys.issubset(set(product.keys()))

    def test_parse_products_title_value(self):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        products = parse_products(soup, "2024-01-01T00:00:00")
        assert products[0]["Title"] == "Cool T-Shirt"

    def test_parse_products_price_value(self):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        products = parse_products(soup, "2024-01-01T00:00:00")
        assert products[0]["Price"] == "$29.99"

    def test_parse_products_timestamp(self):
        ts = "2024-06-01T10:00:00"
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        products = parse_products(soup, ts)
        for product in products:
            assert product["timestamp"] == ts

    def test_parse_products_empty_page(self):
        soup = BeautifulSoup(EMPTY_HTML, "html.parser")
        products = parse_products(soup, "2024-01-01T00:00:00")
        assert products == []


class TestScrapeMain:
    @patch("utils.extract.scrape_page")
    @patch("utils.extract.time.sleep")
    def test_scrape_main_returns_list(self, mock_sleep, mock_scrape_page):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        mock_scrape_page.return_value = soup
        result = scrape_main(total_pages=2)
        assert isinstance(result, list)

    @patch("utils.extract.scrape_page")
    @patch("utils.extract.time.sleep")
    def test_scrape_main_correct_count(self, mock_sleep, mock_scrape_page):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        mock_scrape_page.return_value = soup
        result = scrape_main(total_pages=3)
        # 2 products per page × 3 pages = 6
        assert len(result) == 6

    @patch("utils.extract.scrape_page")
    @patch("utils.extract.time.sleep")
    def test_scrape_main_skips_failed_pages(self, mock_sleep, mock_scrape_page):
        import requests as req
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        mock_scrape_page.side_effect = [soup, Exception("fail"), soup]
        result = scrape_main(total_pages=3)
        assert len(result) == 4  # 2 successful pages × 2 products

    @patch("utils.extract.scrape_page")
    @patch("utils.extract.time.sleep")
    def test_scrape_main_has_timestamp(self, mock_sleep, mock_scrape_page):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        mock_scrape_page.return_value = soup
        result = scrape_main(total_pages=1)
        for item in result:
            assert "timestamp" in item
            assert item["timestamp"] is not None
