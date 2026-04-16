from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()
templates = Jinja2Templates(directory="../templates")

API_BASE_URL = "http://localhost:8000"

def find_path_parser(url: str,base_dir: Path) -> Optional[Any]:
    """
    Restituisce il parser e il percorso del file JSON corrispondente al dominio dell'URL.
    """
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
	
@dataclass
class UiResult:
	url: str = ""
	domain: str = ""
	title: str = ""
	html_text: str = ""
	parsed_text: str = ""
	gold_text: str = ""


def create_app() -> FastAPI:

	@app.get("/", response_class=HTMLResponse)
	async def index(request: Request) -> HTMLResponse:
		gs_urls = fetch_gs_urls()
		return templates.TemplateResponse(
			"index.html",
			{
				"request": request,
				"gs_urls": gs_urls,
				"selected_url": "",
				"result": UiResult(),
				"metrics": {},
			},
		)

	@app.post("/", response_class=HTMLResponse)
	async def run_parse(
		request: Request,
		url: str = Form(default=""),
		gs_url: str = Form(default=""),
	) -> HTMLResponse:
		selected_url = url or gs_url or ""

		# TODO: completare con gestione errori e validazione input
		result = UiResult(url=selected_url)
		metrics: Dict[str, str] = {}

		if selected_url:
			# TODO: chiamare il backend /parse e /gold_standard
			# parse_data = call_backend("/parse", {"url": selected_url})
			# gold_data = call_backend("/gold_standard", {"url": selected_url})
			# metrics_data = call_backend("/evaluate", json_payload={"parsed_text": ..., "gold_standard": ...})
			# result = UiResult(
			# 	url=parse_data["url"],
			# 	domain=parse_data["domain"],
			# 	title=parse_data["title"],
			# 	html_text=parse_data["html_text"],
			# 	parsed_text=parse_data["parsed_text"],
			# 	gold_text=gold_data["gold_text"],
			# )
			# metrics = metrics_data["metrics"]["token_level_eval"]
			pass

		gs_urls = fetch_gs_urls()
		return templates.TemplateResponse(
			"index.html",
			{
				"request": request,
				"gs_urls": gs_urls,
				"selected_url": selected_url,
				"result": result,
				"metrics": metrics,
			},
		)

	return app


def fetch_gs_urls() -> List[str]:
	"""
	Recupera la lista degli URL del Gold Standard.
	TODO: collegare la funzione all'endpoint /domains o /full_gold_standard.
	"""
	# TODO: sostituire con chiamata reale al backend.
	urls = []
	try:
		response = requests.get(f"{API_BASE_URL}/domains")
		response.raise_for_status()
		domini = response.json()['domains']
		script_dir = Path(__file__).parent.resolve()
		base_dir = script_dir.parent.parent
		for dominio in domini:
			json_path = find_path_parser(dominio,base_dir)
			with open(json_path, 'r', encoding='utf-8') as f:
				domains_data = json.load(f)
			
			for entry in domains_data:
				urls.append(entry['url'])
	except requests.RequestException as e:
		domini = []
		print(f"[ERROR] Impossibile recuperare i domini: {e}")

	return []


def call_backend(endpoint: str, params: Optional[Dict[str, str]] = None, json_payload: Optional[Dict] = None) -> Dict:
	"""
	Helper per invocare il backend FastAPI.
	TODO: gestire timeout, errori e status code.
	"""
	url = f"{API_BASE_URL}{endpoint}"
	response = requests.get(url, params=params, timeout=20) if json_payload is None else requests.post(url, json=json_payload, timeout=20)
	response.raise_for_status()
	return response.json()


app = create_app()


if __name__ == "__main__":
	print(fetch_gs_urls())
	"""import uvicorn

	# Avvia il frontend su porta 8004 (allineato alle specifiche del corso)
	uvicorn.run("frontend:app", host="0.0.0.0", port=8004, reload=True)"""

