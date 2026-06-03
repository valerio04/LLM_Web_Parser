from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List, Any
from pathlib import Path
import json
import os
import urllib.request
import urllib.parse

from .evaluation import *
from .parsers.parser1 import IlPostParser
from .parsers.parser2 import StatMuseParser
from .parsers.parser3 import EurLexParser
from .parsers.parser_wikipedia import WikipediaParser

from .db.connection import get_connection
from .db.repository import db_schema as repo_db_schema
from .db.repository import db_stats as repo_db_stats
from .db.repository import get_web_resource as repo_get_web_resource
from .db.repository import get_gold_standard as repo_get_gold_standard
from .db.repository import list_gold_standard_urls as repo_list_gold_standard_urls
from .db.repository import add_web_resource as repo_add_web_resource
from .db.repository import add_gold_standard as repo_add_gold_standard
from .db.repository import delete_web_resource as repo_delete_web_resource
from .db.repository import delete_gold_standard as repo_delete_gold_standard
from .db.repository import add_parsed_document as repo_add_parsed_document
from .db.repository import add_evaluation as repo_add_evaluation
from .db.repository import add_llm_judgement as repo_add_llm_judgement
from .ollama.judge import evaluate_with_ollama

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
    url: Optional[str] = None
    parsed_document_id: Optional[int] = None

class EvaluateResponse(BaseModel):
    token_level_eval: Dict[str, float]
    x_eval: Dict[str, Any] = {}

class JudgeRequest(BaseModel):
    parsed_text: str
    gold_text: str
    url: Optional[str] = None
    parsed_document_id: Optional[int] = None


class JudgeResponse(BaseModel):
    model_name: str
    judge_score: int
    judge_feedback: str
    extra_info: Dict[str, Any] = {}

class FullGsEvalResponse(BaseModel):
    token_level_eval: Dict[str, float]
    judge_score: float
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

class StatusSystemResponse(BaseModel):
    backend: str
    database: str
    ollama: str



# Endpoint

@app.post("/parse")
async def parse_document(parse_request: ParseRequest) -> ParseResponse:
    """
    Esegue il parser per un documento.

    Se local=True:
    - legge html_text dal DB usando l'URL
    - non scarica la pagina online
    - carica i risultai nel DB (web_resource e parsed_document)

    Se local=False:
    - scarica la pagina online
    - carica i risultai nel DB (web_resource e parsed_document)
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

        
        try:
            #salvo il risultato del parsing nel db
            repo_add_web_resource(
                url=result["url"],
                domain=result["domain"],
                title=result["title"],
                html_text=result["html_text"]
            )

            repo_add_parsed_document(
                url=result["url"],
                parsed_text=result["parsed_text"],
                parser_name=parser.__class__.__name__
            )
        except Exception as e:
            print(f"[WARNING] Impossibile salvare risultato parsing nel DB: {e}")

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





#da capire se lasciare cosi o se prendere i dati dal db
@app.get("/domains")
async def get_domains() -> DomainsResponse:
    """
    Restituisce la lista dei domini supportati dal sistema.
    Parametri: nessuno.
    Ritorna: oggetto JSON con la lista dei domini.
    """

    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent

    # Percorso normale, quando domains.json è copiato/montato dentro /app
    json_path = base_dir / "domains.json"

    # Fallback utile se nel docker-compose è montato ./domains.json:/domains.json
    if not json_path.exists():
        json_path = Path("/domains.json")

    if not json_path.exists():
        print(f"[WARNING] File domains.json non trovato: {json_path}")
        raise HTTPException(
            status_code=500,
            detail="File domains.json non trovato"
        )

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            domains_data = json.load(f)

        return DomainsResponse(
            domains=domains_data.get("domains", [])
        )

    except Exception as e:
        print(f"[ERROR] Errore durante la lettura di domains.json: {e}")
        raise HTTPException(
            status_code=500,
            detail="Errore durante la lettura di domains.json"
        )



@app.get("/gold_standard")
async def get_gold_standard(url: str) -> GoldStandardResponse:
    """
    Restituisce il gold standard per un documento leggendo dal DB.
    Parametri: URL
    Ritorna: URL, dominio, titolo, HTML grezzo, gold_text
    """


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
    

    if not is_supported_domain(domain):
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
    Se viene passato url, salva anche le metriche nel DB.
    """

    token_level_eval = Evaluator.token_level_eval(
        request.parsed_text,
        request.gold_text
    )

    x_eval = Evaluator.x_eval_fast(
        request.parsed_text,
        request.gold_text
    )

    if request.url:
        try:
            repo_add_evaluation(
                url=request.url,
                token_level_eval=token_level_eval,
                x_eval=x_eval,
                parsed_document_id=request.parsed_document_id
            )
        except Exception as e:
            print(f"[WARNING] Impossibile salvare evaluation nel DB: {e}")

    return EvaluateResponse(
        token_level_eval=token_level_eval,
        x_eval=x_eval
    )


@app.post("/evaluate_judge")
async def evaluate_judge(request: JudgeRequest) -> JudgeResponse:
    """
    Valuta il testo parsato rispetto al gold standard usando LLM-as-Judge.
    Se viene passato url e l'URL esiste nel DB, salva il giudizio nel DB.
    """

    result = evaluate_with_ollama(
        parsed_text=request.parsed_text,
        gold_text=request.gold_text
    )

    if request.url:
        web_resource = repo_get_web_resource(request.url)

        if web_resource:
            try:
                repo_add_llm_judgement(
                    url=request.url,
                    parsed_document_id=request.parsed_document_id,
                    model_name=result["model_name"],
                    judge_score=result["judge_score"],
                    judge_feedback=result["judge_feedback"],
                    extra_info=result.get("extra_info", {})
                )
            except Exception as e:
                print(f"[WARNING] Impossibile salvare llm_judgement nel DB: {e}")
        else:
            print(f"[WARNING] Judge non salvato: URL non presente in web_resources: {request.url}")

    return JudgeResponse(
        model_name=result["model_name"],
        judge_score=result["judge_score"],
        judge_feedback=result["judge_feedback"],
        extra_info=result.get("extra_info", {})
    )





@app.get("/full_gs_eval")
async def get_full_gs_eval(domain: str) -> FullGsEvalResponse:
    """
    Esegue l'eval su tutto il GS di un dominio usando HTML e gold_text dal DB.
    Salva parsed_documents, evaluations e llm_judgements nel DB.
    Usa x_eval_fast, token_level_eval, evaluate_with_ollama.
    """

    if not is_supported_domain(domain):
        print(f"[WARNING] Dominio non riconosciuto: {domain}")
        raise HTTPException(status_code=400, detail="Dominio non supportato")

    urls = repo_list_gold_standard_urls(domain)

    if not urls:
        raise HTTPException(
            status_code=404,
            detail="Nessun Gold Standard trovato per questo dominio"
        )

    data = {
        "precision": [],
        "recall": [],
        "f1": [],
        "judge_score": [],
        "cosine_similarity": [],
        "boilerplate_ratio_extracted": [],
        "boilerplate_fidelity": [],
    }

    for url in urls:
        try:
            entry = repo_get_gold_standard(url)

            if not entry:
                print(f"[WARNING] Entry GS non trovata nel DB: {url}")
                continue

            parser = find_parser(url)

            if not parser:
                print(f"[WARNING] Parser non trovato per: {url}")
                continue

            parsed_result = await parser.run_from_html(
                url,
                entry["html_text"]
            )

            parsed_text = parsed_result.get("parsed_text", "").strip()

            if not parsed_text:
                print(f"[WARNING] parsed_text vuoto per: {url}")
                continue

            parsed_document_id = None

            try:
                parsed_document_id = repo_add_parsed_document(
                    url=url,
                    parsed_text=parsed_text,
                    parser_name=parser.__class__.__name__
                )
            except Exception as e:
                print(f"[WARNING] Impossibile salvare parsed_document per {url}: {e}")

            token_level_eval = Evaluator.token_level_eval(
                parsed_text,
                entry["gold_text"]
            )

            x_eval = Evaluator.x_eval_fast(
                parsed_text,
                entry["gold_text"]
            )

            #==================da togliere======
            '''
            judge_score = max(1, min(5, round(token_level_eval.get("f1", 0) * 5)))

            judge_result = {
                "model_name": "fast-fallback",
                "judge_score": judge_score,
                "judge_feedback": "Judge score stimato automaticamente da F1 per evitare timeout in full_gs_eval.",
                "extra_info": {
                    "source": "f1_fallback"
                }
            }
            '''
            #==============================
            
            
            #da rimettere mettere
            #=============================
            
            judge_result = evaluate_with_ollama(
                parsed_text=parsed_text,
                gold_text=entry["gold_text"]
            )
            #============================

            try:
                repo_add_evaluation(
                    url=url,
                    parsed_document_id=parsed_document_id,
                    token_level_eval=token_level_eval,
                    x_eval=x_eval
                )
            except Exception as e:
                print(f"[WARNING] Impossibile salvare evaluation per {url}: {e}")
            
            try:
                repo_add_llm_judgement(
                    url=url,
                    parsed_document_id=parsed_document_id,
                    model_name=judge_result["model_name"],
                    judge_score=judge_result["judge_score"],
                    judge_feedback=judge_result["judge_feedback"],
                    extra_info=judge_result.get("extra_info", {})
                )
            except Exception as e:
                print(f"[WARNING] Impossibile salvare llm_judgement per {url}: {e}")

            data["precision"].append(token_level_eval.get("precision", 0))
            data["recall"].append(token_level_eval.get("recall", 0))
            data["f1"].append(token_level_eval.get("f1", 0))

            judge_score = judge_result.get("judge_score", 0)
            if judge_score > 0:
                data["judge_score"].append(judge_score)

            data["cosine_similarity"].append(x_eval.get("cosine_similarity", 0))
            data["boilerplate_ratio_extracted"].append(
                x_eval.get("boilerplate_ratio_extracted", 0)
            )
            data["boilerplate_fidelity"].append(
                x_eval.get("boilerplate_fidelity", 0)
            )

        except Exception as e:
            print(f"[ERROR] Errore durante full_gs_eval per {url}: {e}")

    avg = lambda values: sum(values) / len(values) if values else 0.0

    return FullGsEvalResponse(
        token_level_eval={
            "precision": avg(data["precision"]),
            "recall": avg(data["recall"]),
            "f1": avg(data["f1"]),
        },
        judge_score=avg(data["judge_score"]),
        x_eval={
            "cosine_similarity": avg(data["cosine_similarity"]),
            "boilerplate_ratio_extracted": avg(data["boilerplate_ratio_extracted"]),
            "boilerplate_fidelity": avg(data["boilerplate_fidelity"]),
        }
    )

@app.post("/add_web_resource")
async def add_web_resource(request: AddWebResourceRequest) -> StatusResponse:
    """
    Aggiunge una risorsa web nella tabella web_resources.
    Input minimo: url, html_text.
    """

    
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
        return StatusResponse(status="error")



@app.delete("/web_resource")
async def delete_web_resource(request: DeleteByUrlRequest) -> StatusResponse:
    """
    Rimuove una risorsa web.
    Il gold_standard collegato viene rimosso a cascata tramite FK.
    """

   
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
        return StatusResponse(status="error")





@app.post("/add_gold_standard")
async def add_gold_standard(request: AddGoldStandardRequest) -> StatusResponse:
    """
    Aggiunge una entry nella tabella gold_standard.
    La web_resource corrispondente deve già esistere.
    """

   


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

    

    except Exception as e:
        print(f"[ERROR] Errore durante add_gold_standard: {e}")
        return StatusResponse(status="error")



@app.delete("/gold_standard")
async def delete_gold_standard(request: DeleteByUrlRequest) -> StatusResponse:
    """
    Rimuove solo una entry da gold_standard,
    lasciando intatta la web_resource associata.
    """

    


    try:
        deleted = repo_delete_gold_standard(request.url)

        if not deleted:
            print(f"[WARNING] URL non presente nel Gold Standard: {request.url}")
            return StatusResponse(status="error")


        return StatusResponse(status="ok")

    

    except Exception as e:
        print(f"[ERROR] Errore durante delete_gold_standard: {e}")
        return StatusResponse(status="error")
    
           
    


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

@app.get("/status")
async def get_status() -> StatusSystemResponse:
    """
    Restituisce lo stato dei componenti del sistema.
    L'endpoint risponde sempre HTTP 200.
    """

    return StatusSystemResponse(
        backend="ok",
        database=check_database_status(),
        ollama=check_ollama_status()
    )


# =================helper=====================

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
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc or url


def is_supported_domain(value: str) -> bool:
    """
    Controlla se una stringa contiene un dominio supportato.
    Funziona sia con URL completi sia con domini tipo www.ilpost.it.
    """
    return (
        "wikipedia.org" in value
        or "ilpost.it" in value
        or "statmuse.com" in value
        or "eur-lex.europa.eu" in value
    )

def check_database_status() -> str:
    """
    Controlla se il database è raggiungibile.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1")
        cursor.fetchone()

        cursor.close()
        conn.close()

        return "ok"

    except Exception as e:
        print(f"[WARNING] Database non raggiungibile: {e}")
        return "error"


def check_ollama_status() -> str:
    """
    Controlla se Ollama è raggiungibile.
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        url = f"{ollama_url}/api/tags"

        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                return "ok"

        return "error"

    except Exception as e:
        print(f"[WARNING] Ollama non raggiungibile: {e}")
        return "error"