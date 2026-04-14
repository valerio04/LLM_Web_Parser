import asyncio
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from .base_parser import BaseParser

# Questo parser si riferisce al dominio: https://en.wikipedia.org

class WikipediaParser(BaseParser):
    def __init__(self):
        super().__init__("wikipedia.org")

    def create_crawler_config(self):
        return CrawlerRunConfig(
            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'table', 'infobox', 'toc', 'span'],
            css_selector='.mw-content-ltr.mw-parser-output , .IPA.nopopups.noexcerpt',
            excluded_selector='.hatnote.navigation-not-searchable, .noprint, .mw-references-wrap.mw-references-columns, .citation, .external.text',
            word_count_threshold=0,
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True,
            remove_forms=True,
            remove_consent_popups=True,
            exclude_all_images=True,
            exclude_external_links=True
            
        )
    def format_result(self, url, result):
        """Formats the final result. Can be overridden by subclasses."""
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": self.parse_html(result),
            "parsed_text": self.parse_markdown(result)
        } 


#per testare se il parsing restituisce i campi corretti:
if __name__ == "__main__":
    url = input("Inserisci l'URL della pagina di wikipedia.org: ")
    parser = WikipediaParser()
    result = asyncio.run(parser.run(url))
    print("--- JSON OUTPUT ---")
    print(result['parsed_text'][:200])  


#1 html deve essere grezzo? questo restituisce gia il grezzo?
#2 oltre a quelle configuraziioni nel CrawlerRunConfig, quali altre personalizzazioni sono possibili? devo lavorare solo su parse_markdown?
# devo pulire il testo da markdown a testo normale primadi metterlo neel test evaluation?

"""
OPZIONI E STRUMENTI PER PARSING PERSONALIZZATO (da adattare a seconda del sito):

1. CrawlerRunConfig - Configurazione dell'estrazione
   - excluded_tags: Tag HTML da ignorare (nav, footer, header, aside, script, style)
     Es: excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style']
   
   - word_count_threshold: Min parole per blocco (5=dettagliato, 20=principale)
     Es: word_count_threshold=10  # Ignora blocchi con <10 parole
   
   - cache_mode: CacheMode.BYPASS (no cache), ENABLED (con cache)
     Es: cache_mode=CacheMode.BYPASS  # Sempre fresco
   
   - exclude_external_images: True per escludere immagini esterne
     Es: exclude_external_images=True

2. BrowserConfig - Configurazione del browser
   - headless: True per modalità invisibile (più veloce)
     Es: headless=True
   
   - verbose: True per log dettagliati (utile per debug)
     Es: verbose=True
   
   - timeout: Timeout in ms (es. 30000 = 30 sec)
     Es: timeout=30000  # Se il sito è lento
   
   - user_agent: User agent personalizzato se richiesto
     Es: user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

3. Metodi Personalizzabili:

   A. extract_title(result) - Estrarre titolo da metadati o tag specifici
      Default: result.metadata.get("title", "N/A")
      
      Personalizzato (esempio):
      def extract_title(self, result):
        # Default: result.metadata.get("title", "N/A")
        # Personalizzato: estrarre da tag CSS
        if result.html:
            import re
            match = re.search(r'<h1[^>]*>([^<]+)</h1>', result.html)
            return match.group(1) if match else "N/A"
        return "N/A"

   B. parse_html(result) - Rimuovere script, style, commenti
      Default: result.html
      
      Personalizzato (esempio):
      def parse_html(self, result):
          import re
          html = result.html
          html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
          html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
          return html

   C. parse_markdown(result) - Ripulire testo estratto
      Default: result.markdown
      
      Personalizzato (esempio):
      def parse_markdown(self, result):
          import re
          text = result.markdown
          # Rimuovere URL
          text = re.sub(r'https?://\S+', '', text)
          # Rimuovere email
          text = re.sub(r'\S+@\S+', '', text)
          # Normalizzare spazi
          text = ' '.join(text.split())
          return text

   
      
    

4. Post-processing con Regex (riusabili):
   
   # Rimuovere URL:
   text = re.sub(r'https?://\S+', '', text)
   
   # Rimuovere email:
   text = re.sub(r'\S+@\S+', '', text)
   
   # Rimuovere numeri di pagina [1] [2]:
   text = re.sub(r'\[\d+\]', '', text)
   
   # Normalizzare spazi (rimuovere multipli):
   text = ' '.join(text.split())
   
   # Rimuovere righe vuote:
   text = '\n'.join(line for line in text.split('\n') if line.strip())
   
   # Rimuovere parentesi tonde con contenuto (note Wikipedia):
   text = re.sub(r'\([^)]*\)', '', text)

5. Aspettare Caricamento Dinamico (per siti con JavaScript):
   
   # Aspettare elemento specifico:
   CrawlerRunConfig(
       wait_for_selector=".article-content",
       timeout=10000  # Max 10 secondi
   )
   
   # Eseguire codice JavaScript:
   CrawlerRunConfig(
       js_code=""
       await new Promise(r => setTimeout(r, 2000));  // Aspetta 2 sec
       window.scrollTo(0, document.body.scrollHeight);  // Scrolla
       ""
   )

FLUSSO CONSIGLIATO:
1. Testa parsing di base (senza personalizzazioni)
2. Regola excluded_tags e word_count_threshold
3. Se serve, personalizza parse_markdown() con regex
4. Se testo sporco, personalizza parse_html() prima
5. Se sito dinamico, aggiungi wait_for_selector o js_code
6. Aggiungi campi custom con format_result()
"""