import asyncio
import re
import json
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from .base_parser import BaseParser


@dataclass
class StatMuseTable:
    """Rappresenta una tabella di statistiche estratta dal markdown."""
    title: Optional[str] = None
    headers: List[str] = field(default_factory=list)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "headers": self.headers,
            "rows": self.rows,
            "row_count": len(self.rows)
        }


class StatMuseParser(BaseParser):
    """
    Parser per www.statmuse.com.
    
    Strategia di pulizia:
    1. Configurazione crawl4ai aggressiva per escludere elementi di rumore
    2. Post-processing del markdown per rimuovere sezioni collaterali
    3. Estrazione selettiva del contenuto principale (query result / player profile)
    
    Il contenuto rilevante su StatMuse è:
    - Per pagine /ask/: titolo query, risposta testuale, tabella dati principale
    - Per pagine /player/: summary giocatore, tabella stats
    - NON deve includere: nav, footer, sidebar, "More X Stats", standings, schedule, leaders, etc.
    """

    def __init__(self):
        super().__init__("statmuse.com")
        self.domain_patterns = {
            "ask": r"/(?:nba|nhl|mlb|nfl|fc|cfb|wnba)/ask/",
            "player": r"/(?:nba|nhl|mlb|nfl|fc|cfb|wnba)/player/",
            "home": r"^/$|^/(?:nba|nhl|mlb|nfl|fc|cfb|wnba)/?$",
            "standings": r"/ask/(?:standings|rankings)",
            "scores": r"/ask/(?:scores|schedule)",
            "stats": r"/ask/(?:stats|leaders)"
        }

    def create_crawler_config(self) -> CrawlerRunConfig:
        """
        Configurazione ESTREMAMENTE aggressiva per StatMuse.
        Il sito ha molto rumore che deve essere escluso a livello di crawler.
        """
        return CrawlerRunConfig(
            # Esclusione tag standard
            excluded_tags=[
                'nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript',
                'figure', 'figcaption', 'svg', 'canvas'
            ],
            # Selettori CSS per elementi specifici di StatMuse da escludere
            excluded_selector=(
                # Navigazione e UI
                ".site-nav, .global-nav, .top-nav, .bottom-nav, "
                # Sidebar e contenuti collaterali
                ".sidebar, .side-panel, .right-rail, .left-rail, "
                # Sezioni "More X Stats" (rumore tipico di StatMuse)
                "[class*='more-'], [class*='related-'], [class*='also-'], "
                # Leader boards, standings, schedule nelle pagine ask/player
                ".leaders-section, .standings-section, .schedule-section, "
                ".scores-section, .rankings-section, .betting-section, "
                ".fantasy-section, .trending-section, "
                # Related searches e link correlati
                ".related-searches, .related-links, .see-also, "
                # Footer e elementi finali
                ".site-footer, .page-footer, .footer-content, "
                # App promo e elementi marketing
                ".app-promo, .download-app, .shop-link, "
                # Elementi di condivisione/social
                ".share-buttons, .social-links"
            ),
            word_count_threshold=15,  # Aumentato per filtrare frammenti piccoli
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True,
            remove_overlay_elements=True,
            scan_full_page=False,  # IMPORTANTE: non scansionare tutta la pagina, solo il main content
            wait_for_images=False,
            page_timeout=30000,
            # Focus solo sul contenuto principale
            css_selector="main, article, [role='main'], .query-result, .player-profile, .content-primary",
        )
    
    def extract_title(self, result) -> str:
        """Estrae il titolo dando priorità assoluta all'H1 del markdown, ripulito da eventuali link."""
        markdown = self.parse_markdown(result)
        
        if markdown:
            # Cerca il primo H1. StatMuse formatta la risposta/query principale qui.
            h1 = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
            if h1:
                raw_title = h1.group(1).strip()
                # Rimuove la sintassi markdown dei link: [Testo](url) -> Testo
                clean_title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', raw_title)
                return clean_title.strip()
                
        # Fallback al comportamento della classe base se non trova l'H1
        title = super().extract_title(result)
        if title and title != "N/A":
            return title.replace(" | StatMuse", "").strip()
            
        return "N/A"

    def parse_markdown(self, result) -> str:
        """Estrae il markdown grezzo dal risultato crawl4ai."""
        if hasattr(result, 'markdown_v2') and result.markdown_v2:
            return result.markdown_v2.raw_markdown
        elif hasattr(result, 'markdown') and result.markdown:
            return str(result.markdown)
        return ""

    def parse_html(self, result) -> str:
        """Estrae l'HTML grezzo."""
        if hasattr(result, 'html') and result.html:
            return result.html
        return ""

    # =================================================================
    # POST-PROCESSING: Rimozione rumore dal markdown
    # =================================================================

    def _clean_markdown(self, markdown: str, url: str) -> str:
        """
        Pulizia aggressiva del markdown per rimuovere rumore residuo.
        Questo è il cuore del parser - rimuove tutto ciò che non è contenuto informativo.
        """
        if not markdown:
            return ""
        
        lines = markdown.split('\n')
        cleaned_lines = []
        skip_patterns = self._get_skip_patterns(url)
        in_skip_block = False
        skip_block_end = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Gestione blocchi da saltare (multi-linea)
            if in_skip_block:
                if skip_block_end and re.search(skip_block_end, stripped, re.IGNORECASE):
                    in_skip_block = False
                    skip_block_end = None
                continue
            
            # Check inizio blocco da saltare
            block_skip = self._detect_skip_block(stripped, skip_patterns)
            if block_skip:
                in_skip_block = True
                skip_block_end = block_skip.get('end_pattern')
                continue
            
            # Skip linee singole che matchano pattern di rumore
            if self._is_noise_line(stripped, skip_patterns):
                continue
            
            # Skip linee vuote multiple (max 1 newline consecutivo)
            if not stripped and cleaned_lines and not cleaned_lines[-1].strip():
                continue
            
            cleaned_lines.append(line)
        
        # Seconda passata: rimuovi sezioni finali tipiche
        cleaned = '\n'.join(cleaned_lines)
        cleaned = self._remove_trailing_noise(cleaned)
        
        # Terza passata: pulizia pattern specifici StatMuse
        cleaned = self._clean_statmuse_patterns(cleaned)
        
        return cleaned.strip()

    def _get_skip_patterns(self, url: str) -> Dict[str, Any]:
        """Restituisce i pattern di rumore specifici per tipo di pagina."""
        path = urlparse(url).path
        
        # Pattern comuni a tutte le pagine StatMuse
        common = {
            'nav_links': r'^\*\s*\[.*?\]\(https://www\.statmuse\.com/(?:auth|nba|nhl|mlb|nfl|fc|cfb|wnba|pga|money|scores|trending|product|company|blog|shop|players)\s*\)',
            'image_only_lines': r'^!\[.*?\]\(https?://.*?\)$',
            'empty_table_rows': r'^\|\s*\|\s*$',
            'sign_in': r'^\[?\s*Sign\s+in\s*\]?',
        }
        
        # Pattern per pagine ask (query results)
        ask_patterns = {
            'more_stats': r'^#{1,3}\s*More\s+[A-Za-z\s]+\s+Stats',
            'team_rankings': r'^#{1,3}\s*\w+\s+Rankings',
            'team_standings': r'^#{1,3}\s*(?:Conference\s+)?Standings',
            'schedule': r'^#{1,3}\s*Schedule',
            'scores': r'^#{1,3}\s*Scores',
            'last_game': r'^#{1,3}\s*Last\s+Game',
            'leaders': r'^#{1,3}\s*(?:NBA|NHL|MLB|NFL|FC|CFB|WNBA)\s+\d{4}-\d{2}\s+Leaders',
            'fantasy': r'^#{1,3}\s*(?:NBA|NHL|MLB|NFL|FC|CFB|WNBA)\s+Fantasy',
            'betting': r'^#{1,3}\s*(?:NBA|NHL|MLB|NFL|FC|CFB|WNBA)\s+Betting',
            'related_searches': r'^#{1,3}\s*Related\s+Searches',
            'trending': r'^#{1,3}\s*Trending',
            'app_promo': r'#{1,3}\s*StatMuse\s+App',
        }
        
        # Pattern per pagine player
        player_patterns = {
            'more_stats': r'^#{1,3}\s*More\s+[A-Za-z\s]+\s+Stats',
            'career_stats_link': r'^#{1,3}\s*Career\s+Stats',
            'game_logs': r'^#{1,3}\s*Game\s+Logs',
            'news': r'^#{1,3}\s*\w+\s+News',
        }
        
        if re.search(self.domain_patterns["ask"], path):
            common.update(ask_patterns)
        elif re.search(self.domain_patterns["player"], path):
            common.update(player_patterns)
        
        return common

    def _detect_skip_block(self, line: str, patterns: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Rileva se una linea è l'inizio di un blocco da saltare.
        Restituisce dict con 'end_pattern' se è un blocco multi-linea.
        
        BUG FIX: i pattern originali cercavano solo header con #.
        StatMuse emette molte sezioni come plain text (senza #), quindi
        bisogna matchare anche le varianti senza prefisso.
        """
        # Helper: controlla sia la variante con # che quella plain-text
        def _matches(pat_key: str, fallback: str = r'^$') -> bool:
            pat = patterns.get(pat_key, fallback)
            # prova il pattern originale (con #)
            if re.search(pat, line, re.IGNORECASE):
                return True
            # prova la variante plain-text (rimuove ^#{1,3}\s* dal pattern)
            plain_pat = re.sub(r'^\^#{1,3}\\s\*', '', pat)
            if plain_pat != pat:
                return bool(re.search(plain_pat, line, re.IGNORECASE))
            return False

        # Blocco "More X Stats"
        if _matches('more_stats'):
            return {'end_pattern': r'^#{1,2}\s+(?!(?:More|Related|Trending|NBA|NHL|MLB|NFL|FC|CFB|WNBA))'}

        # Blocco "Related Searches"
        if _matches('related_searches'):
            return {'end_pattern': r'^#{1,2}\s+'}

        # Blocco classifiche/standings — plain: "2025-26 Conference Standings" o "Standings"
        if _matches('team_standings') or re.search(
            r'^\d{4}-\d{2,4}\s+(?:Conference\s+)?Standings\s*$|^(?:Conference\s+)?Standings\s*$',
            line, re.IGNORECASE
        ):
            return {'end_pattern': r'^#{1,2}\s+'}

        # Blocco schedule — plain: "Schedule"
        if _matches('schedule') or re.search(r'^Schedule\s*$', line, re.IGNORECASE):
            return {'end_pattern': r'^#{1,2}\s+'}

        # Blocco leaders
        if _matches('leaders') or re.search(r'^Team\s+Leaders\s*$', line, re.IGNORECASE):
            return {'end_pattern': r'^#{1,2}\s+(?!(?:NBA|NHL|MLB|NFL|FC|CFB|WNBA))'}

        # Blocco rankings — plain: "Team Rankings"
        if _matches('team_rankings') or re.search(r'^Team\s+Rankings\s*$', line, re.IGNORECASE):
            return {'end_pattern': r'^#{1,2}\s+'}

        # Blocco Last Game
        if re.search(r'^Last\s+Game\s*$', line, re.IGNORECASE):
            return {'end_pattern': r'^#{1,2}\s+'}

        # Blocco Playoffs Rankings
        if re.search(r'^Playoffs?\s+\w+', line, re.IGNORECASE):
            return {'end_pattern': r'^#{1,2}\s+'}

        return None

    def _is_noise_line(self, line: str, patterns: Dict[str, Any]) -> bool:
        """Determina se una singola linea è rumore."""
        if not line:
            return False  # Linee vuote gestite separatamente
        
        # Link di navigazione
        if re.search(r'^\[?\s*(?:Home|NBA|NHL|FC|MLB|NFL|CFB|WNBA|PGA|Money|Scores|Trending|Examples|Data|Gallery|About|Blog|Shop)\s*\]?', line):
            return True
        
        # Immagini isolate senza testo contestuale
        if re.match(r'^!\[.*?\]\(https?://.*?\)$', line):
            return True
        
        # Link con solo immagini (badge team/giocatori senza testo)
        if re.match(r'^\[\s*!\[.*?\]\(.*?\)\s*\]\(.*?\)$', line):
            return True
        
        # Linee con solo separatori di tabella vuoti
        if re.match(r'^\|(\s*\|)+$', line):
            return True
        
        # "Sign in" o elementi auth
        if re.search(r'Sign\s+in|Log\s+in|Register', line, re.IGNORECASE):
            return True
        
        return False
    
    def _remove_trailing_noise(self, text: str) -> str:
        """
        La ghigliottina finale: purificazione assoluta delle stringhe.
        Rimuove TUTTI i caratteri non alfabetici prima di fare il check, 
        rendendo impossibile per qualsiasi spazio invisibile ingannare il parser.
        """
        if not text:
            return ""
            
        # splitlines() gestisce nativamente le differenze tra \r\n (Windows) e \n (Unix)
        lines = text.splitlines()
        cut_index = len(lines)
        
        start_markers = [
            "relatedsearches", "teamleaders", "teamrankings", 
            "schedule", "lastgame", "playoffs", "trending", "statmuseapp",
            "nbafantasy", "nhlfantasy", "mlbfantasy", "nflfantasy",
            "nbabetting", "nhlbetting", "mlbbetting", "nflbetting",
            "nbastandings", "nhlstandings", "mlbstandings", "nflstandings",
            "nbascores", "nhlscores", "mlbscores", "nflscores",
            "conferencestandings"
        ]
        
        for i, line in enumerate(lines):
            # Se è una riga di tabella Markdown, la ignoriamo a prescindere
            # Questo evita falsi positivi se, ad esempio, un giocatore si chiama "Moreland"
            if line.lstrip().startswith('|'):
                continue
                
            # PURIFICAZIONE ESTREMA: Mantiene SOLO le lettere a-z.
            # Rimuove numeri, spazi, punteggiatura e caratteri invisibili.
            alpha_only = re.sub(r'[^a-z]', '', line.lower())
            
            if not alpha_only:
                continue
                
            # Check 1: La riga purificata inizia con uno dei nostri marker?
            if any(alpha_only.startswith(m) for m in start_markers):
                cut_index = i
                break
                
            # Check 2: Gestione dinamica di "More [Qualsiasi Cosa] Stats" (es. morelakersstats)
            if alpha_only.startswith("more") and "stats" in alpha_only:
                cut_index = i
                break
                
            # Check 3: Parola singola "Standings" isolata
            if alpha_only == "standings":
                cut_index = i
                break
                
        # Ricostruisce il testo pulito
        return '\n'.join(lines[:cut_index]).strip()
    
    def _clean_statmuse_patterns(self, text: str) -> str:
        """
        Pulizia finale di pattern specifici di StatMuse.
        """
        # 0. Rimuove la fastidiosa riga "Interpreted as:" (con o senza # davanti)
        text = re.sub(r'(?m)^\s*#{0,6}\s*Interpreted\s+as:\s*$', '', text)

        # 1. Linked images [![text](url)](url "title") → text
        text = re.sub(r'\[!\[(.*?)\]\([^)]+\)\]\([^)]+(?:\s+"[^"]+")?\)', r'\1', text)

        # 2. Team badge in tabella: ![ABBR ABBR](url) o ![ABBR ABBR](url "full name") → ABBR
        text = re.sub(
            r'!\[([A-Z]{2,5})\s+[A-Z]{2,5}\]\(https?://[^)]+(?:\s+"[^"]+")?\)',
            r'\1',
            text
        )

        # 3. Rimuovi tutte le restanti immagini StatMuse (cdn e www)
        text = re.sub(
            r'!\[[^\]]*\]\(https?://(?:cdn|www)\.statmuse\.com[^)]*(?:\s+"[^"]+")?\)',
            '',
            text
        )

        # 4. Pulisci markdown link interni a statmuse (lascia solo testo)
        text = re.sub(r'\[([^\]]+)\]\(https://www\.statmuse\.com/[^)]+\)', r'\1', text)

        # 5. Collassa spazi multipli
        text = re.sub(r'[ \t]+', ' ', text)

        # 6. Collassa newline multipli (max 3)
        text = re.sub(r'\n{4,}', '\n\n\n', text)

        return text.strip()

    # =================================================================
    # ESTRAZIONE DATI STRUTTURATI
    # =================================================================

    def _detect_page_type(self, path: str) -> str:
        for ptype, pattern in self.domain_patterns.items():
            if re.search(pattern, path):
                return ptype
        return "generic"

    def _convert_value(self, value: str) -> Any:
        value = value.strip()
        if not value:
            return None
        if value.endswith('%'):
            try:
                return float(value[:-1]) / 100
            except ValueError:
                return value
        if re.match(r'^\d+-\d+$', value):
            return value
        if re.match(r'^[+\-]\d+(\.\d+)?$', value):
            try:
                return float(value)
            except ValueError:
                return value
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def _extract_all_tables(self, markdown: str) -> List[StatMuseTable]:
        """Estrae tabelle dal markdown già pulito."""
        tables = []
        table_pattern = r'((?:\|[^\n]*\|\n?)+)'
        
        for match in re.finditer(table_pattern, markdown):
            table_text = match.group(1).strip()
            if not table_text or '\n' not in table_text:
                continue
            
            lines = [l.strip() for l in table_text.split('\n') if l.strip()]
            if len(lines) < 2:
                continue
            
            # Cerca titolo nella riga precedente
            start_pos = match.start()
            preceding = markdown[max(0, start_pos-300):start_pos]
            title_match = re.search(r'#{1,3}\s+([^\n#]+?)(?:\n|$)', preceding)
            title = title_match.group(1).strip() if title_match else None
            
            table = StatMuseTable(title=title)
            
            # Header
            header_line = lines[0]
            headers = [h.strip() for h in header_line.split('|') if h.strip()]
            table.headers = headers
            
            # Trova inizio dati
            data_start = 1
            if len(lines) > 1 and re.match(r'^\|?[\s\-:|]+\|?$', lines[1]):
                data_start = 2
            
            for line in lines[data_start:]:
                cells = []
                for cell in line.split('|'):
                    cell = cell.strip()
                    if not cell:
                        continue
                    cells.append(cell)
                
                if len(cells) >= len(headers):
                    row = {headers[i]: self._convert_value(cells[i]) for i in range(len(headers))}
                    table.rows.append(row)
                elif len(cells) > 0:
                    table.rows.append({f"col_{i}": self._convert_value(c) for i, c in enumerate(cells)})
            
            if table.rows:
                tables.append(table)
        
        return tables

    def _extract_query_title(self, markdown: str) -> Optional[str]:
        h1 = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
        return h1.group(1).strip() if h1 else None

    def _extract_interpreted_query(self, markdown: str) -> Optional[str]:
        match = re.search(r'Interpreted\s+as:\s*\n+([^\n#]+)', markdown, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_answer_text(self, markdown: str) -> Optional[str]:
        lines = markdown.split('\n')
        capturing = False
        answer_lines = []
        for line in lines:
            if re.search(r'Interpreted\s+as:', line, re.IGNORECASE):
                capturing = True
                continue
            if capturing:
                if line.startswith('|') or line.startswith('#') or line.startswith('!['):
                    break
                if line.strip():
                    answer_lines.append(line.strip())
        return ' '.join(answer_lines) if answer_lines else None

    def _extract_player_summary(self, markdown: str) -> Optional[str]:
        patterns = [
            r'##\s+([A-Z][^\n]+?(?:averaged|played|has|is|are|was|were)[^\n]+)',
            r'###\s*Summary\s*\n+([^\n#]+)',
            r'^([A-Z][a-zA-Z\s\.]+(?:averaged|played)\s+[\d\.]+[^\n]+)'
        ]
        for pat in patterns:
            match = re.search(pat, markdown, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_player_info(self, markdown: str) -> Dict[str, Any]:
        info = {"name": None, "team": None, "position": None, "season": None}
        name_match = re.search(r'#\s*([A-Z][a-zA-Z\s\.]+?)(?:\n|\|)', markdown)
        if name_match:
            info["name"] = name_match.group(1).strip()
        team_match = re.search(r'(?:for|with|played\s+for)\s+the\s+([A-Z][a-zA-Z\s]+?)(?:\.|\n|,)', markdown)
        if team_match:
            info["team"] = team_match.group(1).strip()
        season_match = re.search(r'(\d{4}-\d{2,4})\s+season', markdown)
        if season_match:
            info["season"] = season_match.group(1)
        return info

    def _build_structured_data(self, url: str, clean_markdown: str) -> Dict[str, Any]:
        """Costruisce il payload strutturato dal markdown pulito."""
        path = urlparse(url).path
        page_type = self._detect_page_type(path)
        tables = self._extract_all_tables(clean_markdown)
        
        data = {
            "page_type": page_type,
            "tables": [t.to_dict() for t in tables]
        }
        
        if page_type == "player":
            data["player"] = self._extract_player_info(clean_markdown)
            data["summary"] = self._extract_player_summary(clean_markdown)
        elif page_type == "ask":
            data["query"] = self._extract_query_title(clean_markdown)
            data["interpreted_as"] = self._extract_interpreted_query(clean_markdown)
            data["answer_text"] = self._extract_answer_text(clean_markdown)
        
        return data

    # =================================================================
    # OVERRIDE format_result
    # =================================================================

    def format_result(self, url: str, result) -> Dict[str, Any]:
        raw_markdown = self.parse_markdown(result)
        clean_markdown = self._clean_markdown(raw_markdown, url)
        
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            "html_text": self.parse_html(result),
            "parsed_text": clean_markdown
        }

    async def parse(self, url: str) -> Dict[str, Any]:
        """Entry point compatibile con il tuo main()."""
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
                "content_markdown": "",
                "html_text": "",
                "structured_data": {}
            }


# =================================================================
# TEST CON SALVATAGGIO FILE
# =================================================================
async def main():
    parser = StatMuseParser()
    url = "https://www.statmuse.com/nba/ask/nba-ppg-leaders-this-season"
    
    # Crea directory output
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Esegui il parsing
    risultato = await parser.parse(url)
    
    if risultato["success"]:
        print(f"Titolo: {risultato['title']}")
        print("\n--- CONTENUTO PULITO (primi 800 caratteri) ---")
        print(risultato["parsed_text"][:800] + "...")
        
        # 1. Salva HTML grezzo
        html_file = output_dir / f"statmuse_html_{timestamp}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(risultato["html_text"])
        print(f"\n[✓] HTML grezzo salvato in: {html_file}")
        
        # 2. Salva markdown PULITO
        md_file = output_dir / f"statmuse_clean_{timestamp}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(risultato["parsed_text"])
        print(f"[✓] Markdown pulito salvato in: {md_file}")
        
        # 3. Salva output completo del parser in JSON
        json_file = output_dir / f"statmuse_parsed_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(risultato, f, indent=2, ensure_ascii=False, default=str)
        print(f"[✓] Output parser salvato in: {json_file}")
        
        # 4. Salva anche il markdown grezzo per confronto
        # Lo estraiamo dal result interno (hack per debug)
        # In produzione non serve
        
    else:
        print(f"Errore: {risultato['error']}")
        
        error_file = output_dir / f"statmuse_error_{timestamp}.json"
        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(risultato, f, indent=2, ensure_ascii=False)
        print(f"[✓] Log errore salvato in: {error_file}")


if __name__ == "__main__":
    asyncio.run(main())