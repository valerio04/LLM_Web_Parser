import asyncio
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import re
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
        """Extracts the markdown from the result (safe fallback)."""
        if hasattr(result, 'markdown_v2') and result.markdown_v2:
            return result.markdown_v2.raw_markdown
        elif hasattr(result, 'markdown') and result.markdown:
            return str(result.markdown)
        return ""

    def parse_html(self, result):
        """Extracts the HTML from the result."""
        return result.html

    def create_browser_config(self):
        """Creates and returns a BrowserConfig. Can be overridden by subclasses."""
        return BrowserConfig(
            headless=True,
            verbose=True
        )
    def extract_unwanted_content(self, html: str, tags: list, text: str) -> str:
        """Estrae il contenuto testuale dai tag indesiderati.
        
        Args:
            html: HTML da cui estrarre
            tags: Lista di tag da cercare (es: ['figcaption', 'figure', 'caption'])
        
        Returns:
            Lista di stringhe trovate nei tag specificati (senza i tag HTML)
        """
        unwanted_content = []
        
        for tag in tags:
            # Pattern regex per trovare <tag>...</tag>
            pattern = rf'<{tag}[^>]*>(.*?)</{tag}>'
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                # Rimuove tag HTML dal contenuto
                clean_text = re.sub(r'<[^>]+>', '', match).strip()
                if clean_text:
                    unwanted_content.append(clean_text)
        
        #rimuovi gli oggetti non volut dal testo markdown
        
        
        
        # Rimuovi il testo trovato dal markdown
        for content in unwanted_content:
            # Escapa i caratteri speciali per regex
            escaped_content = re.escape(content)
            text = re.sub(escaped_content, '', text, flags=re.IGNORECASE)
        return text

        

    def format_result(self, url, result):
        """Formats the final result. Can be overridden by subclasses."""
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": self.parse_html(result),
            "parsed_text": self.parse_markdown(result)
        }

    async def run(self, url):
        """Runs the crawler and parses the result."""
        self.validate_url(url)

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.crawler_config)
            return self.format_result(url, result)