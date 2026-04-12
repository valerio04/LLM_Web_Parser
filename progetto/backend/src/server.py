
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def esempio_configurazioni():
    url = "https://en.wikipedia.org/wiki/Minerva"

    # 1. BROWSER CONFIG: Impostazioni "hardware" del browser
    browser_cfg = BrowserConfig(
        headless=True,       # Il browser lavora in background senza aprirsi a schermo
        verbose=True         # Stampa i log nel terminale per aiutarti durante il debug
    )

    # 2. RUN CONFIG: Regole per l'estrazione e la pulizia del testo
    # È QUI che fai la "magia" per pulire il Markdown in automatico!
    run_cfg = CrawlerRunConfig(
        # Esclude tag HTML fastidiosi come menu di navigazione, footer e barre laterali
        excluded_tags=['nav', 'footer', 'header', 'aside'], 
        
        # Ignora i blocchetti di testo troppo corti (elimina bottoni e link sparsi)
        word_count_threshold=10, 
        
        # Ignora la cache (utile quando sviluppi per essere sicuro di scaricare la pagina aggiornata)
        cache_mode=CacheMode.BYPASS, 
        
        # Elimina le immagini dal markdown per avere solo testo pulito
        exclude_external_images=True 
    )

    # 3. ESECUZIONE: Inserisci le configurazioni nel crawler
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Passi il run_cfg specifico alla funzione .arun()
        result = await crawler.arun(url=url, config=run_cfg)
        
        print("--- TITOLO ESTRATTO ---")
        # result.metadata è un dizionario opzionale, meglio usare get()
        title = result.metadata.get("title", "N/A") if result.metadata else "N/A"
        print(title)

        print("\n--- PRIMI 500 CARATTERI DEL MARKDOWN PULITO ---")
        print(result.markdown[:500])

if __name__ == "__main__":
    asyncio.run(esempio_configurazioni())