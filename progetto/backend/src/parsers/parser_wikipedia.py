import asyncio
from pydoc import text
import re
from typing import Dict, Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from .base_parser import BaseParser
import markdown2

# Parser per Wikipedia: https://en.wikipedia.org
class WikipediaParser(BaseParser):
    """Parser specializzato per articoli Wikipedia con pulizia markdown avanzata."""

    def __init__(self):
        super().__init__("wikipedia.org")

    def create_crawler_config(self) -> CrawlerRunConfig:
        """Configurazione del crawler per Wikipedia.
        
        Esclude:
        - Elementi di navigazione (nav, header, footer, aside)
        - Elementi di scripting (script, style)
        - Elementi di tabelle e info box
        - Elementi minori (span, abbr, sub)
        """
        return CrawlerRunConfig(
            css_selector='.mw-content-ltr.mw-parser-output , .IPA.nopopups.noexcerpt',
            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'table', 'infobox', 'toc', 'span', 'abbr', 'sub'],
            excluded_selector='.hatnote.navigation-not-searchable, .noprint, .mw-references-wrap, .citation, .external.text, .side-box-flex, #References, #Bibliography, #External_links, .mw-file-description, .mw:File/Thumb',
            word_count_threshold=0,
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True,
            remove_forms=True,
            remove_consent_popups=True,
            exclude_all_images=True,
            exclude_external_links=True
        )

    def extract_title(self, result) -> str:
        """Estrae il titolo della pagina Wikipedia.
        
        Cerca il tag h1 con id "firstHeading", altrimenti usa i metadati.
        """
        if not hasattr(result, 'html') or not result.html:
            return "N/A"

        # Cerca il tag h1 con id "firstHeading"
        match = re.search(
            r'<h1[^>]*id=["\']firstHeading["\'][^>]*>(.*?)</h1>',
            result.html,
            re.IGNORECASE | re.DOTALL
        )
        if match:
            # Rimuove tag HTML interni
            clean_title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            if clean_title:
                return clean_title

        # Fallback dai metadati
        if hasattr(result, 'metadata') and result.metadata:
            return result.metadata.get("title", "N/A")
        return "N/A"

    def parse_html(self, result) -> str:
        """Estrae l'HTML grezzo della pagina."""
        if hasattr(result, 'html') and result.html:
            return result.html
        return ""

    def parse_markdown(self, result) -> str:
        """Converte il markdown estratto in testo pulito.
        
        Rimuove:
        - Icone e link di navigazione Wikipedia
        - Riferimenti e note ([1], [2], ecc.)
        - Sezioni finali non informative (References, External links, ecc.)
        - Spazi e newline eccessivi
        """
        text = ""
        
        # Estrai il markdown dall'oggetto CrawlResult
        if hasattr(result, 'markdown_v2') and result.markdown_v2:
            text = result.markdown_v2.raw_markdown if hasattr(result.markdown_v2, 'raw_markdown') else str(result.markdown_v2)
        elif hasattr(result, 'markdown') and result.markdown:
            text = result.markdown if isinstance(result.markdown, str) else str(result.markdown)
        else:
            return ""

        if not text:
            return ""

        # 1. Rimuove "Jump to content" e intestazioni standard
        text = re.sub(r'\[Jump to content\]\([^)]*\)', '', text)
        text = re.sub(r'From Wikipedia, the free encyclopedia', '', text)
        text = re.sub(r'^#bodyContent\)?\s*', '', text)

        # 2. Rimuove le icone vuote iniziali (Stella, lucchetto, audio)
        text = re.sub(r'(?m)^\[\]\(https://en\.wikipedia\.org/wiki/(?:Wikipedia:|File:).*?\)\n*', '', text)

        # 3. Rimuove riferimenti a note: [1], [2], [a], [citation needed], ecc.
        text = re.sub(r'\s*\[(?:\[?\d+\]?|[a-zA-Z]?|)\]\([^\[\]\n]*?cite_note[^\[\]\n]*?\)', '', text)

    

        # 4. Rimuove note testuali isolate
        text = re.sub(r'\s*\[(?:\d+|[a-zA-Z])\]', '', text)

        # 5. Rimuove tag di avviso [_[citation needed](...)_]
        text = re.sub(r'\s*\[_\[[^\]]*\]\([^\[\]\n]*\)_\]', '', text)

        # 6. Corregge punti/virgole incollati ai link
        text = re.sub(r'\.\[', '. [', text)
        text = re.sub(r',\[', ', [', text)

        # 7. Rimuove il template "v t e"
        text = re.sub(r'\bv\s*t\s*e\b', '', text)

        # 8. Tronca alle sezioni finali non informative
        text = re.split(
            r'(?im)^#{2,}\s*(References|External links|See also|Further reading|Notes)',
            text
        )[0]

        # 9. Normalizza newline eccessivi
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def format_result(self, url: str, result) -> Dict[str, Any]:
        """Formatta il risultato finale del parsing."""
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": self.parse_html(result),
            "parsed_text": self.parse_markdown(result)
        }


if __name__ == "__main__":
    """Test script per verificare il parser Wikipedia."""
    url = input("Inserisci l'URL della pagina Wikipedia: ")
    parser = WikipediaParser()
    result = asyncio.run(parser.run(url))


    html_text = markdown2.markdown(result.get('parsed_text'))
    # Rimuove i tag HTML
    print("=============testo dopo la conversione markdown->html:===============\n", html_text[:2000])  
    plain_text = re.sub(r'<[^>]+>', '', html_text)
    



    print("\n--- RESULT ---")
    print(f"Title: {result.get('title')}")
    print(f"Domain: {result.get('domain')}")
    print(f"\n--- PARSED TEXT ---")
    print(result.get('parsed_text'))
    print(plain_text)