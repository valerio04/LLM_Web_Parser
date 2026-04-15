import asyncio
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from .base_parser import BaseParser

# Questo parser si riferisce al dominio: https://eur-lex.europa.eu


#TODO: aggiungere golden text piu variegati per testare meglio il parser
#TODO: sbaglia i titoli, non riesce a estrarre quelli corretti, forse perche sono in un tag particolare da capire meglio
class EurLexParser(BaseParser):
    def __init__(self):
        super().__init__("eur-lex.europa.eu")

    def create_crawler_config(self):
        return CrawlerRunConfig(
            excluded_tags=['nav', 'footer', 'header', 'aside'],
            word_count_threshold=10,
            cache_mode=CacheMode.BYPASS,
            exclude_external_images=True
        )
    
    def format_result(self, url, result):
        """Formats the final result. Can be overridden by subclasses."""
        return {
            "url": url,
            "domain": self.domain,
            "title": self.extract_title(result),
            #"html_text": self.parse_html(result),
            "parsed_text": self.parse_markdown(result)[:500]
        }


#per usare questa devi togliere il punto davanti base_parsr
#per testare se il parsing restituisce i campi corretti:
if __name__ == "__main__":
    url = input("Inserisci l'URL della pagina di eur-lex.europa.eu: ")
    parser = EurLexParser()
    result = asyncio.run(parser.run(url))
    print("--- JSON OUTPUT ---")
    print(result)