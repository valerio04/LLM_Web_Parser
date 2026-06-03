"""
Modulo frontend dell'applicazione Minerva Parser.

Questo modulo implementa un server FastAPI che funge da interfaccia web
per la pipeline di parsing e valutazione. Utilizza Jinja2 per il templating
server-side e comunica esclusivamente con il backend tramite le sue API REST.

Pagine disponibili:
    - /           → Home (matricole, stato sistema, domini supportati)
    - /pipeline   → Parser & Evaluation (parsing, metriche, LLM Judge)
    - /gsbuilder  → Gold Standard Builder (aggiunta/rimozione entry nel GS)
    - /stats      → Statistiche e schema del database

Porte:
    - Frontend: 8004
    - Backend (target API): 8003 (configurabile via variabile d'ambiente BACKEND_URL)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests as http_client

app = FastAPI()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8003")

_templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@dataclass
class ParseResult:
    """Contiene i risultati del parsing di un documento web."""

    url: str = ""
    domain: str = ""
    title: str = ""
    html_text: str = ""
    parsed_text: str = ""
    gold_text: str = ""
    error_message: str = ""


# Le metriche di valutazione vengono passate al template come dict semplice
# per massima compatibilità con l'accesso Jinja2 tramite metrics["key"].


@dataclass
class JudgeResult:
    """Contiene il risultato della valutazione LLM-as-Judge."""

    model_name: str = ""
    judge_score: int = 0
    judge_feedback: str = ""


# ─────────────────────── Helper: chiamata al backend ───────────────────────


def call_backend(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, str]] = None,
    json_payload: Optional[Dict[str, Any]] = None,
    timeout: int = 400,
) -> Dict[str, Any]:
    """
    Effettua una chiamata HTTP al backend e restituisce la risposta JSON.

    Parametri:
        endpoint: percorso dell'API (es. '/domains', '/parse').
        method: metodo HTTP ('GET', 'POST', 'DELETE').
        params: parametri query string per le richieste GET.
        json_payload: corpo JSON per le richieste POST.
        timeout: timeout in secondi per la connessione al backend.

    Ritorna:
        Dizionario con la risposta JSON del backend.

    Errori:
        Rilancia requests.RequestException se il backend non è raggiungibile
        o restituisce un errore HTTP.
    """
    url = f"{BACKEND_URL}{endpoint}"
    resp = http_client.request(
        method=method,
        url=url,
        params=params,
        json=json_payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def safe_call(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, str]] = None,
    json_payload: Optional[Dict[str, Any]] = None,
    default: Any = None,
) -> Any:
    """
    Versione sicura di call_backend che non lancia eccezioni.

    Se la chiamata al backend fallisce, restituisce il valore di default
    senza interrompere il rendering della pagina.

    Parametri:
        endpoint: percorso dell'API REST.
        method: metodo HTTP.
        params: parametri query string.
        json_payload: corpo JSON.
        default: valore da restituire in caso di errore.

    Ritorna:
        La risposta JSON del backend oppure il valore di default.
    """
    try:
        return call_backend(endpoint, method, params, json_payload)
    except Exception as e:
        print(f"[WARNING] Chiamata a {endpoint} fallita: {e}")
        return default if default is not None else {}


def get_domains() -> List[str]:
    """
    Recupera la lista dei domini supportati dal backend.

    Ritorna:
        Lista di stringhe con i nomi dei domini (es. ['www.ilpost.it', ...]).
    """
    data = safe_call("/domains", default={"domains": []})
    return data.get("domains", [])


def get_gs_urls(domain: str) -> List[str]:
    """
    Recupera gli URL del Gold Standard disponibili per un dominio.

    Parametri:
        domain: nome del dominio (es. 'www.ilpost.it').

    Ritorna:
        Lista di URL presenti nel Gold Standard per quel dominio.
    """
    data = safe_call(
        "/gold_standard_urls",
        params={"domain": domain},
        default={"gold_standard_urls": []},
    )
    return data.get("gold_standard_urls", [])


def get_all_gs_urls(domains: List[str]) -> Dict[str, List[str]]:
    """
    Costruisce una mappa dominio → lista URL del Gold Standard.

    Chiamata una volta per ogni caricamento della pagina Pipeline o GS Builder,
    fornisce a Jinja2 tutti i dati necessari per popolare i select a tendina
    e al JavaScript client-side per il filtraggio dinamico dominio → URL.

    Parametri:
        domains: lista dei domini supportati.

    Ritorna:
        Dizionario con chiave dominio e valore lista URL.
    """
    result: Dict[str, List[str]] = {}
    for domain in domains:
        result[domain] = get_gs_urls(domain)
    return result


# ─────────────────────── Pagine ───────────────────────


@app.get("/", response_class=HTMLResponse)
def page_home(request: Request) -> HTMLResponse:
    """
    Pagina Home: matricole del gruppo, stato del sistema e domini supportati.

    Chiama GET /status e GET /domains dal backend per popolare il template
    con le informazioni sullo stato dei componenti e la lista dei domini.
    """
    domains = get_domains()
    status = safe_call("/status", default={"backend": "error", "database": "error", "ollama": "error"})

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "active_page": "home",
            "domains": domains,
            "status": status,
            "matricole": ["2107313", "2104581", "2128730"],
        },
    )


@app.get("/pipeline", response_class=HTMLResponse)
def page_pipeline(request: Request) -> HTMLResponse:
    """
    Pagina Pipeline (GET): mostra il form per selezionare un URL e avviare il parsing.

    Carica i domini e i rispettivi URL del Gold Standard per popolare
    i menu a tendina del form.
    """
    domains = get_domains()
    gs_urls_map = get_all_gs_urls(domains)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "active_page": "pipeline",
            "domains": domains,
            "gs_urls_map": gs_urls_map,
            "result": None,
            "metrics": None,
            "judge": None,
            "selected_domain": "",
            "selected_url": "",
            "is_local": True,
            "error_message": "",
        },
    )


@app.post("/pipeline", response_class=HTMLResponse)
def pipeline_action(
    request: Request,
    action: str = Form(default="parse"),
    url: str = Form(default=""),
    domain: str = Form(default=""),
    is_local: str = Form(default="true"),
    prev_parsed_text: str = Form(default=""),
    prev_gold_text: str = Form(default=""),
    prev_html_text: str = Form(default=""),
    prev_domain: str = Form(default=""),
    prev_title: str = Form(default=""),
    prev_url: str = Form(default=""),
) -> HTMLResponse:
    """
    Pagina Pipeline (POST): gestisce le azioni parse, evaluate e judge.

    In base al campo nascosto 'action' del form, esegue:
    - 'parse': chiama POST /parse e GET /gold_standard dal backend.
    - 'evaluate': chiama POST /evaluate con parsed_text e gold_text.
    - 'judge': chiama POST /evaluate_judge con parsed_text e gold_text.

    I risultati precedenti vengono preservati tramite campi hidden nel form
    per evitare di dover rifare il parsing ad ogni azione.

    Parametri:
        action: tipo di azione ('parse', 'evaluate', 'judge').
        url: URL da parsare o su cui eseguire l'evaluation.
        domain: dominio selezionato nel form.
        is_local: 'true' per parsing locale, 'false' per parsing live.
        prev_*: campi hidden con i risultati del parsing precedente.
    """
    domains = get_domains()
    gs_urls_map = get_all_gs_urls(domains)
    local_mode = is_local.lower() == "true"

    result = None
    metrics = None
    judge = None
    error_message = ""

    if action == "parse":
        selected_url = url.strip()
        if not selected_url:
            error_message = "Inserisci o seleziona un URL."
        else:
            try:
                parse_data = call_backend(
                    "/parse",
                    method="POST",
                    json_payload={"url": selected_url, "local": local_mode},
                )
                result = ParseResult(
                    url=parse_data.get("url", selected_url),
                    domain=parse_data.get("domain", ""),
                    title=parse_data.get("title", ""),
                    html_text=parse_data.get("html_text", ""),
                    parsed_text=parse_data.get("parsed_text", ""),
                )

                try:
                    gs_data = call_backend(
                        "/gold_standard",
                        params={"url": selected_url},
                    )
                    result.gold_text = gs_data.get("gold_text", "")
                except http_client.RequestException:
                    result.gold_text = ""

            except http_client.RequestException as e:
                error_message = _extract_error(e)

    elif action == "evaluate":
        result = ParseResult(
            url=prev_url,
            domain=prev_domain,
            title=prev_title,
            html_text=prev_html_text,
            parsed_text=prev_parsed_text,
            gold_text=prev_gold_text,
        )

        if prev_parsed_text and prev_gold_text:
            try:
                eval_data = call_backend(
                    "/evaluate",
                    method="POST",
                    json_payload={
                        "parsed_text": prev_parsed_text,
                        "gold_text": prev_gold_text,
                        "url": prev_url,
                    },
                )
                token = eval_data.get("token_level_eval", {})
                x_eval = eval_data.get("x_eval", {})
                metrics = {
                    "precision": token.get("precision", 0),
                    "recall": token.get("recall", 0),
                    "f1": token.get("f1", 0),
                    "levenshtein": x_eval.get("levenshtein"),
                    "rouge_l": x_eval.get("rouge_l"),
                    "cosine_similarity": x_eval.get("cosine_similarity"),
                    "boilerplate_ratio_extracted": x_eval.get("boilerplate_ratio_extracted"),
                    "boilerplate_fidelity": x_eval.get("boilerplate_fidelity"),
                }
            except http_client.RequestException as e:
                error_message = "Errore evaluation: " + _extract_error(e)
        else:
            error_message = "Testo parsato o Gold Standard mancante per l'evaluation."

    elif action == "judge":
        result = ParseResult(
            url=prev_url,
            domain=prev_domain,
            title=prev_title,
            html_text=prev_html_text,
            parsed_text=prev_parsed_text,
            gold_text=prev_gold_text,
        )

        if prev_parsed_text and prev_gold_text:
            try:
                judge_data = call_backend(
                    "/evaluate_judge",
                    method="POST",
                    json_payload={
                        "parsed_text": prev_parsed_text,
                        "gold_text": prev_gold_text,
                        "url": prev_url,
                    },
                )
                judge = JudgeResult(
                    model_name=judge_data.get("model_name", ""),
                    judge_score=judge_data.get("judge_score", 0),
                    judge_feedback=judge_data.get("judge_feedback", ""),
                )
            except http_client.RequestException as e:
                error_message = "Errore LLM Judge: " + _extract_error(e)
        else:
            error_message = "Testo parsato o Gold Standard mancante per il Judge."

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "active_page": "pipeline",
            "domains": domains,
            "gs_urls_map": gs_urls_map,
            "result": result,
            "metrics": metrics,
            "judge": judge,
            "selected_domain": domain,
            "selected_url": url.strip(),
            "is_local": local_mode,
            "error_message": error_message,
        },
    )


@app.get("/gsbuilder", response_class=HTMLResponse)
def page_gsbuilder(request: Request) -> HTMLResponse:
    """
    Pagina Gold Standard Builder (GET): mostra il form per aggiungere
    o rimuovere entry dal Gold Standard nel database.

    Carica i domini supportati e, per ciascuno, la lista degli URL
    già presenti nel Gold Standard.
    """
    domains = get_domains()
    gs_urls_map = get_all_gs_urls(domains)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "active_page": "gsbuilder",
            "domains": domains,
            "gs_urls_map": gs_urls_map,
            "gs_downloaded_html": "",
            "gs_download_url": "",
            "gs_message": "",
            "gs_error": "",
            "gs_selected_domain": "",
        },
    )


@app.post("/gsbuilder", response_class=HTMLResponse)
def gsbuilder_action(
    request: Request,
    action: str = Form(default=""),
    gs_domain: str = Form(default=""),
    gs_url: str = Form(default=""),
    gs_goldtext: str = Form(default=""),
    gs_html: str = Form(default=""),
    gs_delete_url: str = Form(default=""),
) -> HTMLResponse:
    """
    Pagina Gold Standard Builder (POST): gestisce le azioni di download HTML,
    salvataggio entry e rimozione entry dal Gold Standard.

    In base al campo 'action':
    - 'download': chiama POST /parse per scaricare l'HTML della pagina.
    - 'save': chiama POST /add_web_resource e POST /add_gold_standard.
    - 'delete': chiama DELETE /gold_standard per rimuovere un'entry.

    Parametri:
        action: tipo di azione ('download', 'save', 'delete').
        gs_domain: dominio selezionato.
        gs_url: URL della pagina web.
        gs_goldtext: testo gold inserito dall'utente.
        gs_html: HTML scaricato precedentemente (campo hidden).
        gs_delete_url: URL dell'entry da eliminare.
    """
    domains = get_domains()
    gs_urls_map = get_all_gs_urls(domains)

    downloaded_html = ""
    download_url = ""
    message = ""
    error = ""

    if action == "download":
        url_input = gs_url.strip()
        if not url_input:
            error = "Inserisci un URL."
        else:
            try:
                data = call_backend(
                    "/parse",
                    method="POST",
                    json_payload={"url": url_input, "local": False},
                )
                downloaded_html = data.get("html_text", "")
                download_url = url_input
                message = "HTML scaricato con successo!"
            except http_client.RequestException as e:
                error = "Errore download HTML: " + _extract_error(e)

    elif action == "save":
        url_input = gs_url.strip()
        gold_text_input = gs_goldtext.strip()
        html_input = gs_html

        if not url_input:
            error = "Inserisci un URL."
        elif not gold_text_input:
            error = "Inserisci il gold text."
        elif not html_input:
            error = "Scarica prima l'HTML della pagina."
        else:
            try:
                call_backend(
                    "/add_web_resource",
                    method="POST",
                    json_payload={"url": url_input, "html_text": html_input},
                )
                call_backend(
                    "/add_gold_standard",
                    method="POST",
                    json_payload={"url": url_input, "gold_text": gold_text_input},
                )
                message = "Gold Standard salvato con successo!"
                gs_urls_map = get_all_gs_urls(domains)
            except http_client.RequestException as e:
                error = "Errore salvataggio: " + _extract_error(e)

    elif action == "delete":
        delete_url_input = gs_delete_url.strip()
        if delete_url_input:
            try:
                call_backend(
                    "/gold_standard",
                    method="DELETE",
                    json_payload={"url": delete_url_input},
                )
                message = "Entry rimossa con successo!"
                gs_urls_map = get_all_gs_urls(domains)
            except http_client.RequestException as e:
                error = "Errore rimozione: " + _extract_error(e)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "active_page": "gsbuilder",
            "domains": domains,
            "gs_urls_map": gs_urls_map,
            "gs_downloaded_html": downloaded_html,
            "gs_download_url": download_url,
            "gs_message": message,
            "gs_error": error,
            "gs_selected_domain": gs_domain,
        },
    )


@app.get("/stats", response_class=HTMLResponse)
def page_stats(request: Request) -> HTMLResponse:
    """
    Pagina Statistiche: mostra le statistiche aggregate del database
    e lo schema delle tabelle.

    Chiama GET /db_stats e GET /db_schema dal backend e passa i dati
    direttamente al template Jinja2 per la renderizzazione.
    """
    db_stats = safe_call("/db_stats", default={})
    db_schema = safe_call("/db_schema", default={})

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "active_page": "stats",
            "db_stats": db_stats,
            "db_schema": db_schema,
        },
    )


# ─────────────────────── Utility ───────────────────────


def _extract_error(exc: http_client.RequestException) -> str:
    """
    Estrae un messaggio di errore leggibile da un'eccezione HTTP.

    Tenta di leggere il campo 'detail' dalla risposta JSON del backend.
    Se non è possibile, restituisce una stringa generica con il tipo di errore.

    Parametri:
        exc: eccezione sollevata dalla libreria requests.

    Ritorna:
        Stringa con il messaggio di errore.
    """
    if hasattr(exc, "response") and exc.response is not None:
        try:
            return exc.response.json().get("detail", str(exc))
        except Exception:
            pass
    return "Errore di connessione al backend."
