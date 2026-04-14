import asyncio
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# Cose da modificare in ogni parser specifico:

# 1. create_crawler_config()
#    - excluded_tags: adatta ai tag HTML del sito (nav, footer, aside, ecc.) (non home page ma pagine interne)
#    - word_count_threshold: alza/abbassa per filtrare testo non rilevante
#    - cache_mode: BYPASS per no-cache, ENABLED per usare cache

# 2. create_browser_config() (OPZIONALE)
#    - timeout: se il sito è lento
#    - user_agent: se il sito richiede uno specifico
#    - headless: sempre True se possibile

# 3. extract_title() (OPZIONALE)
#    - Se il titolo non è nei metadati standard
#    - Se serve estrarlo da un selettore CSS particolare

# 4. parse_markdown() / parse_html() (OPZIONALE)
#    - Se il contenuto deve essere processato in modo speciale
#    - Es: rimuovere sezioni, formattare diversamente, ecc.

class BaseParser:
    def __init__(self, domain):
        self.domain = domain
        self.crawler_config = self.create_crawler_config()
        self.browser_config = self.create_browser_config()

    def create_crawler_config(self):
        """Creates and returns a CrawlerRunConfig. To be customized by subclasses."""
        raise NotImplementedError("Subclasses must implement this method")

    def validate_url(self, url):
        """Validates if the URL belongs to the expected domain."""
        parsed_url = urlparse(url)
        if self.domain not in parsed_url.netloc:
            raise ValueError(f"URL does not belong to the domain {self.domain}")

    def extract_title(self, result):
        """Extracts the title from the result."""
        return result.metadata.get("title", "N/A") if result.metadata else "N/A"

    def parse_markdown(self, result):
        """Extracts the markdown from the result."""
        return result.markdown

    def parse_html(self, result):
        """Extracts the HTML from the result."""
        return result.html

    def create_browser_config(self):
        """Creates and returns a BrowserConfig. Can be overridden by subclasses."""
        return BrowserConfig(
            headless=True,
            verbose=True
        )

    def format_result(self, url, result):
        """Formats the final result. Can be overridden by subclasses."""
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": self.parse_html(result),
            "cleaned_html": self.parse_html(result),  # Può essere diverso se parse_html è personalizzato
            "parsed_text": self.parse_markdown(result)
        }

    async def run(self, url):
        """Runs the crawler and parses the result."""
        self.validate_url(url)

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.crawler_config)
            return self.format_result(url, result)