import asyncio
import re
from typing import Any, Dict
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse
from crawl4ai import CrawlerRunConfig, CacheMode, CrawlResult
from .base_parser import BaseParser

# Questo parser si riferisce al dominio: https://en.wikipedia.org

class WikipediaParser(BaseParser):

    def __init__(self) -> None:

        super().__init__("wikipedia.org")



    def create_crawler_config(self) -> CrawlerRunConfig:

        return CrawlerRunConfig(

            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript'],

            # Manteniamo SOLO infobox e roba chiaramente non informativa

            excluded_selector=".infobox, .metadata, .vevent, .toc, .vertical-navbox, .hatnote, .mw-editsection, .sidebar, .ambox",

            word_count_threshold=3,  # meno aggressivo (preserva tabelle)

            cache_mode=CacheMode.BYPASS,

            exclude_external_images=True

        )

   

    def extract_title(self, result: CrawlResult) -> str:

        """Estraggo il titolo della pagina da Wikipedia"""

        if not result.html:

            return "N/A"

        soup = BeautifulSoup(result.html, "html.parser")

        # Wikipedia usa <h1 id="firstHeading">

        h1 = soup.find("h1", {"id": "firstHeading"})

        if h1:

            return h1.get_text(strip=True)

        return result.metadata.get("title", "N/A")



    def _tag_to_markdown(self, tag: Tag) -> str:

        """

        Chiama direttamente l'inline parser, la logica precedente

        veniva ignorata dal return finale.

        """

        return self._inline_to_markdown(tag)



    def _inline_to_markdown(self, tag: Tag) -> str:

        """

        Percorre i figli DIRETTI di un tag e produce testo markdown

        preservando i link [testo](url).

        """

        parts = []

        for child in tag.children:

            if not isinstance(child, Tag):

                # Nodo testuale puro

                parts.append(str(child))

            elif child.name == "a":

                href = child.get("href", "")

                link_text = child.get_text(" ", strip=True)

                if link_text:

                    if href.startswith("/") and not href.startswith("//"):

                        href = f"https://en.wikipedia.org{href}"

                    elif href.startswith("//"):

                        href = f"https:{href}"

                    parts.append(f"[{link_text}]({href})" if href else link_text)

            else:

                # Ricorsione per tag annidati (span, b, i, ecc.)

                parts.append(self._inline_to_markdown(child))

        return "".join(parts).strip()



    def _table_to_markdown(self, table: Tag) -> str:

        """

        Converte una wikitable in una tabella markdown.

        Gestisce sia le celle di intestazione (th) che quelle dati (td).

        Restituisce una stringa vuota se la tabella non ha righe valide.

        """

        rows_md: list[str] = []

        header_done = False



        for row in table.find_all("tr"):

            cells = row.find_all(["th", "td"])

            if not cells:

                continue



            # Testo di ogni cella con link preservati

            cell_texts = [self._inline_to_markdown(cell) for cell in cells]

            # Rimuove celle completamente vuote all'inizio/fine

            if not any(cell_texts):

                continue



            row_line = "| " + " | ".join(cell_texts) + " |"

            rows_md.append(row_line)



            # Inserisce il separatore dopo la prima riga (intestazione)

            if not header_done:

                separator = "| " + " | ".join(["---"] * len(cell_texts)) + " |"

                rows_md.append(separator)

                header_done = True



        return "\n".join(rows_md)



    def parse_markdown(self, result: CrawlResult) -> str:

      if not result.html:

        return ""



      soup = BeautifulSoup(result.html, "html.parser")



      content = soup.find("div", {"id": "mw-content-text"})

      if not content:

        return ""



      # --- RIMOZIONE ELEMENTI NON INFORMATIVI ---

      # AGGIUNTA FONDAMENTALE: .reference (note) e .noprint (citation needed, update, ecc.)

      for el in content.select(

            ".navbox, .vertical-navbox, .sidebar, .infobox, .hatnote, .metadata, .toc, .reference, .noprint"

        ):

        el.decompose()



      for el in content.find_all(["figure", "img", "style", "script"]):

        el.decompose()

     

      # --- GESTIONE DEI BREAK LINEARI ---

      # Sostituiamo ogni <br> con un vero carattere di newline nel buffer di testo

      for br in content.find_all("br"):

          br.replace_with("\n")



      output = []



      # --- PARSING STRUTTURATO ---

      # Aggiunto "pre" alla lista dei tag da cercare

      for tag in content.find_all(["h2", "h3", "p", "ul", "ol", "table", "pre"], recursive=True):



        if tag.name in ("ul", "ol", "p", "pre") and tag.find_parent("table"):

          continue



        # TITOLI

        if tag.name == "h2":

          title = tag.get_text(strip=True)

          if title:

            output.append(f"\n## {title}\n")



        elif tag.name == "h3":

          title = tag.get_text(strip=True)

          if title:

            output.append(f"\n### {title}\n")



        # PARAGRAFI

        elif tag.name == "p":

          text = self._inline_to_markdown(tag)

          if text:

            output.append(text + "\n")



        # LISTE

        elif tag.name in ("ul", "ol"):

          for li in tag.find_all("li", recursive=False):

            li_text = self._inline_to_markdown(li)

            if li_text:

              output.append(f"- {li_text}")



        # TABELLE

        elif tag.name == "table":

          if tag.find_parent("table"):

            continue

          table_md = self._table_to_markdown(tag)

          if table_md:

            output.append("\n" + table_md + "\n")

                   

        # CODICE (Gestione dei blocchi <pre>)

        elif tag.name == "pre":

          code_text = tag.get_text()

          if code_text:

            # Lo avvolge nei backtick tripli tipici del Markdown

            output.append(f"\n```\n{code_text.strip()}\n```\n")



      text = "\n".join(output)



      # --- CLEANUP (ORA MOLTO PIÙ SNELLO) ---

      # Le regex per citation needed e note non servono più!

       

      # Rimuove il template "v t e" (che sopravvive a volte sotto le tabelle)

      text = re.sub(r'\bv\s*t\s*e\b', '', text)



      # Tronca alle sezioni non informative

      text = re.split(

        r'(?im)^##\s*(References|External links|See also|Further reading)',

        text

      )[0]



      return text.strip()

       

    def format_result(self, url: str, result: CrawlResult) -> Dict[str, Any]:

        """Formats the final result. Can be overridden by subclasses."""

        return {

            "url": url,

            "domain": self.domain,

            "title": self.extract_title(result),

            "html_text": result.html,                       # Commento classroom del prof: "Il campo html_text deve contenere result.html restituito da Crawl4Ai"

            "parsed_text": self.parse_markdown(result)

        }



#per testare se il parsing restituisce i campi corretti:

if __name__ == "__main__":

    url = input("Inserisci l'URL della pagina di wikipedia.org: ")

    parser = WikipediaParser()

    result = asyncio.run(parser.run(url))

    print("--- JSON OUTPUT ---")

    print(result)

   

    # Salvataggio su file .md

    filename = f"{result['title'].replace(' ', '_')}.md"

    with open(filename, "w", encoding="utf-8") as f:

        f.write(result["parsed_text"])

    print(f"--- Salvato in: {filename} ---")









r"""

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