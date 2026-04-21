from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Dict, List, Optional, Any  # <-- Aggiunto Any
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import markdown2
import re

app = FastAPI()
# Usa un percorso assoluto basato sulla locazione del file
_templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir)) 

API_BASE_URL = "http://backend:8003"

def find_path_parser(url: str, base_dir: Path) -> Optional[Any]:
    """
    Restituisce il parser e il percorso del file JSON corrispondente al dominio dell'URL.
    """
    if "wikipedia.org" in url:
        return base_dir / "gs_data" / "wikipedia_org" / "gs.json"
    elif "ilpost.it" in url:
        return base_dir / "gs_data" / "ilpost_it" / "gs.json"
    elif "statmuse.com" in url:
        return base_dir / "gs_data" / "statmuse_com" / "gs.json"
    elif "eur-lex.europa.eu" in url:
        return base_dir / "gs_data" / "eurlex_europa_eu" / "gs.json"
    else:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        return None

@dataclass
class UiResult:
    url: str = ""
    domain: str = ""
    title: str = ""
    html_text: str = ""
    parsed_text: str = ""
    gold_text: str = ""
    error_message: str = ""

# --- ROTTE SPOSTATE FUORI DA create_app() e rimosso 'async' ---

@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    gs_urls = fetch_gs_urls()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "gs_urls": gs_urls,
            "selected_url": "",
            "result": UiResult(),
            "metrics": {},
        },
    )

# TODO: oltre all if selected url, aggiungi and seected_url in gs_urls, vedi se ha senso 
@app.post("/", response_class=HTMLResponse)
def run_parse(request: Request, url: str = Form(default=""), gs_url: str = Form(default="")) -> HTMLResponse:
    selected_url = url or gs_url or "" 
    
    result = UiResult(url=selected_url)
    metrics: Dict[str, str] = {}
    gs_urls = fetch_gs_urls()

    if selected_url:
        try:
            parse_data = call_backend("/parse", {"url": selected_url})
            
            gold_data = {}
            metrics_data = {}
            
            try:
                gold_data = call_backend("/gold_standard", {"url": selected_url})
            except requests.RequestException as e:
                print(f"[INFO] Nessun Gold Standard trovato per questo URL: {e}")
            
            
            parsed_text = parse_data.get("parsed_text", "")
            gold_text = gold_data.get("gold_text", "")
          
            
			
            if gold_text:
                try:
                    metrics_data = call_backend(
                        "/evaluate", 
                        json_payload={"parsed_text": parsed_text, "gold_text": gold_text}
                    )
                except requests.RequestException as e:
                    print(f"[ERROR] Errore durante l'evaluation: {e}")

			# TODO: non so se il prof vuole il md o il testo pulito nell intefaccia
			
			#html_text = markdown2.markdown(parse_data.get("parsed_text", ""))
            #plain_text = (re.sub(r'<[^>]+>', '', html_text)).strip()
            result = UiResult(
                url=parse_data.get("url", selected_url),
                domain=parse_data.get("domain", ""),
                title=parse_data.get("title", ""),
                html_text=parse_data.get("html_text", ""),
                #parsed_text=plain_text,
                parsed_text=parse_data.get("parsed_text", ""),
                gold_text=gold_data.get("gold_text", ""),
            )
            metrics = metrics_data.get("token_level_eval", {})
            
        except requests.RequestException as e:
            # Gestione base dell'errore per il parsing
            print(f"[ERROR] Errore durante il parsing dal backend: {e}")
            
            error_details = "Errore di connessione."
            if hasattr(e, 'response') and e.response is not None:
                try:
                    # Legge proprio il campo "detail" che hai impostato nel backend!
                    error_details = e.response.json().get("detail", str(e))
                except Exception:
                    pass
                    
            result.error_message = error_details

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "gs_urls": gs_urls,
            "selected_url": selected_url,
            "result": result,
            "metrics": metrics,
        },
    )

# -------------------------------------------------------------

def fetch_gs_urls() -> List[str]:
    urls = []
    try:
        response = requests.get(f"{API_BASE_URL}/domains")
        response.raise_for_status() 
        domini = response.json().get('domains', [])
        
        script_dir = Path(__file__).parent.resolve()
        base_dir = script_dir.parent.parent
        
        for dominio in domini:
            json_path = find_path_parser(dominio, base_dir)
            if json_path and json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    domains_data = json.load(f)
                for entry in domains_data:
                    urls.append(entry.get('url'))
            else:
                print(f"[WARNING] File non trovato: {json_path}")
                
    except requests.RequestException as e:
        print(f"[ERROR] Impossibile recuperare i domini: {e}")
    except json.JSONDecodeError:
        print("[ERROR] Errore nel decoding del JSON locale.")

    return urls

def call_backend(endpoint: str, params: Optional[Dict[str, str]] = None, json_payload: Optional[Dict] = None) -> Dict:
    url = f"{API_BASE_URL}{endpoint}"
    if json_payload is None:
        response = requests.get(url, params=params)
    else:
        response = requests.post(url, json=json_payload)
    
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    import uvicorn
    # Assicurati che il nome del file Python corrisponda a "frontend" in "frontend:app"
    # TODO: ricontrolla
    uvicorn.run("src.frontend:app", host="0.0.0.0", port=8004)