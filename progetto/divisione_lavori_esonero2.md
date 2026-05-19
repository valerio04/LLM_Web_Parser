### Mancante

- [ ] Implementare `POST /evaluate_judge`
- [ ] Collegare `POST /evaluate_judge` al servizio LLM/Ollama
- [ ] Salvare `model_name`, `judge_score`, `judge_feedback` in `llm_judgements`
- [ ] Fare comparire `avg_eval_judge` popolato in `GET /db_stats`
- [ ] Implementare `GET /status`
- [ ] Verificare che tutti gli endpoint rispettino esattamente input/output della specifica
- [ ] Fare test automatici finali sugli endpoint

### LLM Judge

- [ ] Aggiungere container Ollama nel `docker-compose.yaml`
- [ ] Esporre Ollama sulla porta obbligatoria `11434`
- [ ] Scegliere il modello da usare, per esempio `llama3.2:3b`
- [ ] Automatizzare il pull/caricamento del modello all’avvio, se possibile
- [ ] Scrivere il prompt per LLM-as-Judge
- [ ] Forzare risposta JSON dal modello
- [ ] Gestire fallback se il modello non restituisce JSON valido
- [ ] Implementare chiamata Python verso Ollama
- [ ] Collegare il judge a `POST /evaluate_judge`
- [ ] Salvare il risultato in `llm_judgements`

### Web UI

- [ ] Pagina/sezione per selezionare dominio
- [ ] Pagina/sezione per selezionare URL dal Gold Standard
- [ ] Input manuale URL
- [ ] Opzione Live/Local per il parsing
- [ ] Bottone per eseguire `POST /parse`
- [ ] Visualizzazione `html_text`
- [ ] Visualizzazione `parsed_text`
- [ ] Visualizzazione `gold_text` se disponibile
- [ ] Bottone per eseguire `POST /evaluate`
- [ ] Visualizzazione metriche automatiche: precision, recall, F1, metriche extra
- [ ] Bottone per eseguire `POST /evaluate_judge`
- [ ] Visualizzazione `model_name`, `judge_score`, `judge_feedback`
- [ ] Pagina/sezione per mostrare `GET /db_stats`
- [ ] Pagina/sezione per mostrare `GET /status`
- [ ] Gestione errori restituiti dalle API

### Docker finale

- [x] Backend su porta `8003`
- [x] Frontend su porta `8004`
- [x] MariaDB su porta `3306`
- [ ] Ollama su porta `11434`
- [ ] Tutti i container avviabili con `docker compose up --build`
- [ ] Nessun path assoluto
- [ ] Testare progetto spostandolo in un’altra cartella



## Test finali e consegna

- [ ] Eseguire `docker compose down -v`
- [ ] Eseguire `docker compose up --build`
- [ ] Verificare che il DB venga popolato automaticamente
- [ ] Verificare `POST /parse`
- [ ] Verificare `GET /gold_standard`
- [ ] Verificare `GET /gold_standard_urls`
- [ ] Verificare `POST /evaluate`
- [ ] Verificare `POST /evaluate_judge`
- [ ] Verificare `GET /full_gs_eval`
- [ ] Verificare `POST /add_web_resource`
- [ ] Verificare `POST /add_gold_standard`
- [ ] Verificare `DELETE /web_resource`
- [ ] Verificare `DELETE /gold_standard`
- [ ] Verificare `GET /db_schema`
- [ ] Verificare `GET /db_stats`
- [ ] Verificare `GET /status`
- [ ] Eseguire script di test automatico ufficiale
- [ ] Ottenere `ALL TESTS PASS!`
- [ ] Aggiornare README / istruzioni di avvio
- [ ] Preparare `report.pdf`
- [ ] Pulire file temporanei di test
- [ ] Creare zip finale con struttura corretta


# Divisione dei lavori - Esonero 2 / Progetto Finale

## Stato attuale del progetto

Consideriamo già completate le parti del primo esonero e le estensioni già fatte dal gruppo:

- Parser per tutti i domini assegnati.
- Gold Standard con almeno 10 URL per dominio.
- Valutazione `token_level_eval`.
- Metriche extra già implementate.

Questa roadmap quindi riguarda solo ciò che manca per completare l'esonero 2 / progetto finale, escludendo i lavori personalizzati o di tesi.

---

# Obiettivo generale

Completare la pipeline finale con:

1. Database MariaDB.
2. Integrazione parser/API con il database.
3. LLM-as-Judge con Ollama.
4. API REST complete.
5. Web UI completa.
6. Docker Compose multi-container.
7. Test finali, README e preparazione consegna.

---

# Divisione del lavoro tra i 3 componenti

## Persona 1 - Database e persistenza dati

Questa persona si occupa della parte MariaDB e della gestione persistente dei dati.

### Responsabilità principali

- Progettare lo schema del database.
- Creare le tabelle obbligatorie:
  - `web_resources`
  - `gold_standard`
- Creare eventuali tabelle aggiuntive utili:
  - `parsed_documents`
  - `evaluations`
  - `llm_judgements`
- Scrivere lo script SQL di inizializzazione.
- Scrivere lo script Python per popolare il database al primo avvio.
- Caricare nel database:
  - URL
  - dominio
  - titolo
  - HTML grezzo
  - gold text
- Scrivere funzioni Python per leggere, inserire, modificare ed eliminare dati dal database.
- Preparare funzioni riutilizzabili dal backend FastAPI.

### File/cartelle consigliate

```text
database/
├── schema.sql
├── init_db.py
├── db.py
└── repository.py
```

### Tabelle minime obbligatorie

```sql
web_resources (
    url VARCHAR(...) PRIMARY KEY,
    domain VARCHAR(...),
    title TEXT,
    html_text LONGTEXT,
    created_at TIMESTAMP
);
```

```sql
gold_standard (
    url VARCHAR(...) PRIMARY KEY,
    gold_text LONGTEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (url) REFERENCES web_resources(url) ON DELETE CASCADE
);
```

### Output finale atteso

Alla fine, la Persona 1 deve consegnare:

- Database avviabile.
- Tabelle create correttamente.
- Gold Standard caricato automaticamente nel DB.
- HTML grezzo disponibile nel DB.
- Funzioni Python pronte per essere usate dalle API.

---

## Persona 2 - Backend FastAPI e API REST

Questa persona si occupa degli endpoint richiesti dal progetto finale e del collegamento tra parser, evaluation e database.

### Responsabilità principali

- Aggiornare il backend FastAPI.
- Collegare gli endpoint al database.
- Collegare gli endpoint ai parser già esistenti.
- Collegare gli endpoint alle metriche già implementate.
- Gestire gli errori in modo chiaro.
- Usare Pydantic per validazione input/output.

### Endpoint da controllare o implementare

#### Parsing

- `POST /parse`

Deve accettare:

```json
{
  "url": "https://...",
  "local": true
}
```

Comportamento:

- Se `local = true`, usa l'HTML salvato nel database.
- Se `local = false` o assente, scarica la pagina online.
- Se il dominio non è supportato, restituisce errore.
- Se l'URL non è nel DB quando `local = true`, restituisce errore.

---

#### Gold Standard

- `GET /domains`
- `GET /gold_standard`
- `GET /gold_standard_urls`

---

#### Evaluation

- `POST /evaluate`
- `POST /evaluate_judge`
- `GET /full_gs_eval`

---

#### Database management

- `POST /add_web_resource`
- `POST /add_gold_standard`
- `DELETE /web_resource`
- `DELETE /gold_standard`

---

#### Stato e statistiche

- `GET /db_stats`
- `GET /db_schema`
- `GET /status`

### File/cartelle consigliate

```text
backend/
├── main.py
├── routers/
│   ├── parse.py
│   ├── gold_standard.py
│   ├── evaluation.py
│   ├── judge.py
│   └── database.py
├── schemas/
│   └── models.py
└── services/
    ├── parser_service.py
    ├── evaluation_service.py
    ├── judge_service.py
    └── db_service.py
```

### Output finale atteso

Alla fine, la Persona 2 deve consegnare:

- API REST complete.
- Endpoint conformi alla specifica.
- Parsing da HTML locale funzionante.
- Evaluation automatica funzionante.
- Collegamento al DB funzionante.
- Gestione errori robusta.

---

## Persona 3 - LLM Judge, Web UI e Docker

Questa persona si occupa della parte LLM-as-Judge, dell'interfaccia web e della containerizzazione finale.

---

# Parte A - LLM-as-Judge

## Responsabilità principali

- Configurare Ollama.
- Scegliere un modello piccolo compatibile con CPU.
- Implementare il judge.
- Scrivere un prompt stabile.
- Forzare risposta JSON.
- Gestire fallback se l'LLM non risponde nel formato corretto.
- Collegare il judge all'endpoint `POST /evaluate_judge`.

### Modelli consigliati da provare

- `llama3.2:3b`
- `phi4-mini`
- `qwen3:4b`
- `gemma4:e2b`
- `ministral-3:3b`

### Output JSON obbligatorio

```json
{
  "model_name": "llama3.2:3b",
  "judge_score": 4,
  "judge_feedback": "Il testo è quasi completo, ma contiene un po' di rumore."
}
```

### Fallback obbligatorio

Se l'LLM non restituisce un JSON valido, il sistema deve comunque rispondere con una struttura sicura, ad esempio:

```json
{
  "model_name": "llama3.2:3b",
  "judge_score": 0,
  "judge_feedback": "Errore: il modello non ha restituito un JSON valido."
}
```

---

# Parte B - Web UI

## Responsabilità principali

La Web UI deve permettere di testare e visualizzare tutta la pipeline.

### Funzionalità consigliate

- Selezione del dominio.
- Selezione URL dal Gold Standard.
- Inserimento manuale di un URL.
- Bottone per eseguire il parsing.
- Opzione per usare `local=true`.
- Visualizzazione:
  - HTML grezzo
  - parsed text
  - gold text
- Bottone per evaluation automatica.
- Visualizzazione metriche:
  - precision
  - recall
  - F1
  - metriche extra
- Bottone per LLM-as-Judge.
- Visualizzazione:
  - model name
  - judge score
  - judge feedback
- Pagina o sezione per statistiche DB.
- Pagina o sezione per stato componenti.

### File/cartelle consigliate

```text
frontend/
├── app.py
├── templates/
│   ├── index.html
│   ├── results.html
│   └── stats.html
└── static/
    ├── style.css
    └── script.js
```

---

# Parte C - Docker

## Responsabilità principali

- Creare Dockerfile backend.
- Creare Dockerfile frontend.
- Configurare container MariaDB.
- Configurare container Ollama.
- Creare `docker-compose.yml`.
- Verificare che tutto parta con un solo comando.

### Container richiesti

```text
backend     FastAPI
frontend    Web UI
database    MariaDB
llm         Ollama
```

### Porte consigliate / richieste

```text
backend  -> 8003
frontend -> 8004
mariadb  -> 3306
ollama   -> 11434
```

### Comando finale atteso

```bash
docker compose up --build
```

### Output finale atteso

Alla fine, la Persona 3 deve consegnare:

- Judge funzionante.
- UI completa.
- Docker Compose funzionante.
- Sistema avviabile con un solo comando.

---

# Timeline consigliata

## Giorni 1-2

| Persona | Task |
|---|---|
| Persona 1 | Schema DB + tabelle obbligatorie |
| Persona 2 | Struttura API + Pydantic models |
| Persona 3 | Setup Ollama + primo judge funzionante |

### Obiettivo

Avere:

```text
DB creato
API avviabile
Judge testabile separatamente
```

---

## Giorni 3-5

| Persona | Task |
|---|---|
| Persona 1 | Script init DB dai JSON del Gold Standard |
| Persona 2 | Endpoint DB + parse con local=true |
| Persona 3 | Prima versione Web UI per parse/evaluate/judge |

### Obiettivo

Avere una pipeline base:

```text
Scelgo URL dal GS
Uso HTML locale dal DB
Eseguo parser
Confronto con gold_text
Calcolo metriche
Chiamo LLM Judge
```

---

## Giorni 6-8

| Persona | Task |
|---|---|
| Persona 1 | Salvataggio evaluation e judge nel DB |
| Persona 2 | /db_stats, /db_schema, /status |
| Persona 3 | Docker Compose completo |

### Obiettivo

Avere il progetto avviabile con:

```bash
docker compose up --build
```

---

## Giorni 9-12

Tutti lavorano insieme su:

- Test endpoint.
- Test UI.
- Test Docker.
- Bugfix.
- Pulizia codice.
- README.
- Preparazione demo.
- Controllo finale della specifica.

---

# Dipendenze tra i task

La sequenza più importante è:

```text
1. Schema DB
   ↓
2. Script init DB
   ↓
3. API collegate al DB
   ↓
4. UI collegata alle API
   ↓
5. Docker Compose unico
   ↓
6. Test finali
```

In parallelo:

```text
LLM Judge può essere sviluppato separatamente
e collegato alle API appena pronto.
```

---

# Branch Git consigliati

Non lavorare direttamente su `main`.

## Branch principale di sviluppo

```bash
dev-esonero2
```

## Branch per persona

```bash
feature/database
feature/api
feature/ui-judge-docker
```

## Flusso consigliato

```bash
git checkout dev-esonero2
git pull origin dev-esonero2

git checkout -b feature/nome-task
```

Quando una feature è pronta:

```bash
git checkout dev-esonero2
git pull origin dev-esonero2
git merge feature/nome-task
git push origin dev-esonero2
```

Quando tutto è stabile:

```bash
git checkout main
git merge dev-esonero2
git push origin main
```

---

# Regole pratiche per evitare problemi

## 1. Non modificare tutti gli stessi file

Per evitare conflitti:

- Persona 1 lavora soprattutto su `database/`.
- Persona 2 lavora soprattutto su `backend/`.
- Persona 3 lavora soprattutto su `frontend/`, `llm/` e Docker.

---

## 2. Decidere subito le interfacce

Prima di lavorare separati, stabilire:

- nomi delle funzioni DB;
- formato JSON degli endpoint;
- nomi delle tabelle;
- nomi dei campi;
- variabili d'ambiente Docker.

---

## 3. Docker non va lasciato alla fine

Anche se Docker è assegnato alla Persona 3, bisogna provarlo già dai primi giorni.

Il rischio principale è che il codice funzioni in locale ma non nei container.

---

## 4. Fare merge frequenti

Consigliato almeno un merge al giorno su:

```bash
dev-esonero2
```

In questo modo i problemi si scoprono subito.

---

# Checklist finale

## Database

- [ ] MariaDB parte in Docker.
- [ ] Tabelle `web_resources` e `gold_standard` create.
- [ ] Foreign key configurata correttamente.
- [ ] Script init funzionante.
- [ ] Gold Standard caricato nel DB.
- [ ] HTML grezzo caricato nel DB.

## API REST

- [ ] `POST /parse`
- [ ] `GET /domains`
- [ ] `GET /gold_standard`
- [ ] `GET /gold_standard_urls`
- [ ] `POST /evaluate`
- [ ] `POST /evaluate_judge`
- [ ] `GET /full_gs_eval`
- [ ] `POST /add_web_resource`
- [ ] `POST /add_gold_standard`
- [ ] `DELETE /web_resource`
- [ ] `DELETE /gold_standard`
- [ ] `GET /db_stats`
- [ ] `GET /db_schema`
- [ ] `GET /status`

## LLM Judge

- [ ] Ollama configurato.
- [ ] Modello scelto.
- [ ] Prompt scritto.
- [ ] Output JSON valido.
- [ ] Fallback per JSON non valido.
- [ ] Endpoint `POST /evaluate_judge` funzionante.

## Web UI

- [ ] Selezione dominio.
- [ ] Selezione URL dal GS.
- [ ] Parsing da UI.
- [ ] Evaluation da UI.
- [ ] Judge da UI.
- [ ] Visualizzazione metriche.
- [ ] Visualizzazione feedback LLM.
- [ ] Visualizzazione statistiche DB.

## Docker

- [ ] Dockerfile backend.
- [ ] Dockerfile frontend.
- [ ] Container MariaDB.
- [ ] Container Ollama.
- [ ] `docker-compose.yml`.
- [ ] Backend su porta `8003`.
- [ ] Frontend su porta `8004`.
- [ ] Avvio con `docker compose up --build`.

## Consegna

- [ ] README aggiornato.
- [ ] Istruzioni di avvio chiare.
- [ ] Esempi di chiamate API.
- [ ] Screenshot o descrizione UI.
- [ ] Test manuali effettuati.
- [ ] Branch finale pulito.
