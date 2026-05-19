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
        return 1

    if score < 1 or score > 5:
        return 1
    
    return score


def build_judge_prompt(parsed_text: str, gold_text: str) -> str:
    """
    Costruisce il prompt per LLM-as-Judge.
    """

    parsed_text_clean = BaseParser.remove_markdown(parsed_text)
    gold_text_clean = BaseParser.remove_markdown(gold_text)
    return f"""
    Valuta la qualità del testo estratto da un parser confrontandolo con il Gold Standard.

    Devi valutare:
    - completezza del contenuto informativo
    - presenza di testo inutile o boilerplate
    - coerenza rispetto al Gold Standard
    - eventuale testo mancante o rumore

    Rispondi SOLO con un JSON valido.
    Non usare markdown.
    Non aggiungere testo fuori dal JSON.

    Formato obbligatorio:
    {{
    "judge_score": <numero intero da 1 a 5>,
    "judge_feedback": "<breve feedback in italiano>"
    }}

    Scala:
    1 = pessimo
    2 = insufficiente
    3 = sufficiente
    4 = buono
    5 = ottimo

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

    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    model_name = os.getenv("OLLAMA_MODEL", "phi4-mini:latest")
    endpoint = f"{ollama_url}/api/chat"

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": build_judge_prompt(parsed_text, gold_text),
            }
        ],
        "stream": False,
    }

    try:
        request_data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            endpoint,
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            response_data = response.read().decode("utf-8")

        ollama_response = json.loads(response_data)

        content = (
            ollama_response
            .get("message", {})
            .get("content", "")
            .strip()
        )

        parsed_json = extract_json_from_text(content)

        judge_score = normalize_judge_score(
            parsed_json.get("judge_score", 0)
        )

        judge_feedback = str(
            parsed_json.get("judge_feedback", "")
        ).strip()

        if judge_score == 0:
            judge_feedback = "Errore: judge_score mancante o fuori dal range 1-5."

        if not judge_feedback:
            judge_feedback = "Il modello non ha fornito un feedback valido."

        return {
            "model_name": model_name,
            "judge_score": judge_score,
            "judge_feedback": judge_feedback,
            "extra_info": {
                "raw_response": content
            }
        }

    except Exception as e:
        print(f"[ERROR] Errore durante la chiamata a Ollama: {e}")

        return {
            "model_name": model_name,
            "judge_score": 1,
            "judge_feedback": "Errore: il modello non ha restituito un JSON valido o Ollama non è raggiungibile.",
            "extra_info": {
                "error": str(e)
            }
        }