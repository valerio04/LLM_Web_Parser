import asyncio
import json
import re
from urllib.parse import urlparse
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

from crawl4ai import CrawlerRunConfig, CacheMode
from .base_parser import BaseParser

class StatMuseParser(BaseParser):
    """
    Parser per www.statmuse.com.
    
    Strategia F1-Score Maximizer:
    - BeautifulSoup estrae sequenzialmente h1, h2, h3 e tabelle.
    - Generazione dati tab-separated per la massima compatibilità col Tokenizer dell'Evaluator.
    - Deduplicazione testuale per ignorare le tabelle Mobile/Desktop ripetute (es. MLB Standings).
    - Iniezione dinamica degli header vuoti (TEAM per classifiche, DATE per finanza, NAME per giocatori).
    """

    def __init__(self):
        super().__init__("www.statmuse.com")

    def create_crawler_config(self) -> CrawlerRunConfig:
        """
        Configurazione del crawler per Wikipedia.
        """
        return CrawlerRunConfig(
            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript', 'svg'],
            cache_mode=CacheMode.BYPASS,
            # Esclude le immagini per evitare che gli 'alt' raddoppino i loghi
            exclude_external_images=True,
            wait_for="js:() => document.querySelectorAll('div.text-inherit').length > 0",
            #delay_before_return_seconds=2.0 # Opzionale: un piccolo cuscinetto per il caricamento delle API
        )
    
    def extract_title(self, result) -> str:
        """
        Estrae il titolo cercando il tag h1 nell'HTML o nei metadati.
        """
        html_content = getattr(result, 'html', "")
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            h1 = soup.find('h1')
            if h1:
                return h1.get_text(separator=' ', strip=True)
        
        title = super().extract_title(result)
        if title and title != "N/A":
            return title.replace(" | StatMuse", "").strip()
        return "N/A"
    
    def _extract_text_with_bs4(self, html_content: str, url: str) -> str:
        if not html_content:
            return ""
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # --- 1. PULIZIA ESTREMA PREVENTIVA ---
        # Rimuoviamo menu, footer, script, svg
        for element in soup(["script", "style", "noscript", "meta", "header", "footer", "nav", "svg"]):
            element.decompose()
            
        # Rimuoviamo i banner dei cookie e div legali
        for banner in soup.select('[id*="cookie"], [id*="consent"], [class*="cookie"], [class*="consent"], [class*="privacy"]'):
            banner.decompose()
                
        parts = []
        
        lower_url = url.lower()
        is_standings = "standings" in lower_url
        is_finance = "money" in lower_url or "price" in lower_url
        is_scores = "scores" in lower_url
        
        h1 = soup.find('h1')
        if h1:
            parts.append(h1.get_text(separator=' ', strip=True))
            
        # --- 2. GESTIONE SPECIFICA: SCORES IN VERTICALE ---
        if is_scores:
            main_content = soup.find('main') or soup.find('body') or soup
            
            # Pulizia opzionale dei menu delle date (es. "Tue May 26", "Today", "All", ecc.)
            for nav_item in main_content.find_all(string=re.compile(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) [A-Z][a-z]{2} \d{1,2}$|^Yesterday$|^Today$|^Tomorrow$')):
                if nav_item.parent:
                    nav_item.parent.decompose()
                    
            # Estrazione con "\n" per ottenere il layout verticale desiderato
            testo_punteggi = main_content.get_text(separator='\n', strip=True)
            
            # Rimuoviamo l'h1 se è stato duplicato all'inizio
            if h1:
                h1_text = h1.get_text(separator=' ', strip=True)
                if testo_punteggi.startswith(h1_text):
                    testo_punteggi = testo_punteggi[len(h1_text):].strip()
            
            # Cerca tutti i blocchi delle partite (sostituisci con la classe CSS reale)
            games = main_content.find_all('div', class_=['flex','gap-3', 'py-2','px-3','text-inherit']) 

            for game in games:
                # Se troviamo il blocco del punteggio, la partita è finita
                score = game.find('div', class_=['w-max','flex','flex-col','justify-center','text-right','text-sm','text-gray-5'])
                if score:
                    # Altrimenti è futura, cerchiamo l'orario nell'attributo 'datetime'
                    time_tag = game.find(class_=['flex','flex-col','justify-center','items-end','text-nowrap','text-sm',])
                    if time_tag and time_tag.has_attr('datetime'):
                        print(f"Partita in programma. Orario UTC: {time_tag['datetime']}")
                else:
                    print("Partita conclusa.")
                        
            # Normalizziamo eventuali blocchi di righe vuote eccessive (es. 4-5 a capo di fila)
            testo_punteggi = re.sub(r'\n{3,}', '\n\n', testo_punteggi)
                    
            if testo_punteggi:
                parts.append(testo_punteggi)
                
            return '\n\n'.join(parts)
            
        processed_tables = set()
        parsed_tables_text = set()
        
        for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'table']):
            
            if tag.name in ['h2', 'h3', 'h4', 'h5']:
                text = tag.get_text(separator=' ', strip=True)
                lower_text = text.lower()
                
                if "interpreted as:" in lower_text:
                    continue
                
                is_noise = any(kw in lower_text for kw in [
                    "related searches", "trending", "statmuse app",
                    "team leaders", "team rankings", "fantasy", "betting",
                    "last game"
                ])
                
                if "more" in lower_text and "stats" in lower_text:
                    is_noise = True
                    
                if "standings" in lower_text and not is_standings:
                    is_noise = True
                
                if is_noise:
                    break 
                
                if text:
                    parts.append(text)
                    
            elif tag.name == 'table':
                if id(tag) in processed_tables: continue
                if any(p.name == 'table' for p in tag.parents): continue
                processed_tables.add(id(tag))
                
                rows = []
                trs = tag.find_all('tr')
                for tr_idx, tr in enumerate(trs):
                    is_last_row = (tr_idx == len(trs) - 1)
                    cells = []
                    for i, cell in enumerate(tr.find_all(['th', 'td'])):
                        c_text = cell.get_text(separator=' ', strip=True)
                        
                        # Se la cella è testualmente vuota, prova a recuperare 
                        # il nome dall'attributo 'alt' della foto o dal 'title'
                        if not c_text:
                            img = cell.find('img')
                            if img and img.get('alt'):
                                c_text = img.get('alt').strip()
                            elif cell.get('title'):
                                c_text = cell.get('title').strip()
                        
                        # Iniezione dinamica di header e Total
                        if not c_text:
                            if cell.name == 'th':
                                if i == 0:
                                    if is_standings: c_text = "TEAM"
                                    elif is_finance: c_text = "DATE"
                                elif i == 1 and not is_standings and not is_finance:
                                    c_text = "NAME"
                            elif cell.name == 'td':
                                if i == 0 and is_last_row:
                                    c_text = "Total"
                                    
                        cells.append(c_text)
                        
                    if any(c.strip() for c in cells): 
                        rows.append('\t'.join(cells))
                        
                if rows:
                    table_text = '\n'.join(rows)
                    if table_text not in parsed_tables_text:
                        parsed_tables_text.add(table_text)
                        parts.append(table_text)
                
        return '\n\n'.join(parts)

    def format_result(self, url: str, result) -> Dict[str, Any]:
        """
        Formatta il risultato finale del parsing.
        """
        html_content = getattr(result, 'html', "")
        parsed_text = self._extract_text_with_bs4(html_content, url)
        
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": html_content,
            "parsed_text": parsed_text
        }