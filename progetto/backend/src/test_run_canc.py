from evaluation import evaluate_gold_standard, generate_evaluation_report
import json
from pathlib import Path

if __name__ == "__main__":
    # Esempio di utilizzo con Wikipedia e Minerva
     # Percorso del file gs.json
    script_dir = Path(__file__).parent.resolve()
    gs_file_path = script_dir.parent.parent / "gs_data" / "wikipedia_org" / "gs.json"

    # Carica i dati dal file JSON
    with open(gs_file_path, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)

    print("Oggetto JSON caricato:", gold_data)

    # Valutazione del gold standard
    results = evaluate_gold_standard(gold_data)

    # Generazione del report
    report = generate_evaluation_report(results)
    print(report)

   
