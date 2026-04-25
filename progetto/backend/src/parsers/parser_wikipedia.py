import asyncio
from pydoc import text
import re
from typing import Dict, Any
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from .base_parser import BaseParser
#from base_parser import BaseParser

import markdown2
#TODO: sbaglia i titoli, non riesce a estrarre quelli corretti, forse perche sono in un tag particolare da capire meglio

# Parser per Wikipedia: https://en.wikipedia.org
class WikipediaParser(BaseParser):
    """Parser specializzato per articoli Wikipedia con pulizia markdown avanzata."""

    def __init__(self):
        super().__init__("en.wikipedia.org")

    def create_crawler_config(self) -> CrawlerRunConfig:
        """Configurazione del crawler per Wikipedia.
        
        Esclude:
        - Elementi di navigazione (nav, header, footer, aside)
        - Elementi di scripting (script, style)
        - Elementi di tabelle e info box
        - Elementi minori (span, abbr, sub)
        """
        '''css_selector='.mw-content-ltr.mw-parser-output , .IPA.nopopups.noexcerpt',
            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'infobox', 'toc', 'span', 'abbr', 'sub', 'figure', 'figcaption'],
            excluded_selector='.hatnote.navigation-not-searchable, .noprint, .mw-references-wrap, .citation, .external.text, .side-box-flex, #References, #Bibliography, #External_links, .mw-file-description',
            word_count_threshold=0,
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True,
            remove_forms=True,
            remove_consent_popups=True,
            exclude_all_images=True,
            exclude_external_links=True'''
        return CrawlerRunConfig(
            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript', 'figure', 'img'],
            # AGGIUNTI .gallery e .thumb per eliminare le gallerie e le miniature (con le loro didascalie)
            excluded_selector=".infobox, .metadata, .vevent, .toc, .vertical-navbox, .hatnote, .mw-editsection, .sidebar, .ambox, .navbox, .shortdescription, .gallery, .thumb",
            word_count_threshold=0, 
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True
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
        
        # Estrai il markdown dall'oggetto CrawlResult (approccio intermedio e sicuro)
        if hasattr(result, 'markdown_v2') and result.markdown_v2:
            text = result.markdown_v2.raw_markdown
        elif hasattr(result, 'markdown') and result.markdown:
            text = str(result.markdown)
        else:
            return ""

        if not text:
            return ""

        # 0. RIMUOVE CONTENUTO DA TAG INDESIDERATI (figcaption, caption, ecc.)
        # Estrai dal cleaned_html il contenuto di tag che non vuoi nel markdown
        html = self.parse_html(result)
        #if html:
            # Cerca contenuto da <figcaption>, <caption>, <aside> nel HTML
        #    text = self.extract_unwanted_content(html, ['figcaption'], text) #, 'caption', 'aside', 'figure'
            
        # 1. Rimuove "Jump to content" e intestazioni standard
        text = re.sub(r'\[Jump to content\]\([^)]*\)', '', text)
        text = re.sub(r'From Wikipedia, the free encyclopedia', '', text)
        text = re.sub(r'^#bodyContent\)?\s*', '', text)

        # 2. Rimuove le icone vuote e i link ai file immagine rimasti
        text = re.sub(r'(?m)^\[\]\((?:https://en\.wikipedia\.org)?/wiki/(?:Wikipedia:|File:)[^)]+\)\n*', '', text)
        # E per sicurezza, rimuove anche quelli inline (non all'inizio della riga)
        text = re.sub(r'\[\]\((?:https://en\.wikipedia\.org)?/wiki/(?:Wikipedia:|File:)[^)]+\)', '', text)

        # 3. Rimuove riferimenti a note: [1], [2], [a], [citation needed], ecc.
        text = re.sub(r'\s*\[(?:\[?\d+\]?|[a-zA-Z]?|)\]\([^\[\]\n]*?cite_note[^\[\]\n]*?\)', '', text)

    

        # 4. Rimuove note testuali isolate
        text = re.sub(r'\s*\[(?:\d+|[a-zA-Z])\]', '', text)

        # 5. Rimuove tag di avviso [_[citation needed](...)_]
        text = re.sub(r'\s*\[_\[[^\]]*\]\([^\[\]\n]*\)_\]', '', text)

        # 6. Corregge punti/virgole incollati ai link
        text = re.sub(r'\.\[', '. [', text)
        text = re.sub(r',\[', ', [', text)

        # 6.1 
        text = re.sub(r'\|', '', text)

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
            #"html_cleaned": result.cleaned_html,## canc
            "parsed_text": self.parse_markdown(result),
            #"parsed_text_markdown_grezzo": result.markdown, ##canc
        }
 

if __name__ == "__main__":
    """Test script per verificare il parser Wikipedia."""
    #url = input("Inserisci l'URL della pagina Wikipedia: ")
    url="https://en.wikipedia.org/wiki/List_of_largest_empires"
    parser = WikipediaParser()
    result = asyncio.run(parser.run(url))

  #PULISCE FACENDOLO DIVETARE UN SEMPLICE TESTO PULITO SENZA MARKDOWN O HTML
    html_text = BaseParser.remove_markdown(result.get('parsed_text'))
    # Rimuove i tag HTML
    print("=============testo dopo la conversione markdown->html:===============\n", html_text[:2000])  
    plain_text = re.sub(r'<[^>]+>', '', html_text)
    



    print("\n--- RESULT ---")
    print(f"Title: {result.get('title')}")
    print(f"Domain: {result.get('domain')}")
    #print(f"\n--- HTML TEXT (pulito)-------------------------")
    #print(result.get('html_cleaned'))
    #print(f"\n--- PARSED TEXT grezzo--------------------------------")
    #print(result.get('parsed_text_markdown_grezzo'))
   
    print(f"\n--- PLAIN TEXT---")
    print(plain_text)