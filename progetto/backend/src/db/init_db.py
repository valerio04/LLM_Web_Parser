from pathlib import Path
from typing import List, Dict, Optional
import json
import time
try:
    from .repository import add_web_resource, add_gold_standard
except ImportError:
    from repository import add_web_resource, add_gold_standard

try:
    from .connection import get_connection
except ImportError:
    from connection import get_connection

def find_project_root() -> Path:
    """
    Cerca la root del progetto risalendo dalle cartelle finché non trova gs_data.
    Ritorna il path della root del progetto.
    """
    current_path = Path(__file__).resolve()

    for parent in current_path.parents:
        if (parent / "gs_data").exists():
            return parent

    raise FileNotFoundError("[ERROR] Cartella gs_data non trovata nella root del progetto")


def find_gs_json_files(base_dir: Path) -> List[Path]:
    """
    Cerca tutti i file gs.json dentro le sottocartelle di gs_data.
    """
    gs_data_dir = base_dir / "gs_data"
    #permette di trovare tutti i file */gs.jason dentro gs_data
    gs_json_files = sorted(gs_data_dir.glob("*/gs.json"))

    if not gs_json_files:
        raise FileNotFoundError(f"[ERROR] Nessun file gs.json trovato in {gs_data_dir}")

    return gs_json_files


def read_file(file_path: Path) -> str:
    """
    Legge il contenuto di un file di testo.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"[ERROR] File non trovato: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_json_file(json_path: Path) -> List[Dict]:
    """
    Carica il contenuto di un file gs.json.
    Il formato atteso è una lista di entry.
    l'output è una lista di dizionari, ognuno rappresenta un entry.
    """
    if not json_path.exists():
        raise FileNotFoundError(f"[ERROR] File JSON non trovato: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"[ERROR] Formato non valido in {json_path}: attesa una lista JSON")

    return data


def validate_entry(entry: Dict, json_path: Path) -> bool:
    """
    Controlla che una entry del GS abbia tutti i campi richiesti.
    """
    required_fields = ["url", "domain", "title", "html_file", "gold_file"]

    for field in required_fields:
        if field not in entry or not entry[field]:
            print(f"[WARNING] Campo mancante '{field}' in {json_path}")
            print(f"[WARNING] Entry ignorata: {entry}")
            return False

    return True


def load_entry_into_db(entry: Dict, base_dir: Path) -> bool:
    """
    Carica una singola entry del Gold Standard nel database.
    Inserisce prima web_resources e poi gold_standard.
    """
    try:
        url = entry["url"]
        domain = entry["domain"]
        title = entry["title"]

        html_file_path = base_dir / "gs_data" / entry["html_file"]
        gold_file_path = base_dir / "gs_data" / entry["gold_file"]

        html_text = read_file(html_file_path)
        gold_text = read_file(gold_file_path)

        add_web_resource(
            url=url,
            domain=domain,
            title=title,
            html_text=html_text,
        )

        add_gold_standard(
            url=url,
            gold_text=gold_text,
        )

        return True

    except Exception as e:
        print(f"[ERROR] Errore durante il caricamento dell'entry: {entry.get('url', 'URL non disponibile')}")
        print(f"[ERROR] Dettaglio: {e}")
        return False



def wait_for_db(max_retries: int = 20, delay: int = 2) -> None:
    """
    Aspetta che MariaDB sia pronto prima di caricare il Gold Standard.
    """
    for attempt in range(max_retries):
        try:
            conn = get_connection()
            conn.close()
            print("[INFO] Connessione al DB riuscita")
            return
        except Exception as e:
            print(f"[WARNING] DB non pronto, tentativo {attempt + 1}/{max_retries}: {e}")
            time.sleep(delay)

    raise RuntimeError("[ERROR] MariaDB non disponibile dopo vari tentativi")


def db_already_initialized() -> bool:
    """
    Controlla se il database è già stato popolato.
    Se web_resources contiene almeno una riga, considero il DB già inizializzato.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM web_resources")
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return count > 0

    except Exception as e:
        print(f"[WARNING] Impossibile controllare se il DB è già inizializzato: {e}")
        return False

def init_db_from_gs_data() -> None:
    """
    Inizializza il database caricando tutti i Gold Standard presenti in gs_data.
    Per ogni entry:
    - legge html_file
    - legge gold_file
    - salva HTML in web_resources
    - salva gold_text in gold_standard
    """
    wait_for_db()

    if db_already_initialized():
        print("[INFO] DB già inizializzato, caricamento GS saltato")
        return

    try:
        base_dir = find_project_root()
        gs_json_files = find_gs_json_files(base_dir)

        total_entries = 0
        loaded_entries = 0
        skipped_entries = 0

        print(f"[INFO] Root progetto trovata: {base_dir}")
        print(f"[INFO] File gs.json trovati: {len(gs_json_files)}")

        for json_path in gs_json_files:
            print(f"[INFO] Caricamento file: {json_path}")

            try:
                entries = load_json_file(json_path)
            except Exception as e:
                print(f"[ERROR] Impossibile leggere {json_path}: {e}")
                continue

            for entry in entries:
                total_entries += 1

                if not validate_entry(entry, json_path):
                    skipped_entries += 1
                    continue

                if load_entry_into_db(entry, base_dir):
                    loaded_entries += 1
                else:
                    skipped_entries += 1

        print("[INFO] Inizializzazione DB completata")
        print(f"[INFO] Entry totali lette: {total_entries}")
        print(f"[INFO] Entry caricate/aggiornate: {loaded_entries}")
        print(f"[INFO] Entry ignorate: {skipped_entries}")

    except Exception as e:
        print(f"[ERROR] Errore durante l'inizializzazione del database: {e}")


if __name__ == "__main__":
    init_db_from_gs_data()