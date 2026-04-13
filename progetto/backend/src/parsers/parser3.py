import asyncio
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from base_parser import BaseParser

# Questo parser si riferisce al dominio: https://eur-lex.europa.eu

class EurLexParser(BaseParser):
    def __init__(self):
        super().__init__("eur-lex.europa.eu")

    def create_crawler_config(self):
        return CrawlerRunConfig(
            excluded_tags=['nav', 'footer', 'header', 'aside'],
            word_count_threshold=10,
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True
        )

#per testare se il parsing restituisce i campi corretti:
if __name__ == "__main__":
    url = input("Inserisci l'URL della pagina di eur-lex.europa.eu: ")
    parser = EurLexParser()
    result = asyncio.run(parser.run(url))
    print("--- JSON OUTPUT ---")
    print(result)