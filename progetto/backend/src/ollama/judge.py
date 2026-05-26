import json
import os
import re
import urllib.request
import urllib.error
from typing import Any, Dict

from ..parsers.base_parser import BaseParser


def extract_json_from_text(text: str) -> dict:
    """
    Prova a estrarre un JSON dalla risposta del modello.
    Se il modello aggiunge testo extra, prende il contenuto tra la prima { e l'ultima }.
    """
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("Nessun JSON trovato nella risposta del modello")

    return json.loads(match.group(0))


def normalize_judge_score(value: Any) -> int:
    """
    Converte il judge_score in intero e controlla che sia tra 1 e 5.
    Se non è valido, ritorna 0.
    """
    try:
        score = int(value)
    except Exception:
        return 0

    if score < 1 or score > 5:
        return 0

    return score


def validate_judge_response(parsed_json: dict, raw_response: str, model_name: str) -> Dict[str, Any]:
    """
    Controlla che la risposta del modello sia nel formato richiesto.
    Accetta solo:
    {
      "judge_score": int 1-5,
      "judge_feedback": str
    }
    """

    if not isinstance(parsed_json, dict):
        return {
            "model_name": model_name,
            "judge_score": 0,
            "judge_feedback": "Errore: la risposta del modello non è un oggetto JSON.",
            "extra_info": {
                "raw_response": raw_response
            }
        }

    allowed_keys = {"judge_score", "judge_feedback"}
    actual_keys = set(parsed_json.keys())

    if not allowed_keys.issubset(actual_keys):
        return {
            "model_name": model_name,
            "judge_score": 0,
            "judge_feedback": "Errore: risposta JSON valida ma formato non conforme.",
            "extra_info": {
                "raw_response": raw_response,
                "received_keys": list(actual_keys),
                "expected_keys": list(allowed_keys)
            }
        }

    judge_score = normalize_judge_score(parsed_json.get("judge_score"))

    if judge_score == 0:
        return {
            "model_name": model_name,
            "judge_score": 0,
            "judge_feedback": "Errore: judge_score mancante o fuori dal range 1-5.",
            "extra_info": {
                "raw_response": raw_response,
                "received_judge_score": parsed_json.get("judge_score")
            }
        }

    judge_feedback = str(parsed_json.get("judge_feedback", "")).strip()

    if not judge_feedback:
        return {
            "model_name": model_name,
            "judge_score": 0,
            "judge_feedback": "Errore: judge_feedback mancante o vuoto.",
            "extra_info": {
                "raw_response": raw_response
            }
        }

    return {
        "model_name": model_name,
        "judge_score": judge_score,
        "judge_feedback": judge_feedback,
        "extra_info": {
            "raw_response": raw_response
        }
    }


def build_judge_prompt(parsed_text: str, gold_text: str) -> str:
    """
    Costruisce il prompt per LLM-as-Judge.
    """

    parsed_text_clean = BaseParser.remove_markdown(parsed_text)
    gold_text_clean=gold_text
    #gold_text_clean = BaseParser.remove_markdown(gold_text)

    #in teoria non va messo ma il pc muore se gli passi tutto oppure è troppo grande la finstra e non ce l afa l ai
    
    #TODO: con 1200 il teser andava in timeout, con 300 funziona
    #max_chars = 1200
    max_chars=300
    parsed_text_clean = parsed_text_clean[:max_chars]
    gold_text_clean = gold_text_clean[:max_chars]

    return f"""
    Sei un valutatore automatico di parsing.

    Devi confrontare TESTO PARSATO e GOLD STANDARD.
    Non valutare la qualità giornalistica, stilistica o argomentativa del testo.
    Non suggerire miglioramenti generici.
    Valuta SOLO quanto il TESTO PARSATO conserva le informazioni presenti nel GOLD STANDARD.

    Rispondi SOLO con un JSON valido con ESATTAMENTE questi due campi:
    {{
    "judge_score": <intero da 1 a 5>,
    "judge_feedback": "<feedback breve in italiano>"
    }}

    Criteri:
    - 5 = il TESTO PARSATO contiene quasi tutte le informazioni del GOLD STANDARD e poco rumore
    - 4 = contiene le informazioni principali del GOLD STANDARD, con piccole omissioni o poco rumore
    - 3 = contiene una parte rilevante del GOLD STANDARD, ma mancano varie informazioni o c'è rumore
    - 2 = contiene poche informazioni del GOLD STANDARD oppure molto rumore
    - 1 = è quasi completamente diverso dal GOLD STANDARD, vuoto, non pertinente o pieno di rumore

    Nel feedback devi dire:
    - cosa manca rispetto al GOLD STANDARD, oppure
    - quale rumore/testo inutile è presente rispetto al GOLD STANDARD, oppure
    - se il contenuto coincide bene.

    Non dire cosa "sarebbe stato utile aggiungere" se non è presente nel GOLD STANDARD.
    Non usare altri campi.
    Non usare title, text, context, content, description.
    Non aggiungere spiegazioni fuori dal JSON.

    TESTO PARSATO:
    {parsed_text_clean}

    GOLD STANDARD:
    {gold_text_clean}
    """


def evaluate_with_ollama(parsed_text: str, gold_text: str) -> Dict[str, Any]:
    """
    Chiama Ollama per valutare parsed_text rispetto a gold_text.
    Restituisce sempre un dizionario con:
    - model_name
    - judge_score
    - judge_feedback
    - extra_info
    """
    #prendo le variabili d'ambiente per configurare la chiamata a ollama:

    #chiama ollama nel docker interno
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    model_name = os.getenv("OLLAMA_MODEL", "llama3.2:3b")  # default a un modello più leggero per evitare timeout
    endpoint = f"{ollama_url}/api/chat"

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": build_judge_prompt(parsed_text, gold_text),
            }
        ],
        # "stream": False, serve per mandare la rispsta tutta in una volta e non a pezzi
        "stream": False,
        "format": "json",
        "options": {
            #"num_predict": 300,
            #"temperature": 0.2,
            
        }
    }

    try:
        #crea il dato da mandare a ollama
        request_data = json.dumps(payload).encode("utf-8")

        #costruisco la richiesta HTTP POST a Ollama
        request = urllib.request.Request(
            endpoint,
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        #manda la richiesta a Ollama e aspetta la risposta, con un timeout di 320 secondi
        with urllib.request.urlopen(request, timeout=1000) as response:
            response_data = response.read().decode("utf-8")

        ollama_response = json.loads(response_data)

        content = (
            ollama_response
            .get("message", {})
            .get("content", "")
            .strip()
        )

        print("========== RISPOSTA GREZZA OLLAMA ==========", flush=True)
        print(content, flush=True)
        print("============================================", flush=True)

        parsed_json = extract_json_from_text(content)

        return validate_judge_response(
            parsed_json=parsed_json,
            raw_response=content,
            model_name=model_name
        )

    except Exception as e:
        print(f"[ERROR] Errore durante la chiamata a Ollama: {e}")

        return {
            "model_name": model_name,
            "judge_score": 0,
            "judge_feedback": "Errore: il modello non ha restituito un JSON valido o Ollama non è raggiungibile.",
            "extra_info": {
                "error": str(e)
            }
        }
    
