import asyncio
import re
import html
from typing import Dict, Any
from pathlib import Path

from crawl4ai import CrawlerRunConfig, CacheMode, CrawlResult
from .base_parser import BaseParser

class IlPostParser(BaseParser):
    """Parser specializzato per ilpost.it con pulizia markdown avanzata."""

    def __init__(self) -> None:
        super().__init__("ilpost.it")
        
        # --- PRE-COMPILAZIONE REGEX ---
        # 1. H1 Iniziale
        self.re_h1_start = re.compile(r'^#\s+.*$', re.MULTILINE)
        
        # 2. Sezioni inutili
        self.re_footer_cut = re.compile(r'(?im)^(?:Tag:|Mostra i commenti|### Consigliati|## \[|\*\*\*|_Disclaimer:|\*\*Vuoi iniziare subito)')
        
        # 3. Boilerplate, Social e Dirette
        self.re_social_noise = re.compile(r'(?mi)^[\s\*]*\[?(Condividi|Facebook|X \(Twitter\)|Email|Whatsapp|Regala il Post|Ascolta l\'articolo|Questo articolo ha più|Ci sono nuovi aggiornamenti).*$')
        
        # 4. Link Editoriali (Leggi anche)
        self.re_leggi_anche = re.compile(r'(?mi)^.*\*\*\s*(?:[-–]\s*)?Leggi anche:?\*\*.*$|^.*\[(?:[-–]\s*)?Leggi anche:?\].*$')
        
        # 5. Inviti all'abbonamento
        self.re_abbonamento = re.compile(r'(?mi)^.*Se vuoi sostenere il Post.*$|^.*Abbonati a il Post.*$')

        # 6. Minutaggio player audio
        self.re_audio_time = re.compile(r'(?mi)^\s*(?:\d{1,2}:)?\d{1,2}:\d{2}\s*$')
        
        # 7. DIDASCALIE FOTO: Intercetta righe che finiscono con "(.../Getty Images)" ecc.
        self.re_captions = re.compile(r'(?mi)^.*\([^)]*(?:Getty Images|AP Photo|ANSA|Reuters|EPA|Lapresse|LaPresse|Fotogramma|Tim de Waele|Luc Claessen)[^)]*\)\s*$')

    def create_crawler_config(self) -> CrawlerRunConfig:
        """Configurazione del crawler per Il Post."""
        return CrawlerRunConfig(
            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript', 'figure', 'img', 'iframe', 'form'],
            excluded_selector=(
                ".cookie-banner, #iubenda-cs-banner, .share, .social, .social-share, "
                ".newsletter, .banner, .adv, .ad-container, #pp-paywall, .tags, "
                ".author-box, .related-posts, .caption, figcaption"
            ),
            word_count_threshold=0, 
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True
        )
    
    def extract_title(self, result: CrawlResult) -> str:
        """Estrae il titolo cercando il tag h1 nell'HTML o nei metadati."""
        if not result.html:
            return "N/A"
            
        match = re.search(r'<h1[^>]*>(.*?)</h1>', result.html, re.IGNORECASE | re.DOTALL)
        if match:
            clean_title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            clean_title = html.unescape(clean_title) 
            if clean_title:
                return clean_title
                
        return result.metadata.get("title", "N/A")

    def parse_html(self, result: CrawlResult) -> str:
        """Restituisce l'HTML grezzo estratto."""
        return result.html if result.html else ""

    def parse_markdown(self, result: CrawlResult) -> str:
        """Pulisce il markdown rimuovendo rumore editoriale ma conservando la sintassi MD."""
        text = ""
        if hasattr(result, 'markdown_v2') and result.markdown_v2:
            text = result.markdown_v2.raw_markdown
        elif result.markdown:
            text = str(result.markdown)
            
        if not text:
            return ""

        # 1. Taglia tutto ciò che precede il titolo H1
        match_start = self.re_h1_start.search(text)
        if match_start:
            text = text[match_start.start():]
        
        # 2. Taglia commenti, tag e footer
        text = self.re_footer_cut.split(text)[0]
        
        # 3. RIMOZIONE RUMORE (Social, Leggi anche, Abbonamenti, Audio, Didascalie)
        text = self.re_social_noise.sub('', text)
        text = self.re_leggi_anche.sub('', text)
        text = self.re_abbonamento.sub('', text)
        text = self.re_audio_time.sub('', text)
        text = self.re_captions.sub('', text) # <--- Taglio didascalie!
        
        # 4. NORMALIZZAZIONE SPAZI (Senza intaccare i marcatori Markdown)
        text = '\n'.join([line.strip() for line in text.split('\n')])
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()
        
    def format_result(self, url: str, result: CrawlResult) -> Dict[str, Any]:
        """Formatta il risultato finale."""
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": self.parse_html(result),
            "parsed_text": self.parse_markdown(result)
        }

if __name__ == "__main__":
    async def main():
        url = "https://www.ilpost.it/2023/05/02/le-nuove-regole-del-post/"
        parser = IlPostParser()
        result = await parser.run(url)
        
        print("\n--- RISULTATO PARSING IL POST ---")
        print(f"Titolo: {result['title']}")
        print(f"Testo Parsato (primi 500 car.):\n{result['parsed_text'][:500]}...")

    asyncio.run(main())