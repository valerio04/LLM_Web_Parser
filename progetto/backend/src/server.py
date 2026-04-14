from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List, Any
from pathlib import Path
import json

from parsers.parser1 import IlPostParser
from parsers.parser2 import StatMuseParser
from parsers.parser3 import EurLexParser
from parsers.parser_wikipedia import WikipediaParser

app = FastAPI(title="Parser API")

# Modelli Pydantic per validazione I/O

class ParseResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str

# chiedere al professore se bisogna fare in questo modo o basta restituire un dizionario nella funzione
# chiedere se usare liste o set per evaluation
# chiedere se queste funzioni devono essere eseguite solo su file testati da noi o da un qualsiasi file nel dominio
# chiedere se è corretta l'organizazione dei file txt

class DomainsResponse(BaseModel):
    domains: Dict[str, List[str]]  # domain -> list of URLs

class GoldStandardResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str

class FullGoldStandardResponse(BaseModel):
    domain: str
    gold_standards: List[Dict[str, Any]]

class EvaluateRequest(BaseModel):
    parsing_result: Dict[str, Any]
    gold_standard: str

class EvaluateResponse(BaseModel):
    metrics: Dict[str, float]

class FullGsEvalRequest(BaseModel):
    domain: str

class FullGsEvalResponse(BaseModel):
    domain: str
    aggregated_metrics: Dict[str, float]


# Endpoint

@app.get("/parse")
async def parse_document(url: str) -> ParseResponse:
    """
    Esegue il parser per un documento di un dominio.
    """
    # Seleziona il parser in base al dominio
    if "wikipedia.org" in url:
        parser = WikipediaParser()
    elif "ilpost.it" in url:
        parser = IlPostParser()
    elif "statmuse.com" in url:
        parser = StatMuseParser()
    elif "eur-lex.europa.eu" in url:
        parser = EurLexParser()
    else:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    try:
        result = await parser.run(url)
        return ParseResponse(url = result['url'], 
                             domain=result['domain'], 
                             title=result['title'], 
                             html_text=result['html_text'], 
                             parsed_text=result['parsed_text'])
    
    # TODO: testare se questa eccezione viene catturata quando il parsing fallisce (es: url non esistente, timeout, ecc.)
    except Exception as e:
        print(f"[ERROR] Errore durante il parsing: {e}")
        raise HTTPException(status_code=500, detail="Errore durante il parsing")

@app.get("/domains")
async def get_domains() -> DomainsResponse:
    """
    Restituisce la lista dei domini assegnati con i link associati.
    """
    pass

@app.get("/gold_standard")
async def get_gold_standard(url: str) -> GoldStandardResponse:
    """
    Restituisce il gold standard per un documento.
    """

    # Determina il file JSON da cui caricare il gold standard in base al dominio dell'URL
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
    if "wikipedia.org" in url:
        json_path = base_dir / "gs_data" / "wikipedia_org"/ "gs.json"
    elif "ilpost.it" in url:
        json_path = base_dir / "gs_data" / "ilpost_it" / "gs.json"
    elif "statmuse.com" in url:
        json_path = base_dir / "gs_data" / "statmuse_com" / "gs.json"
    elif "eur-lex.europa.eu" in url:
        json_path = base_dir / "gs_data" / "eurlex_europa_eu" / "gs.json" 
    else:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    # Carica i dati dal file JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)

    print("Oggetto JSON caricato:", gold_data)

    # cerco l'entry corrispondente all'url e restituisco il gold standard
    for entry in gold_data:
        if entry['url'] == url:
            gold_file_path = base_dir / "gs_data" / entry['gold_file']
            html_file_path = base_dir / "gs_data" / entry['html_file']

            # Leggi il contenuto del file gold standard
            with open(gold_file_path, 'r', encoding='utf-8') as f:
                gold_text = f.read()

            # Leggi il contenuto del file html standard
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_text = f.read()

            return GoldStandardResponse(url=entry['url'], domain=entry['domain'], title=entry['title'], html_text=html_text, gold_text=gold_text) 
    raise HTTPException(status_code=404, detail="l'url non è nel GS")


@app.get("/full_gold_standard")
async def get_full_gold_standard(domain: str) -> FullGoldStandardResponse:
    """
    Restituisce tutto il GS del dominio.
    """
    pass

@app.post("/evaluate")
async def evaluate_result(request: EvaluateRequest) -> EvaluateResponse:
    """
    Dato risultato parsing e gs restituisce le metriche di evaluation.
    """
    pass

@app.get("/full_gs_eval")
async def get_full_gs_eval(domain: str) -> FullGsEvalResponse:
    """
    Restituisce l'evaluation aggregata su tutto il GS.
    """
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)