from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List, Any
from pathlib import Path
import json

from .evaluation import *
from .parsers.parser1 import IlPostParser
from .parsers.parser2 import StatMuseParser
from .parsers.parser3 import EurLexParser
from .parsers.parser_wikipedia import WikipediaParser

app = FastAPI(title="Parser API")

# Modelli Pydantic per validazione I/O

class ParseResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str

class ParseRequest(BaseModel):
    url: str
    html_text: str

class DomainsResponse(BaseModel):
    domains: List[str]

class GoldStandardResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str

class FullGoldStandardResponse(BaseModel):
    gold_standard: List[GoldStandardResponse]

class EvaluateRequest(BaseModel):
    parsed_text: str
    gold_text: str

class EvaluateResponse(BaseModel):
    token_level_eval: Dict[str, float]
    x_eval: Dict[str, Any] = {}

class FullGsEvalResponse(BaseModel):
    token_level_eval: Dict[str, float]
    x_eval: Dict[str, Any] = {}


# Endpoint

@app.get("/parse")
async def parse_document(url: str) -> ParseResponse:
    """
    Esegue il parser per un documento di un dominio.
    Parametri: URL del documento da parsare
    Ritorna: URL, dominio, titolo, testo HTML originale, testo parsato
    """

    # 1. Ricava le informazioni di parser e path
    parser= find_parser(url)
    
    # 2. Se parser_info è None (dominio non riconosciuto), da subito l'eccezione 400
    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")
        
    
    try:
        result = await parser.run(url)
        return ParseResponse(url = result['url'], 
                             domain=result['domain'], 
                             title=result['title'], 
                             html_text=result['html_text'], 
                             parsed_text=result['parsed_text'])
    
    except Exception as e:
        print(f"[ERROR] Errore durante il parsing: {e}")
        raise HTTPException(status_code=500, detail="Errore durante il parsing")



@app.post("/parse")
async def parse_document_from_html(parse_request: ParseRequest) -> ParseResponse:
    """
    Esegue il parser per un documento di un dominio direttamente dall'HTML presente nel gold standard (se esiste).
    Parametri: URL, file_HTML
    Ritorna: URL, dominio, titolo, testo HTML originale, testo parsato
    """

    url = parse_request.url
    html_text = parse_request.html_text
    
    # 1. Ricava le informazioni di parser e path
    parser = find_parser(url)

    # 2. Se parser è None (dominio non riconosciuto), da subito l'eccezione 400
    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")
        
    
    try:
        result = await parser.run_from_html(url, html_text)
        return ParseResponse(url = result['url'], 
                             domain=result['domain'], 
                             title=result['title'], 
                             html_text=result['html_text'], 
                             parsed_text=result['parsed_text'])
    
    except Exception as e:
        print(f"[ERROR] Errore durante il parsing: {e}")
        raise HTTPException(status_code=500, detail="Errore durante il parsing")



@app.get("/domains")
async def get_domains() -> DomainsResponse:
    """
    Restituisce la lista dei domini assegnati con i link associati.
    Parametri: None
    Ritorna: lista domini
    """
    # cerca il path del progetto a partire da questo file
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
    # prende il percorso del file domains.json
    json_path = base_dir / "domains.json"

    if not json_path.exists():
        print(f"[WARNING] File domains.json non trovato: {json_path}")
        raise HTTPException(status_code=500, detail="File domains.json non trovato")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        domains_data = json.load(f)

    return DomainsResponse(domains=domains_data.get("domains", []))

@app.get("/gold_standard")
async def get_gold_standard(url: str) -> GoldStandardResponse:
    """
    Restituisce il gold standard per un documento.
    Parametri: URL
    Ritorna: URL, dominio, titolo, testo HTML originale, gold_text
    """
    
    # cerca il path del progetto a partire da questo file
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
    # restituisce il percorso del file JSON associato al dominio
    json_path = find_path(url)

    # Se il percorso è None (dominio non riconosciuto), da subito l'eccezione 400
    if not json_path:
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
    Parametri: dominio
    Ritorna: List[{URL, dominio, title, HTML_file, gold_text}]
    """

    # cerca il path del progetto a partire da questo file
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
    # restituisce il percorso del file JSON associato al dominio
    json_path = find_path(domain)

    # Se il percorso è None (dominio non riconosciuto), da subito l'eccezione 400
    if not json_path:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    
    
    # Carica i dati dal file JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)

    # inizializzo la lista che conterrà i GoldStandardResponse
    gold_standard=[]
    for entry in gold_data:
        gold_file_path = base_dir / "gs_data" / entry['gold_file']
        html_file_path = base_dir / "gs_data" / entry['html_file']

        # Leggi il contenuto del file gold standard
        with open(gold_file_path, 'r', encoding='utf-8') as f:
            gold_text = f.read()

        # Leggi il contenuto del file html standard
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_text = f.read()

        gold_standard.append(GoldStandardResponse(url=entry['url'], domain=entry['domain'], title=entry['title'], html_text=html_text, gold_text=gold_text))
    result = FullGoldStandardResponse(gold_standard=gold_standard)
    return result



@app.post("/evaluate")
async def evaluate_result(request: EvaluateRequest) -> EvaluateResponse:
    """
    Esegue l'eval tra il testo parsato e il gold standard.
    Parametri: parsed_text e gold_text
    Ritorna: risultati delle metriche associate all'URL (token_level_eval e x_level eval)
    """    
        
    token_level_eval = Evaluator.token_level_eval(request.parsed_text, request.gold_text)
    x_eval = Evaluator.x_eval_complete(request.parsed_text, request.gold_text)
    

    result=EvaluateResponse(token_level_eval=token_level_eval, x_eval=x_eval)
    return result


@app.get("/full_gs_eval")
async def get_full_gs_eval(domain: str) -> FullGsEvalResponse:
    """
    Esegue l'eval su tutto il GS di un dominio e restituisce la media dei risultati.
    Parametri: dominio
    Ritorna: risultati delle metriche associate al dominio (token_level_eval e x_level eval)
    """
    
    # restituisce il percorso del file JSON associato al dominio
    json_path = find_path(domain)
    
    # Se il percorso è None (dominio non riconosciuto), da subito l'eccezione 400
    if not json_path:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    
    # Carico i dati contenuti nel file json
    with open(json_path, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
    
    # chiamo la funzione che calcola le metriche di tutto il GS del dominio
    eval_response = await evaluate_gold_standard(gold_data)

    if not eval_response:
        return FullGsEvalResponse(
            token_level_eval={"precision": 0, "recall": 0, "f1": 0}, 
            x_eval={"boilerplate_ratio_extracted": 0, "boilerplate_fidelity": 0, "cosine_similarity": 0}
        )
    
    # Inizializziamo le liste
    data = {
        "p": [], "r": [], "f1": [],
        "cos": [], "bp_ext": [], "bp_diff": []
    }

    # Popolamento delle liste con i risultati di ogni entry del GS
    for metrics in eval_response.values():
        data["p"].append(metrics.get("precision", 0))
        data["r"].append(metrics.get("recall", 0))
        data["f1"].append(metrics.get("f1", 0))
        
        x = metrics.get("x_eval", {})
        data["cos"].append(x.get("cosine_similarity", 0))
        data["bp_ext"].append(x.get("boilerplate_ratio_extracted", 0))
        data["bp_diff"].append(x.get("boilerplate_fidelity", 0))

    # Helper per la media
    avg = lambda l: sum(l) / len(l) if l else 0.0

    return FullGsEvalResponse(
        token_level_eval={
            "precision": avg(data["p"]),
            "recall": avg(data["r"]),
            "f1": avg(data["f1"])
        },
        x_eval={
            "boilerplate_ratio_extracted": avg(data["bp_ext"]),
            "boilerplate_fidelity": avg(data["bp_diff"]),
            "cosine_similarity": avg(data["cos"])
        }
    )

def find_parser(url: str) -> Optional[BaseParser]:
    """
    Restituisce il parser corrispondente al dominio dell'URL.
    Parametri: URL
    Ritorna: parser associato all'URL
    """
    if "wikipedia.org" in url:
        return WikipediaParser()
    elif "ilpost.it" in url:
        return IlPostParser()
    elif "statmuse.com" in url:
        return StatMuseParser()
    elif "eur-lex.europa.eu" in url:
        return EurLexParser()
    else:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        return None
    
def find_path(url: str) -> Optional[Path]:
    """
    Restituisce il percorso del file JSON corrispondente al dominio dell'URL.
    Parametri: URL
    Ritorna: percorso del file JSON associato al dominio
    """
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
    if "wikipedia.org" in url:
        return base_dir / "gs_data" / "wikipedia_org"/ "gs.json"
    elif "ilpost.it" in url:
        return base_dir / "gs_data" / "ilpost_it" / "gs.json"
    elif "statmuse.com" in url:
        return base_dir / "gs_data" / "statmuse_com" / "gs.json"
    elif "eur-lex.europa.eu" in url:
        return base_dir / "gs_data" / "eurlex_europa_eu" / "gs.json"
    else:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        return None
