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
        return CrawlerRunConfig(
            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript', 'svg'],
            cache_mode=CacheMode.BYPASS,
            # Esclude le immagini per evitare che gli 'alt' raddoppino i loghi
            exclude_external_images=True, 
        )
    
    def extract_title(self, result) -> str:
        """Estrae il titolo cercando il tag h1 nell'HTML o nei metadati."""
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
        
        # Eliminiamo SOLO gli svg che inquinano il testo con path interni.
        # Manteniamo i tag 'img' per poterne estrarre l'attributo 'alt' se necessario.
        for tag in soup.find_all(['svg']):
            tag.decompose()
                
        parts = []
        is_standings = "standings" in url.lower()
        is_finance = "money" in url.lower() or "price" in url.lower()
        
        h1 = soup.find('h1')
        if h1:
            parts.append(h1.get_text(separator=' ', strip=True))
            
        processed_tables = set()
        parsed_tables_text = set()
        
        for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'table']):
            
            if tag.name in ['h2', 'h3', 'h4', 'h5']:
                text = tag.get_text(separator=' ', strip=True)
                lower_text = text.lower()
                
                if "interpreted as:" in lower_text:
                    continue
                
                # --- GHIGLIOTTINA DEL RUMORE ---
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
                        
                        # FIX: Se la cella è testualmente vuota, prova a recuperare 
                        # il nome dall'attributo 'alt' della foto o dal 'title'
                        if not c_text:
                            img = cell.find('img')
                            if img and img.get('alt'):
                                c_text = img.get('alt').strip()
                            elif cell.get('title'):
                                c_text = cell.get('title').strip()
                        
                        # FIX PERFETTO: Iniezione dinamica di header e Total
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
                    # Deduplicatore che risolve le classifiche MLB duplicate per CSS responsive
                    if table_text not in parsed_tables_text:
                        parsed_tables_text.add(table_text)
                        parts.append(table_text)
                
        return '\n\n'.join(parts)

    def format_result(self, url: str, result) -> Dict[str, Any]:
        html_content = getattr(result, 'html', "")
        parsed_text = self._extract_text_with_bs4(html_content, url)
        
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": html_content,
            "parsed_text": parsed_text
        }
    
    #TODO: capire se si può cancellare.
    async def parse(self, url: str) -> Dict[str, Any]:
        try:
            self.validate_url(url)
            data = await self.run(url)
            data["success"] = True
            return data
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "domain": self.domain,
                "title": "Error",
                "html_text": "",
                "parsed_text": ""
            }


if __name__ == "__main__":
    async def main():
        parser = StatMuseParser()
        url = "https://www.statmuse.com/nba/ask/nba-ppg-leaders-this-season"
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        risultato = await parser.parse(url)
        
        if risultato.get("success"):
            print(f"Titolo: {risultato['title']}")
            print("\n--- CONTENUTO PULITO (primi 800 caratteri) ---")
            print(risultato["parsed_text"][:800] + "...")
        else:
            print(f"Errore: {risultato.get('error')}")

    asyncio.run(main())