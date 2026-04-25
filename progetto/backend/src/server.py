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


# TODO: controllare i domini in server direttamente da qui

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
    
    # TODO: testare se questa eccezione viene catturata quando il parsing fallisce (es: url non esistente, timeout, ecc.)
    except Exception as e:
        print(f"[ERROR] Errore durante il parsing: {e}")
        raise HTTPException(status_code=500, detail="Errore durante il parsing")







@app.post("/parse")
async def parse_document_from_html(parse_request: ParseRequest) -> ParseResponse:
    """
    Esegue il parser per un documento di un dominio.
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
    
    # TODO: testare se questa eccezione viene catturata quando il parsing fallisce (es: url non esistente, timeout, ecc.)
    except Exception as e:
        print(f"[ERROR] Errore durante il parsing: {e}")
        raise HTTPException(status_code=500, detail="Errore durante il parsing")





















@app.get("/domains")
async def get_domains() -> DomainsResponse:
    """
    Restituisce la lista dei domini assegnati con i link associati.
    """
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
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
    """

    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
    json_path = find_path(url)
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
    """
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
    json_path = find_path(domain)
    if not json_path:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    
    
    # Carica i dati dal file JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)

    print("Oggetto JSON caricato:", gold_data)

    
    gold_standard=[]
    # cerco l'entry corrispondente all'url e restituisco il gold standard
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
    Dato risultato parsing e gs restituisce le metriche di evaluation.
    """
    
    #clean_parsed = BaseParser.remove_markdown(request.parsed_text)# da capire meglio
    # Pulisci il testo Markdown prima della valutazione
    #cleaned_parsed_text = clean_markdown(request.parsed_text)
    
    token_level_eval = Evaluator.token_level_eval(request.parsed_text, request.gold_text)
    x_eval = Evaluator.x_eval(request.parsed_text, request.gold_text)
    

    result=EvaluateResponse(token_level_eval=token_level_eval, x_eval=x_eval)
    return result



#TODO: fixato. x Valerio rivedi se è corretto 
@app.get("/full_gs_eval")
async def get_full_gs_eval(domain: str) -> FullGsEvalResponse:
    """
    Restituisce l'evaluation aggregata su tutto il GS.
    """
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent
    json_path = find_path(domain)
    if not json_path:
        raise HTTPException(status_code=400, detail="Dominio non supportato")
    
    # Carica i dati dal file JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
    
    eval_response = await evaluate_gold_standard(gold_data)

    if not eval_response:
        return FullGsEvalResponse(token_level_eval={"precision": 0, "recall": 0, "f1": 0}, x_eval={"jaccard": 0, "rouge_l": 0, "levenshtein": 0, "similarity_ratio": 0, "cosine_similarity": 0})
    
    precisions = []
    recalls = []
    f1_scores = []
    #extra metrics
    jaccard_scores = []
    rouge_l_scores = []
    levenshtein_distances = []
    similarity_ratios = []
    cosine_similarities = []

    for entry_name, metrics in eval_response.items():
        precision = metrics.get("precision", 0)
        recall = metrics.get("recall", 0)
        f1 = metrics.get("f1", 0)
        #extra metrics
        x_eval = metrics.get("x_eval", {})
        jaccard = x_eval.get("jaccard", 0)
        rouge_l = x_eval.get("rouge_l", 0)
        levenshtein = x_eval.get("levenshtein", 0)
        similarity_ratio = x_eval.get("similarity_ratio", 0)
        cosine_similarity = x_eval.get("cosine_similarity", 0)

        
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        #extra metrics
        jaccard_scores.append(jaccard)
        similarity_ratios.append(similarity_ratio)
        cosine_similarities.append(cosine_similarity)
        rouge_l_scores.append(rouge_l)
        levenshtein_distances.append(levenshtein)

    avg_f1 = 0
    avg_precision = 0
    avg_recall = 0
    #extra metrics
    avg_jaccard = 0
    avg_rouge_l = 0
    avg_levenshtein = 0
    avg_similarity_ratio = 0
    avg_cosine_similarity = 0
    if precisions:
        if len(precisions)==0:
            avg_precision =0
        else:
            avg_precision = sum(precisions) / len(precisions)
        if len(recalls)==0:
            avg_recall =0
        else:   
            avg_recall = sum(recalls) / len(recalls)
        if len(f1_scores)==0:
            avg_f1 =0
        else:
            avg_f1 = sum(f1_scores) / len(f1_scores)
        #extra metrics
        if len(jaccard_scores)==0:
            avg_jaccard =0
        else:
            avg_jaccard = sum(jaccard_scores) / len(jaccard_scores)
        if len(rouge_l_scores)==0:
            avg_rouge_l =0
        else:
            avg_rouge_l = sum(rouge_l_scores) / len(rouge_l_scores)
        if len(levenshtein_distances)==0:
            avg_levenshtein =0
        else:
            avg_levenshtein = sum(levenshtein_distances) / len(levenshtein_distances)
        if len(similarity_ratios)==0:
            avg_similarity_ratio =0
        else:
            avg_similarity_ratio = sum(similarity_ratios) / len(similarity_ratios)
        if len(cosine_similarities)==0:
            avg_cosine_similarity =0
        else:
            avg_cosine_similarity = sum(cosine_similarities) / len(cosine_similarities)


    result = FullGsEvalResponse(token_level_eval=  {"precision": avg_precision, "recall": avg_recall,"f1": avg_f1}, x_eval={"jaccard": avg_jaccard, "rouge_l": avg_rouge_l, "levenshtein": avg_levenshtein, "similarity_ratio": avg_similarity_ratio, "cosine_similarity": avg_cosine_similarity})
    return result

def find_path_parser(url: str,base_dir: Path) -> Optional[Any]:
    """
    Restituisce il parser e il percorso del file JSON corrispondente al dominio dell'URL.
    """
    if "wikipedia.org" in url:
        return WikipediaParser(), base_dir / "gs_data" / "wikipedia_org"/ "gs.json"
    elif "ilpost.it" in url:
        return IlPostParser(), base_dir / "gs_data" / "ilpost_it" / "gs.json"
    elif "statmuse.com" in url:
        return StatMuseParser(), base_dir / "gs_data" / "statmuse_com" / "gs.json"
    elif "eur-lex.europa.eu" in url:
        return EurLexParser(), base_dir / "gs_data" / "eurlex_europa_eu" / "gs.json"
    else:
        print(f"[WARNING] Dominio non riconosciuto: {url}")
        return None

def find_parser(url: str) -> Optional[BaseParser]:
    """
    Restituisce il parser corrispondente al dominio dell'URL.
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)