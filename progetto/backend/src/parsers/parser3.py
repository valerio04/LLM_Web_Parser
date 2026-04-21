import asyncio
import re
import html
from typing import Any, Dict
from crawl4ai import CrawlerRunConfig, CacheMode, CrawlResult
from .base_parser import BaseParser

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
            excluded_tags=['nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript', 'form', 'iframe'],
            excluded_selector=(
                "header#op-header, #op-header-pdf, .ecl-site-footer, .ecl-site-header__banner, "
                ".sidebar-offcanvas, .NavSearch, .EurlexSearch, .Sidebar, .SidebarTools, "
                ".PubFormat, .PubFormats, .Logo, .Emission, "
                ".wt-banner, .modal, .cookie-consent, #iubenda-cs-banner, .DocumentTitle.pull-left, #PP1Contents, #PP2Contents, #PP3Contents, .hd-ti, .hd-lg, .hd-oj, #PP3, #PP1, #PP2, .lseu-section-relevant-terms"
            ),
            css_selector=".panel.panel-default.PagePanel, .EurlexContent",
            word_count_threshold=0,
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True,
            delay_before_return_html=3.5 
        )
    
    def extract_title(self, result: CrawlResult) -> str:
        if not result.html:
            return "EUR_Lex_Senza_Titolo"
            
        match = re.search(r'<title>(.*?)</title>', result.html, re.IGNORECASE)
        if match:
            title = html.unescape(re.sub(r'<[^>]+>', '', match.group(1)).strip())
            return title.replace(" - EUR-Lex", "")
                
        if result.metadata:
            return result.metadata.get("title", "EUR_Lex_Senza_Titolo")
        return "EUR_Lex_Senza_Titolo"

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