from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Dict, List, Optional, Any  # <-- Aggiunto Any
from pathlib import Path

from bs4 import BeautifulSoup
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import mistune
import requests
import markdown2
import re

app = FastAPI()
# Usa un percorso assoluto basato sulla locazione del file
_templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir)) 

API_BASE_URL = "http://backend:8003"

def find_path(url: str) -> Optional[Any]:
    """
    Restituisce il percorso del file JSON corrispondente al dominio dell'URL.
    """
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
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
            "x_metrics": {},
        },
    )

@app.post("/", response_class=HTMLResponse)
def run_parse(request: Request, url: str = Form(default=""), gs_url: str = Form(default="")) -> HTMLResponse:
    """
    Esegue il parsing dell'URL selezionato, recupera il gold standard associato e calcola le metriche di valutazione.
    restituisce una pagina HTML con i risultati.
    """
    selected_url = url or gs_url or "" 
    
    result = UiResult(url=selected_url)
    metrics: Dict[str, str] = {}
    x_metrics: Dict[str, str] = {}  
    gs_urls = fetch_gs_urls()

    if selected_url:
        try:
            # cerca il percorso di progetto
            script_dir = Path(__file__).parent.resolve()
            base_dir = script_dir.parent.parent
            local_html = None

            # cerca il percorso associato all'url selezionato
            json_path = find_path(selected_url)

            try:
                # se il percorso e il file JSON esistono carica il contenuto
                if json_path and json_path.exists():
                    with open(json_path, 'r', encoding='utf-8') as f:
                        entries = json.load(f)

                    # cerca nel contenuto caricato se trova una entry con lo stesso url di quello selezionato.
                    # Qui tentiamo di caricare il file HTML associato all'URL (se presente nel GS)
                    for entry in entries:
                        if entry.get('url') == selected_url and entry.get('html_file'):
                            html_file_path = base_dir / 'gs_data' / entry.get('html_file')
                            if html_file_path.exists():
                                with open(html_file_path, 'r', encoding='utf-8') as hf:
                                    local_html = hf.read()
                            break
            except Exception:
                # se qualcosa fallisce, continueremo con il parsing online
                local_html = None

            if local_html is not None:
                # invia il payload al backend per usare run_from_html
                parse_data = call_backend("/parse", json_payload={"url": selected_url, "html_text": local_html})
            else:
                # fallback: parsing online
                parse_data = call_backend("/parse", {"url": selected_url})

            gold_data = {}
            metrics_data = {}
            
            # carico il gold standar dell'URL tramite la GET
            try:
                gold_data = call_backend("/gold_standard", {"url": selected_url})
            except requests.RequestException as e:
                print(f"[INFO] Nessun Gold Standard trovato per questo URL: {e}")
            
            parsed_text = parse_data.get("parsed_text", "")
            gold_text = gold_data.get("gold_text", "")
          
            # se esiste il gold_standard associato a quell'URL faccio l'evaluate
            if gold_text:
                try:
                    metrics_data = call_backend(
                        "/evaluate", 
                        json_payload={"parsed_text": parsed_text, "gold_text": gold_text}
                    )
                except requests.RequestException as e:
                    print(f"[ERROR] Errore durante l'evaluation: {e}")
            
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
            x_metrics = metrics_data.get("x_eval", {})

            
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
            "x_metrics": x_metrics,
        },
    )

# -------------------------------------------------------------

def fetch_gs_urls() -> List[str]:
    """
    Recupera la lista degli URL dei Gold Standard dai file JSON locali.
    Ritorna una lista di URL.
    """
    urls = []
    try:
        # fa una GET domains/ per ottenere tutti i domini supportati e li salva in una lista
        response = requests.get(f"{API_BASE_URL}/domains")
        response.raise_for_status() 
        domini = response.json().get('domains', [])
                
        for dominio in domini:
            # cerca il percorso del file JSON associato al dominio
            json_path = find_path(dominio)

            # se il percorso e il file JSON esistono carica il contenuto
            if json_path and json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    domains_data = json.load(f)

                # inserisci nella lista gli url presenti nel file JSON
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
    """
    Effettua una chiamata al backend, gestendo sia GET che POST a seconda della presenza di json_payload.
    Ritorna la risposta JSON come dizionario.
    """

    url = f"{API_BASE_URL}{endpoint}"
    if json_payload is None:
        response = requests.get(url, params=params)
    else:
        response = requests.post(url, json=json_payload)
    
    response.raise_for_status()
    return response.json()
