"""
Modulo frontend dell'applicazione Minerva Parser.

Questo modulo implementa un server FastAPI che funge da:
1. Server web per servire la pagina HTML principale tramite Jinja2.
2. Reverse proxy per inoltrare le chiamate API al backend,
   evitando problemi di CORS lato browser.

Porte:
    - Frontend: 8004
    - Backend (target proxy): 8003 (configurabile via variabile d'ambiente BACKEND_URL)
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import requests as http_client

app = FastAPI()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8003")

_templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@app.get("/", response_class=HTMLResponse)
def serve_index(request: Request) -> HTMLResponse:
    """
    Serve la pagina principale dell'applicazione.

    Utilizza il template engine Jinja2 per renderizzare il file index.html
    contenuto nella cartella templates/.

    Parametri:
        request: oggetto Request di FastAPI, necessario per il rendering Jinja2.

    Ritorna:
        HTMLResponse con la pagina HTML renderizzata.
    """
    return templates.TemplateResponse(request, "index.html", {})


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_backend(path: str, request: Request) -> Response:
    """
    Reverse proxy che inoltra tutte le richieste /api/* al servizio backend.

    Il browser comunica solo con il frontend (stessa origine), eliminando
    la necessità di configurare CORS. Le richieste vengono inoltrate al backend
    preservando metodo HTTP, query parameters, body e Content-Type.

    Parametri:
        path: percorso relativo dopo /api/ (es. "parse", "domains", "db_stats").
        request: oggetto Request di FastAPI con i dati della richiesta originale.

    Ritorna:
        Response con il contenuto, lo status code e il Content-Type ricevuti dal backend.

    Errori:
        Se il backend non è raggiungibile, restituisce HTTP 502 con messaggio di errore JSON.
    """
    target_url = f"{BACKEND_URL}/{path}"
    params = dict(request.query_params)
    body = await request.body()

    headers = {}
    if body:
        headers["Content-Type"] = request.headers.get(
            "Content-Type", "application/json"
        )

    try:
        resp = http_client.request(
            method=request.method,
            url=target_url,
            params=params,
            data=body if body else None,
            headers=headers,
            timeout=400,
        )

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers={
                "Content-Type": resp.headers.get(
                    "Content-Type", "application/json"
                )
            },
        )

    except http_client.RequestException as e:
        error_msg = str(e).replace('"', '\\"')
        return Response(
            content=(
                '{"detail": "Errore di connessione al backend: '
                + error_msg
                + '"}'
            ),
            status_code=502,
            headers={"Content-Type": "application/json"},
        )
