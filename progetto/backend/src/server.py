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

try:
    from .db.repository import db_schema as repo_db_schema
    from .db.repository import db_stats as repo_db_stats
    from .db.repository import get_web_resource as repo_get_web_resource
    from .db.repository import get_gold_standard as repo_get_gold_standard
    from .db.repository import list_gold_standard_urls as repo_list_gold_standard_urls
    from .db.repository import add_web_resource as repo_add_web_resource
    from .db.repository import add_gold_standard as repo_add_gold_standard
    from .db.repository import delete_web_resource as repo_delete_web_resource
    from .db.repository import delete_gold_standard as repo_delete_gold_standard
except ImportError:
    from db.repository import db_schema as repo_db_schema
    from db.repository import db_stats as repo_db_stats
    from db.repository import get_web_resource as repo_get_web_resource
    from db.repository import get_gold_standard as repo_get_gold_standard
    from db.repository import list_gold_standard_urls as repo_list_gold_standard_urls
    from db.repository import add_web_resource as repo_add_web_resource
    from db.repository import add_gold_standard as repo_add_gold_standard
    from db.repository import delete_web_resource as repo_delete_web_resource
    from db.repository import delete_gold_standard as repo_delete_gold_standard
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
    local: Optional[bool] = False

class DomainsResponse(BaseModel):
    domains: List[str]

class GoldStandardResponse(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str

class GoldStandardUrlsResponse(BaseModel):
    gold_standard_urls: List[str]

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

class AddWebResourceRequest(BaseModel):
    url: str
    html_text: str
    domain: Optional[str] = None
    title: Optional[str] = None


class AddGoldStandardRequest(BaseModel):
    url: str
    gold_text: str


class DeleteByUrlRequest(BaseModel):
    url: str


class StatusResponse(BaseModel):
    status: str

# Endpoint


@app.post("/parse")
async def parse_document(parse_request: ParseRequest) -> ParseResponse:
    """
    Esegue il parser per un documento.

    Se local=True:
    - legge html_text dal DB usando l'URL
    - non scarica la pagina online

    Se local=False:
    - scarica la pagina online
    """

    url = parse_request.url
    parser = find_parser(url)

    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    try:
        if parse_request.local:
            web_resource = repo_get_web_resource(url)

            if not web_resource:
                print(f"[WARNING] URL non presente nel DB: {url}")
                raise HTTPException(
                    status_code=404,
                    detail="URL non presente nel DB"
                )

            result = await parser.run_from_html(
                url,
                web_resource["html_text"]
            )

        else:
            result = await parser.run(url)

        return ParseResponse(
            url=result["url"],
            domain=result["domain"],
            title=result["title"],
            html_text=result["html_text"],
            parsed_text=result["parsed_text"]
        )

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Errore durante il parsing: {e}")
        raise HTTPException(status_code=500, detail="Errore durante il parsing")

#da modificare ancora
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
    Restituisce il gold standard per un documento leggendo dal DB.
    Parametri: URL
    Ritorna: URL, dominio, titolo, HTML grezzo, gold_text
    """

    parser = find_parser(url)

    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    try:
        entry = repo_get_gold_standard(url)

        if not entry:
            print(f"[WARNING] URL non presente nel Gold Standard: {url}")
            raise HTTPException(
                status_code=404,
                detail="URL non presente nel Gold Standard"
            )

        return GoldStandardResponse(
            url=entry["url"],
            domain=entry["domain"],
            title=entry["title"],
            html_text=entry["html_text"],
            gold_text=entry["gold_text"]
        )

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Errore durante il recupero del Gold Standard dal DB: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero del Gold Standard"
        )


@app.get("/gold_standard_urls")
async def get_gold_standard_urls(domain: str) -> GoldStandardUrlsResponse:
    """
    Restituisce tutti gli URL del Gold Standard per un dominio leggendo dal DB.
    Parametri: dominio
    Ritorna: lista URL del Gold Standard
    """
    parser = find_path(domain)

    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {domain}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    try:
        urls = repo_list_gold_standard_urls(domain)

        return GoldStandardUrlsResponse(
            gold_standard_urls=urls
        )

    except Exception as e:
        print(f"[ERROR] Errore durante il recupero degli URL GS dal DB: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero degli URL del Gold Standard"
        )




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

@app.post("/add_web_resource")
async def add_web_resource(request: AddWebResourceRequest) -> StatusResponse:
    """
    Aggiunge una risorsa web nella tabella web_resources.
    Input minimo: url, html_text.
    """

    parser = find_parser(request.url)

    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {request.url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    try:
        domain = request.domain or get_domain_from_url(request.url)
        title = request.title or ""

        repo_add_web_resource(
            url=request.url,
            domain=domain,
            title=title,
            html_text=request.html_text
        )

        return StatusResponse(status="ok")

    except Exception as e:
        print(f"[ERROR] Errore durante add_web_resource: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante l'aggiunta della web resource"
        )


@app.delete("/web_resource")
async def delete_web_resource(request: DeleteByUrlRequest) -> StatusResponse:
    """
    Rimuove una risorsa web.
    Il gold_standard collegato viene rimosso a cascata tramite FK.
    """

    parser = find_parser(request.url)

    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {request.url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    try:
        deleted = repo_delete_web_resource(request.url)

        if not deleted:
            print(f"[WARNING] URL non presente in web_resources: {request.url}")
            raise HTTPException(
                status_code=404,
                detail="URL non presente in web_resources"
            )

        return StatusResponse(status="ok")

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Errore durante delete_web_resource: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante la rimozione della web resource"
        )




@app.post("/add_gold_standard")
async def add_gold_standard(request: AddGoldStandardRequest) -> StatusResponse:
    """
    Aggiunge una entry nella tabella gold_standard.
    La web_resource corrispondente deve già esistere.
    """

    parser = find_parser(request.url)

    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {request.url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    try:
        web_resource = repo_get_web_resource(request.url)

        if not web_resource:
            print(f"[WARNING] URL non presente in web_resources: {request.url}")
            raise HTTPException(
                status_code=404,
                detail="URL non presente in web_resources"
            )

        repo_add_gold_standard(
            url=request.url,
            gold_text=request.gold_text
        )

        return StatusResponse(status="ok")

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Errore durante add_gold_standard: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante l'aggiunta del gold standard"
        )


@app.delete("/gold_standard")
async def delete_gold_standard(request: DeleteByUrlRequest) -> StatusResponse:
    """
    Rimuove solo una entry da gold_standard,
    lasciando intatta la web_resource associata.
    """

    parser = find_parser(request.url)

    if not parser:
        print(f"[WARNING] Dominio non riconosciuto: {request.url}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    try:
        deleted = repo_delete_gold_standard(request.url)

        if not deleted:
            print(f"[WARNING] URL non presente nel Gold Standard: {request.url}")
            raise HTTPException(
                status_code=404,
                detail="URL non presente nel Gold Standard"
            )

        return StatusResponse(status="ok")

    except HTTPException:
        raise

    except Exception as e:
        print(f"[ERROR] Errore durante delete_gold_standard: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante la rimozione del gold standard"
        )
    
    

@app.get("/db_schema")
async def get_db_schema():
    """
    Restituisce lo schema del database.
    """
    try:
        return repo_db_schema()
    except Exception as e:
        print(f"[ERROR] Errore durante il recupero dello schema DB: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero dello schema DB"
        )


@app.get("/db_stats")
async def get_db_stats():
    """
    Restituisce statistiche generali sui dati salvati nel database.
    """
    try:
        return repo_db_stats()
    except Exception as e:
        print(f"[ERROR] Errore durante il recupero delle statistiche DB: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero delle statistiche DB"
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
    if "en.wikipedia.org" in url:
        return base_dir / "gs_data" / "wikipedia_org"/ "gs.json"
    elif "www.ilpost.it" in url:
        return base_dir / "gs_data" / "ilpost_it" / "gs.json"
    elif "www.statmuse.com" in url:
        return base_dir / "gs_data" / "statmuse_com" / "gs.json"
    elif "eur-lex.europa.eu" in url:
        return base_dir / "gs_data" / "eurlex_europa_eu" / "gs.json"
    else:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        return None

def get_domain_from_url(url: str) -> str:
    """
    Ricava il dominio supportato a partire dall'URL.
    """
    if "wikipedia.org" in url:
        return "en.wikipedia.org"
    elif "ilpost.it" in url:
        return "www.ilpost.it"
    elif "statmuse.com" in url:
        return "www.statmuse.com"
    elif "eur-lex.europa.eu" in url:
        return "eur-lex.europa.eu"
    else:
        return ""
