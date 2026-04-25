import asyncio
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import mistune
import re
from bs4 import BeautifulSoup

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
        """Crea e ritorna un CrawlerRunConfig. Deve essere configurata nelle sottoclassi."""
        raise NotImplementedError("Le sottoclassi devono implementare questo metodo")

    def validate_url(self, url):
        """Verifica se l'URL appartiene al dominio atteso."""
        parsed_url = urlparse(url)
        if self.domain not in parsed_url.netloc:
            raise ValueError(f"URL non appartiene al dominio {self.domain}")

    def extract_title(self, result):
        """Estrae il titolo dal risultato."""
        return result.metadata.get("title", "N/A") if result.metadata else "N/A"

    def parse_markdown(self, result):
        """Estrae il markdown dal risultato (safe fallback)."""
        if hasattr(result, 'markdown_v2') and result.markdown_v2:
            return result.markdown_v2.raw_markdown
        elif hasattr(result, 'markdown') and result.markdown:
            return str(result.markdown)
        return ""

    def parse_html(self, result):
        """Estrae l'HTML dal risultato."""
        return result.html

    def create_browser_config(self):
        """Creates and returns a BrowserConfig. Can be overridden by subclasses."""
        return BrowserConfig(
            headless=True,
            verbose=True
        )
    
    '''
    def remove_markdownn(md: str) -> str:
        """
        Rimuove il Markdown da una stringa, restituendo solo il testo pulito.
        Usa la libreria mistune per convertire il Markdown in HTML, poi BeautifulSoup per estrarre solo il testo.
        """
        html = mistune.html(md)
        soup = BeautifulSoup(html, "html.parser")
        # rimuove i tag lasciando il testo esattamente in-place (nessun separatore aggiunto, mantiene punteggiatura)
        for tag in soup.find_all(True):
            tag.unwrap()
        text = re.sub(r'[ \t]+', ' ', str(soup)) # collassa spazi orizzontali (non \n)
        text = re.sub(r'\n+', '\n', text) # collassa nuove linee multiple in una sola
        return text.strip()
    '''
    def remove_markdown(md: str) -> str:
        """Rimuove ogni traccia di formattazione per il confronto metrico."""
        html = mistune.html(md)
        soup = BeautifulSoup(html, "html.parser")
        # Rimuove i tag ma mantiene il contenuto
        text = soup.get_text(separator=' ') 
        # Normalizza spazi e newline
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def format_result(self, url, result):
        """Formatta il risultato finale. CPuò essere sovrascritto dalle sottoclassi."""
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": self.parse_html(result),
            "parsed_text": self.parse_markdown(result)
        }

    async def run(self, url):
        """Esegue il crawler e parsa il risultato."""
        self.validate_url(url)

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.crawler_config)
            return self.format_result(url, result)
    
    async def run_from_html(self, url, html):
        """Esegue il crawler sull'HTML fornito e parsa il risultato."""
        self.validate_url(url)

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=f"raw:{html}", config=self.crawler_config)
            return self.format_result(url, result)  