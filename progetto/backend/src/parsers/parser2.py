import asyncio
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from .base_parser import BaseParser

# Questo parser si riferisce al dominio: https://www.statmuse.com

class StatMuseParser(BaseParser):
    def __init__(self):
        super().__init__("statmuse.com")

    def create_crawler_config(self):
        return CrawlerRunConfig(
            excluded_tags=['nav', 'footer', 'header', 'aside'],
            word_count_threshold=10,
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True
        )

 