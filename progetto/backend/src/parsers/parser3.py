import asyncio
import re
import html
from typing import Any, Dict
from crawl4ai import CrawlerRunConfig, CacheMode, CrawlResult
from .base_parser import BaseParser
from bs4 import BeautifulSoup
class EurLexParser(BaseParser):
    def __init__(self):
        super().__init__("eur-lex.europa.eu")
        
        # Pattern di pulizia
        self.re_gu_headers = re.compile(r'(?mi)^(?:L\s+\d+/\d+\s*$|C\s+\d+/\d+\s*$|[A-Z]{2}\s*$)')
        self.re_ui_noise = re.compile(r'(?mi)^\s*\[(?:Top|Inizio pagina|.*?\*)\](?:\(.*?\))?\s*$')
        self.re_banners = re.compile(r'(?mi)^.*(?:cookies|official website of the European Union|sito ufficiale dell\'Unione).*$')
        self.re_ieni_nav = re.compile(r'(?ms)\n?(?:Below,\s+you\s+will\s+find|Qui\s+di\s+seguito\s+sono\s+disponibili):.*$')
        self.re_img = re.compile(r'!\[[^\]]*\]\([^)]*\)')
        self.re_start_noise = re.compile(r'(?s)^EUR-Lex\s*-\s*.*?\n.*?\n')
        self.re_barre = re.compile(r'\|') 
        
    def create_crawler_config(self) -> CrawlerRunConfig:
        return CrawlerRunConfig(
            simulate_user=True,           # Simula comportamento umano
            override_navigator=True,      # Bypassa bot-detection
            wait_for="css:#document1, .EurlexContent",

            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript', 'form', 'iframe'],
            # Pulizia mirata: rimuoviamo i componenti UI di EUR-Lex
            excluded_selector=(
                "button, .ecl-site-footer, .ecl-site-header__banner, .sidebar-offcanvas, "
                ".NavSearch, .EurlexSearch, .Sidebar, .SidebarTools, .wt-banner, "
                ".cookie-consent, #iubenda-cs-banner, .lseu-section-relevant-terms, "
                ".dropdown-menu, .LanguageSearch, p.cojnote"
            ),
            # Selettore specifico per il corpo del testo del glossario
            # #PP3Contents è il contenitore standard del testo istituzionale
            css_selector="#PP3Contents, .EurlexContent", 
            word_count_threshold=10,
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True,
            # Importante per Crawl4AI: prova a usare 'fit_markdown' per evitare ripetizioni
            process_iframes=False,
            remove_overlay_elements=True,
            page_timeout=60000, 
            delay_before_return_html=2.0
        )
    
    def extract_title(self, result: CrawlResult) -> str:
        # Helper per pulire la formattazione
        def clean_title(text: str) -> str:
            if not text:
                return ""
            return re.sub(r'\s+', ' ', text).replace(" - EUR-Lex", "").strip()

        title = ""

        # 1. TENTATIVO 1: Metadati (Il tuo metodo originale che funziona quasi sempre)
        if result.metadata and result.metadata.get("title"):
            title = result.metadata.get("title", "")
        elif result.html:
            soup = BeautifulSoup(result.html, 'html.parser')
            if soup.title and soup.title.string:
                title = soup.title.string

        title = clean_title(title)

        # 2. CONTROLLO TRAPPOLA: È un VERO titolo o solo il codice CELEX?
        # Le stringhe fittizie di EUR-Lex sono fatte così: "EUR-Lex - 52026PC0130 - IT" o solo "52026PC0130"
        # Usiamo una regex rigorosa per capire se la stringa è composta solo dal CELEX e dalla lingua.
        is_fake_title = bool(re.match(r'^(?:EUR-Lex\s*-\s*)?[0-9][A-Z0-9]{8,12}(?:\s*-\s*[A-Za-z]{2})?$', title))

        # Se il titolo è buono, lo restituiamo subito (così salviamo tutti gli altri documenti!)
        if title and not is_fake_title and title != "EUR_Lex_Senza_Titolo":
            return title

        # 3. TENTATIVO 2 (FALLBACK): Scansione del DOM (Per documenti come 52026PC0130)
        # Arriviamo qui SOLO se il metadato era vuoto o se era un falso titolo CELEX
        if result.html:
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Cerchiamo le classi specifiche che EUR-Lex usa per i titoli
            title_element = soup.select_one('.Titreobjet_cp, .Titreobjet_sg, .doc-ti, .oj-doc-ti, p.title, .doc-title')
            
            if title_element:
                extracted = clean_title(title_element.get_text(separator=' '))
                if extracted:
                    return extracted
            
            # Ultima spiaggia assoluta: il primo H1
            if soup.h1:
                h1_text = clean_title(soup.h1.get_text(separator=' '))
                if h1_text:
                    return h1_text

        # Se proprio fallisce tutto, restituisce il fake title o la stringa di default
        return title if title else "EUR_Lex_Senza_Titolo"
    
    def _deduplicate(self, text: str) -> str:
        paragraphs = re.split(r'\n{2,}', text)
        clean_paras = []
        seen = set()

        for p in paragraphs:
            norm = " ".join(p.lower().split())
            if norm and norm not in seen:
                clean_paras.append(p)
                seen.add(norm)
                if len(seen) > 10: 
                    seen.clear() 

        return '\n\n'.join(clean_paras)

    def parse_markdown(self, result: CrawlResult) -> str:
        if hasattr(result, 'markdown_v2') and result.markdown_v2:
            text = result.markdown_v2.raw_markdown
        else:
            text = result.markdown or ""
            
        if not text: 
            return ""
        
        text = self.re_gu_headers.sub('', text)
        text = self.re_ui_noise.sub('', text)
        text = self.re_banners.sub('', text)
        text = self.re_img.sub('', text)
        text = self.re_start_noise.sub('', text)
        text = self.re_ieni_nav.sub('', text)
        text = self.re_barre.sub(' ', text) 

        
        text = self._deduplicate(text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()
        
    def format_result(self, url: str, result: CrawlResult) -> Dict[str, Any]:
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": result.html or "",
            "parsed_text": self.parse_markdown(result)
        }

if __name__ == "__main__":
    async def main():
        url = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A12016M%2FTXT" # Esempio
        url = "https://eur-lex.europa.eu/content/news/index.html?locale=it"
        url = "https://eur-lex.europa.eu/IT/legal-content/glossary/nato-north-atlantic-treaty-organisation.html"
        parser = EurLexParser()
        result = await parser.run(url)
        
        print("\n--- RISULTATO PARSING IL POST ---")
        print(f"Titolo: {result['title']}")

        html_text = BaseParser.remove_markdown(result.get('parsed_text'))
        print(f"Testo Parsato (primi 500 car.):\n{html_text[:10000]}...")

    asyncio.run(main())