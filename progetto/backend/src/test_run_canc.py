from evaluation import evaluate_gold_standard, generate_evaluation_report
import json
from pathlib import Path
import asyncio

if __name__ == "__main__":
    # Chiedi il dominio all'utente
    #domain = input("Inserisci il dominio per il quale vuoi caricare il file JSON (esempio: wikipedia_org): ").strip()
    
    # dominio statico se preferisci:
    domain = "wikipedia_org" 
    #domain = "eurlex_europa_eu" 
    #domain = "ilpost_it"
    #domain= "statmuse_com"

    # Percorso del file gs.json basato sul dominio
    script_dir = Path(__file__).parent.resolve()
    gs_file_path = script_dir.parent.parent / "gs_data" / domain / "gs.json"

    # Controlla se il file esiste
    if not gs_file_path.exists():
        print(f"Errore: Il file JSON per il dominio '{domain}' non esiste nel percorso {gs_file_path}")
    else:
        # Carica i dati dal file JSON
        with open(gs_file_path, 'r', encoding='utf-8') as f:
            gold_data = json.load(f)

        print("Oggetto JSON caricato:", gold_data)

        # Valutazione del gold standard
        results = asyncio.run(evaluate_gold_standard(gold_data))

        # Generazione del report
        report = generate_evaluation_report(results)
        print(report)


