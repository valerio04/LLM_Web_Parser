# Roadmap aggiornata secondo esonero / progetto finale

> Assunzione aggiornata: il primo esonero è completato **e avete già completato tutti i parser assegnati, 10 URL per dominio e metriche extra**. Questa roadmap quindi elenca solo ciò che resta da implementare per il progetto finale base. Sono esclusi lavori personalizzati/tesi.

## Stato attuale considerato già completato

- [x] Primo esonero completato.
- [x] Parser per tutti i domini assegnati.
- [x] Almeno 10 URL per dominio nel Gold Standard.
- [x] Gold Standard in JSON.
- [x] `token_level_eval` con precision, recall e F1.
- [x] Metriche extra già implementate.
- [x] API REST base del primo esonero.
- [x] Web UI base del primo esonero.
- [x] Containerizzazione base backend/frontend.

---

## Obiettivo finale rimasto

Portare il progetto alla versione finale integrando:

- database MariaDB persistente;
- caricamento automatico dei dati del Gold Standard nel DB;
- parsing in modalità locale usando HTML salvato nel DB;
- LLM-as-Judge con Ollama;
- API REST complete del progetto finale;
- Web UI completa per parsing, evaluation, Gold Standard, DB e statistiche;
- Docker Compose con 4 container: backend, frontend, MariaDB, Ollama;
- report finale e zip consegnabile.

---

## 1. Controllo e stabilizzazione di parser, GS e metriche già fatti

Anche se questa parte è completata, conviene fare un controllo prima di costruirci sopra DB, API e UI.

### Task di verifica

- [ ] Verificare che ogni parser restituisca sempre lo stesso formato:
  - `url`;
  - `domain`;
  - `title`;
  - `html_text`;
  - `parsed_text` in Markdown.
- [ ] Verificare che ogni dominio abbia almeno 10 entry GS complete.
- [ ] Verificare che ogni entry GS abbia:
  - `url`;
  - `domain`;
  - `title`;
  - `html_text` grezzo/statico;
  - `gold_text` pulito.
- [ ] Verificare che il parsing funzioni anche partendo dall'`html_text` statico, non solo live dal web.
- [ ] Verificare che `token_level_eval` e metriche extra non crashino con:
  - testo vuoto;
  - Markdown sporco;
  - URL non presente nel GS;
  - domini diversi.

### Priorità

Alta, ma è una fase di controllo: non è un blocco nuovo da implementare.

---

## 2. Database MariaDB

### Cosa manca

Nel primo esonero il database non era richiesto. Nel progetto finale deve diventare il centro della pipeline: deve salvare HTML, Gold Standard, risultati di parsing, metriche e giudizi LLM.

### Task

- [ ] Aggiungere MariaDB come container Docker dedicato.
- [ ] Usare MariaDB Connector/Python nel backend.
- [ ] Progettare lo schema relazionale.
- [ ] Implementare obbligatoriamente le tabelle con nomi fissi:
  - `web_resources`;
  - `gold_standard`.
- [ ] Rispettare i campi obbligatori di `web_resources`:
  - `url` come primary key;
  - `domain`;
  - `title`;
  - `html_text`;
  - `created_at`.
- [ ] Rispettare i campi obbligatori di `gold_standard`:
  - `url` come primary key e foreign key verso `web_resources.url`;
  - `gold_text`;
  - `created_at`.
- [ ] Aggiungere tabelle libere ma utili, ad esempio:
  - `parsed_documents`;
  - `metric_evaluations`;
  - `judge_evaluations`;
  - `domains`, se utile.
- [ ] Impostare foreign key e vincoli di integrità.
- [ ] Implementare script di inizializzazione automatico:
  - crea le tabelle se non esistono;
  - legge i JSON da `gs_data/`;
  - inserisce `web_resources` e `gold_standard`;
  - evita duplicati al riavvio.
- [ ] Fare in modo che il backend possa usare dati locali dal DB quando `local = true`.
- [ ] Salvare nel DB i risultati di parsing/evaluation quando vengono calcolati.

### Schema minimo consigliato

```sql
web_resources(
  url PRIMARY KEY,
  domain,
  title,
  html_text,
  created_at
)

gold_standard(
  url PRIMARY KEY REFERENCES web_resources(url),
  gold_text,
  created_at
)

parsed_documents(
  id PRIMARY KEY,
  url REFERENCES web_resources(url),
  parsed_text,
  created_at
)

metric_evaluations(
  id PRIMARY KEY,
  url REFERENCES web_resources(url),
  precision,
  recall,
  f1,
  extra_metrics_json,
  created_at
)

judge_evaluations(
  id PRIMARY KEY,
  url REFERENCES web_resources(url),
  model_name,
  judge_score,
  judge_feedback,
  created_at
)
```

### Priorità

Altissima. Molte API e pagine della UI dipendono dal DB.

---

## 3. LLM-as-Judge con Ollama

### Cosa manca

Nel progetto finale va implementata una valutazione automatica qualitativa tramite LLM locale. Per il progetto base non serve usare modelli enormi: va usato Ollama con un modello piccolo compatibile con CPU.

### Task

- [ ] Aggiungere un modulo `judge` nel backend.
- [ ] Integrare Ollama come servizio locale.
- [ ] Scegliere un modello piccolo compatibile con CPU, ad esempio:
  - `gemma4:e2b`;
  - `llama3.2:3b`;
  - `phi4-mini`;
  - `qwen3:4b`;
  - `ministral-3:3b`.
- [ ] Testare più modelli e sceglierne uno stabile.
- [ ] Creare un prompt strutturato che confronti:
  - `parsed_text`;
  - `gold_text`.
- [ ] Far rispondere il modello in JSON con almeno:
  - `model_name`;
  - `judge_score`, intero tra 1 e 5;
  - `judge_feedback`.
- [ ] Gestire il caso in cui l’LLM risponda male:
  - JSON non valido;
  - score mancante;
  - score fuori range;
  - timeout;
  - Ollama non disponibile.
- [ ] Prevedere un fallback sicuro, ad esempio:
  - `judge_score: null`;
  - `judge_feedback` con messaggio di errore controllato;
  - `status: error` se richiesto dalla vostra architettura.
- [ ] Salvare i giudizi del judge nel DB.
- [ ] Usare il judge anche in `/full_gs_eval`, calcolando lo score medio.

### Priorità

Alta. È uno dei blocchi nuovi principali del secondo esonero.

---

## 4. API REST complete

### Cosa manca

Le API del primo esonero vanno ampliate e adattate al DB, al parsing locale e al judge.

### Endpoint da implementare o aggiornare

#### Parsing

- [ ] `POST /parse`
  - input: `{"url": str, "local": Optional[bool]}`;
  - se `local = false` o assente: scarica live dal web;
  - se `local = true`: usa `html_text` salvato nel DB;
  - output: `url`, `domain`, `title`, `html_text`, `parsed_text`.

#### Domini e Gold Standard

- [ ] `GET /domains`
  - restituisce tutti i domini supportati.
- [ ] `GET /gold_standard`
  - input: `url`;
  - legge dal DB;
  - restituisce entry del GS.
- [ ] `GET /gold_standard_urls`
  - input: `domain`;
  - restituisce tutti gli URL del GS per quel dominio.

#### Evaluation

- [ ] `POST /evaluate`
  - input: `parsed_text`, `gold_text`;
  - output: `token_level_eval` + metriche extra già implementate.
- [ ] `POST /evaluate_judge`
  - input: `parsed_text`, `gold_text`;
  - output obbligatorio: `model_name`, `judge_score`, `judge_feedback`.
- [ ] `GET /full_gs_eval`
  - input: `domain`;
  - usa HTML statico salvato nel DB;
  - esegue parsing di tutte le entry;
  - calcola media di precision, recall, F1;
  - calcola media delle metriche extra;
  - calcola media del `judge_score`.

#### Gestione DB

- [ ] `POST /add_web_resource`
  - input: `url`, `html_text`;
  - aggiunge risorsa in `web_resources`.
- [ ] `POST /add_gold_standard`
  - input: `url`, `gold_text`;
  - aggiunge entry in `gold_standard`;
  - errore se la web resource non esiste.
- [ ] `DELETE /web_resource`
  - input: `url`;
  - elimina risorsa e, a cascata, il GS associato.
- [ ] `DELETE /gold_standard`
  - input: `url`;
  - elimina solo il GS, lasciando la web resource.

#### Stato e diagnostica

- [ ] `GET /db_stats`
  - conteggi `web_resources` per dominio;
  - conteggi `gold_standard` per dominio;
  - metriche medie;
  - judge score medio;
  - usa dati pre-calcolati e salvati nel DB, se disponibili.
- [ ] `GET /db_schema`
  - restituisce schema, tabelle e colonne del DB.
- [ ] `GET /status`
  - stato backend;
  - stato DB;
  - stato Ollama.

### Requisiti trasversali

- [ ] Usare FastAPI.
- [ ] Usare Pydantic per input/output.
- [ ] Rispettare esattamente i formati richiesti dalle slide.
- [ ] Gestire esplicitamente errori:
  - dominio non supportato;
  - URL irraggiungibile;
  - URL non presente nel DB;
  - URL non presente nel GS;
  - Ollama non disponibile;
  - input malformato.

### Priorità

Altissima. Il backend è la parte più probabile da testare automaticamente.

---

## 5. Web UI completa

### Cosa manca

La UI del primo esonero va trasformata in un’interfaccia completa per usare tutta la pipeline tramite API REST.

### Requisiti generali

- [ ] Usare HTML/CSS + Jinja2.
- [ ] Tenere il frontend in un container separato.
- [ ] Fare in modo che tutta la logica passi dalle API REST del backend.
- [ ] Mostrare chiaramente gli errori restituiti dal backend.

### Pagine da implementare

#### Home Page

- [ ] Link di navigazione alle sezioni principali.
- [ ] Matricole dei membri del gruppo.
- [ ] Stato del sistema:
  - backend;
  - DB;
  - Ollama.
- [ ] Lista domini supportati.

#### Pagina Parser & Evaluation

- [ ] Form per inserire un URL manualmente.
- [ ] Menu a tendina con URL presenti nel GS.
- [ ] Modalità Live/Local:
  - Live: scarica dal web;
  - Local: usa HTML salvato nel DB.
- [ ] Visualizzazione di:
  - `html_text` grezzo;
  - `parsed_text` in Markdown;
  - `gold_text`, se presente.
- [ ] Visualizzazione metriche:
  - precision;
  - recall;
  - F1;
  - metriche extra già implementate.
- [ ] Visualizzazione Judge:
  - modello usato;
  - score;
  - feedback testuale.

#### Pagina Gold Standard Builder

Anche se avete già 10 URL per dominio, questa pagina serve per gestire il DB e dimostrare che si possono aggiungere/modificare dati dalla UI.

- [ ] Selezione dominio.
- [ ] Inserimento URL.
- [ ] Download/visualizzazione HTML grezzo.
- [ ] Area testo per inserire `gold_text` manuale.
- [ ] Submit che salva nel DB:
  - web resource;
  - gold standard.
- [ ] Lista URL già presenti nel GS per il dominio selezionato.
- [ ] Pulsante per eliminare entry del GS.

#### Pagina Stats

- [ ] Conteggio `web_resources` per dominio.
- [ ] Conteggio `gold_standard` per dominio.
- [ ] Metriche medie per dominio.
- [ ] Judge score medio per dominio.
- [ ] Eventuali statistiche extra utili.

### Priorità

Media-alta. Non è solo estetica: deve permettere di usare DB, evaluation e judge senza chiamare le API a mano.

---

## 6. Docker Compose: passare da 2 container a 4 container

### Cosa manca

Il primo esonero richiedeva backend + frontend. Il progetto finale richiede architettura multi-container con backend, frontend, database e LLM.

### Container richiesti

- [ ] Backend FastAPI.
  - Porta obbligatoria: `8003`.
- [ ] Frontend Jinja2/HTML.
  - Porta obbligatoria: `8004`.
- [ ] MariaDB.
  - Porta obbligatoria: `3306`.
- [ ] Ollama.
  - Porta obbligatoria: `11434`.

### Task

- [ ] Aggiornare `docker-compose.yaml`.
- [ ] Aggiungere servizio MariaDB con volume persistente.
- [ ] Aggiungere servizio Ollama con volume persistente.
- [ ] Configurare variabili ambiente per:
  - host DB;
  - username/password DB;
  - nome database;
  - host Ollama;
  - modello scelto.
- [ ] Assicurarsi che il backend aspetti che DB e Ollama siano disponibili, o gestisca retry.
- [ ] Fare in modo che `init_db.py` o equivalente parta automaticamente al primo avvio.
- [ ] Usare solo path relativi.
- [ ] Verificare che funzioni con:

```bash
docker compose up --build
```

senza passaggi manuali intermedi.

### Priorità

Altissima. Il test automatico parte dopo `docker compose up --build`.

---

## 7. Struttura progetto consigliata

```text
progetto/
├── docker-compose.yaml
├── domains.json
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── server.py
│       ├── parsers/
│       │   ├── base.py
│       │   ├── wikipedia.py
│       │   ├── domain_1.py
│       │   ├── domain_2.py
│       │   └── domain_3.py
│       ├── evaluation/
│       │   ├── metrics.py
│       │   └── judge.py
│       ├── db/
│       │   ├── connection.py
│       │   ├── schema.sql
│       │   ├── repository.py
│       │   └── init_db.py
│       └── models/
│           └── schemas.py
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── frontend.py
│       └── templates/
├── gs_data/
│   ├── wikipedia_gs.json
│   ├── dominio_1_gs.json
│   ├── dominio_2_gs.json
│   └── dominio_3_gs.json
└── report.pdf
```

---

## 8. Ordine di lavoro consigliato aggiornato

### Fase 1 — Stabilizzazione rapida

- [ ] Verificare che parser, GS e metriche extra già completate funzionino ancora.
- [ ] Verificare parsing da HTML statico.
- [ ] Pulire struttura cartelle e codice.

### Fase 2 — Database

- [ ] Aggiungere MariaDB.
- [ ] Creare schema.
- [ ] Popolare DB da JSON al primo avvio.
- [ ] Collegare backend al DB.
- [ ] Salvare risultati parsing/evaluation nel DB.

### Fase 3 — API complete

- [ ] Aggiornare `/parse` con modalità `local`.
- [ ] Implementare endpoint GS dal DB.
- [ ] Implementare add/delete DB.
- [ ] Implementare stats/schema/status.
- [ ] Verificare formati JSON con Pydantic.

### Fase 4 — LLM Judge

- [ ] Aggiungere Ollama.
- [ ] Scegliere modello.
- [ ] Scrivere prompt.
- [ ] Implementare parsing JSON + fallback.
- [ ] Collegare `/evaluate_judge` e `/full_gs_eval`.
- [ ] Salvare i risultati del judge nel DB.

### Fase 5 — UI completa

- [ ] Home con status e domini.
- [ ] Parser & Evaluation.
- [ ] Gold Standard Builder.
- [ ] Stats.
- [ ] Gestione errori in pagina.

### Fase 6 — Docker e test finali

- [ ] Docker Compose a 4 container.
- [ ] Porte corrette: 8003, 8004, 3306, 11434.
- [ ] Nessun path assoluto.
- [ ] Test automatico backend.
- [ ] Test manuale frontend.
- [ ] Test in altra cartella/VM Ubuntu.

### Fase 7 — Consegna

- [ ] Scrivere `report.pdf`.
- [ ] Controllare struttura zip.
- [ ] Nome zip con tutte le matricole:

```text
matricola1_matricola2_matricola3_lab_progetto.zip
```

- [ ] Non includere lo script di test automatico.
- [ ] Consegnare su Google Classroom tramite form.

---

## 9. Checklist sintetica finale aggiornata

### Già fatto

- [x] 4 parser funzionanti: Wikipedia + 3 domini assegnati.
- [x] Almeno 10 URL per dominio nel GS.
- [x] GS in JSON dentro `gs_data/`.
- [x] `token_level_eval` funzionante.
- [x] Metriche extra implementate.

### Da fare

- [ ] HTML statico verificato e usabile per ogni entry.
- [ ] MariaDB funzionante.
- [ ] Tabelle obbligatorie `web_resources` e `gold_standard`.
- [ ] Popolamento DB automatico al primo avvio.
- [ ] Salvataggio risultati parsing/evaluation nel DB.
- [ ] LLM-as-Judge con Ollama.
- [ ] Fallback se il judge non restituisce JSON valido.
- [ ] API complete e conformi alla specifica.
- [ ] UI completa con Home, Parser/Evaluation, GS Builder, Stats.
- [ ] Docker Compose con 4 container.
- [ ] Porte corrette: backend 8003, frontend 8004, MariaDB 3306, Ollama 11434.
- [ ] `docker compose up --build` funziona senza step manuali.
- [ ] Test automatico backend superato.
- [ ] Frontend testato manualmente.
- [ ] Nessun path assoluto.
- [ ] Report PDF scritto in LaTeX.
- [ ] Zip finale con nome corretto.

---

## 10. Rischi principali da evitare

- Parser che funzionano live ma non con HTML statico dal DB.
- JSON del GS non coerente con i campi che servono al DB.
- Tabelle obbligatorie con nomi/campi diversi da quelli richiesti.
- Endpoint che rispondono con formato JSON diverso dalla specifica.
- LLM Judge che restituisce testo libero e manda in crash il backend.
- `full_gs_eval` troppo lento perché ricalcola tutto senza caching o senza usare dati salvati.
- Docker Compose che richiede comandi manuali dopo l’avvio.
- Path assoluti nel codice o nei volumi.
- Backend non esposto su `8003`.
- Frontend non esposto su `8004`.
- MariaDB/Ollama non raggiungibili dai test.
- Report dimenticato nello zip.
