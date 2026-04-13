# Progetto Esonero 1 - Roadmap di Sviluppo

## Panoramica
Costruire una pipeline end-to-end per acquisire e analizzare documenti da sorgenti web eterogenee usando `Crawl4AI`.

## Fasi di Sviluppo

### Fase 1: Personalizzazione dei Parser ⭐ (PRIORITÀ ALTA)
**Obiettivo**: Rendere i parser funzionali e di qualità per ogni dominio assegnato.

**Task**:
- [ ] Testare ogni parser con 5-10 URL reali del dominio
- [ ] Regolare `CrawlerRunConfig` per ogni dominio:
  - `excluded_tags`: escludere elementi non rilevanti (nav, footer, aside, ecc.)
  - `word_count_threshold`: filtrare blocchi di testo troppo corti
  - `cache_mode`: scegliere la strategia di cache appropriata
- [ ] Verificare che `parsed_text` sia pulito e in formato MARKDOWN
- [ ] Testare gestione di URL problematici (404, timeout, ecc.)

**File da modificare**:
- `parser1.py` (ilpost.it)
- `parser2.py` (statmuse.com)
- `parser3.py` (eur-lex.europa.eu)
- `parser_wikipedia.py` (wikipedia.org)

**Metriche di successo**: Il parser deve estrarre testo pulito e leggibile per la maggior parte degli URL.

---

### Fase 2: Creazione del Gold Standard (GS) ⭐ (PRIORITÀ ALTA)
**Obiettivo**: Costruire dataset di riferimento per la valutazione.

**Task**:
- [ ] Per ogni dominio assegnato:
  - [ ] Selezionare **almeno 5 URL rappresentative** (NO homepage)
  - [ ] Scegliere pagine di tipo diverso con contenuti vari
  - [ ] Copiare manualmente il **solo testo informativo** dal browser
  - [ ] Escludere: menu, footer, sidebar, banner pubblicitari

- [ ] Creare file JSON `dominio_x_gs.json` con struttura:
  ```json
  [
    {
      "url": "https://...",
      "domain": "esempio.it",
      "title": "Titolo estratto",
      "html_text": "HTML grezzo della pagina (HTML senza filtri)",
      "gold_text": "Testo pulito manuale (NO MARKDOWN)"
    },
    ...
  ]
  ```

**Posizione file**: `gs_data/` (una cartella per dominio)

**Metriche di successo**: 
- Minimo 5 URL per dominio
- Testo coerente e ben formattato
- Copertina diverse tipologie di pagine

---

### Fase 3: Implementazione della Valutazione ⭐ (PRIORITÀ ALTA)
**Obiettivo**: Valutare qualità dei parser contro il GS.

**Task**:
- [ ] Implementare `token_level_eval` (OBBLIGATORIO):
  - **Precision**: `|tokens_estratti ∩ tokens_gs| / |tokens_estratti|`
  - **Recall**: `|tokens_estratti ∩ tokens_gs| / |tokens_gs|`
  - **F1**: `2 × precision × recall / (precision + recall)`

- [ ] Testare ogni parser contro il GS:
  - [ ] Eseguire parser su ogni URL del GS
  - [ ] Confrontare `parsed_text` con `gold_text`
  - [ ] Calcolare metriche
  - [ ] Registrare risultati

**Interpretazione F1**:
- **< 0.6**: Scarso (perde contenuto o aggiunge rumore)
- **0.6 - 0.80**: Medio (contenuto principale presente)
- **> 0.80**: Buono ✅ (cattura testo rilevante con poco rumore)

**Metriche di successo**: 
- F1 > 0.80 per almeno il 70% dei test
- Validazione manuale dei risultati

---

### Fase 4: API REST con FastAPI (PRIORITÀ MEDIA)
**Obiettivo**: Esporre gli endpoint per il parsing e la valutazione.

**Endpoint obbligatori**:

#### GET `/parse`
- **Input**: `url` (string, via query params)
- **Output**: JSON con `url`, `domain`, `title`, `html_text`, `parsed_text`
- **Errori**: Dominio non supportato, URL irraggiungibile

#### GET `/domains`
- **Input**: Nessuno
- **Output**: JSON con lista di domini supportati

#### GET `/gold_standard`
- **Input**: `url` (string, via query params)
- **Output**: Entry GS con `url`, `domain`, `title`, `html_text`, `gold_text`
- **Errori**: Dominio non supportato, URL non nel GS

#### GET `/full_gold_standard`
- **Input**: `domain` (string, via query params)
- **Output**: JSON con lista di tutti gli elementi GS per quel dominio
- **Errori**: Dominio non supportato

#### POST `/evaluate`
- **Input**: JSON con `parsed_text`, `gold_text`
- **Output**: JSON con `token_level_eval` (precision, recall, f1)

#### GET `/full_gs_eval`
- **Input**: `domain` (string, via query params)
- **Output**: Valutazione aggregata (media delle metriche su tutto il GS)
- **Errori**: Dominio non supportato

**Framework**: FastAPI + Pydantic
**Porta**: 8003
**File**: `backend/src/server.py`

**Metriche di successo**: 
- Tutti gli endpoint funzionano correttamente
- Validazione input/output con Pydantic
- Gestione esplicita degli errori

---

### Fase 5: Web UI (PRIORITÀ MEDIA)
**Obiettivo**: Interfaccia web per testare il parsing e visualizzare risultati.

**Funzionalità**:
- [ ] Input form per inserire URL
- [ ] Menù a tendina con URL dal GS (per test rapidi)
- [ ] Mostra confronto:
  - Testo HTML grezzo (input del parser)
  - Testo pulito (output del parser)
- [ ] Se URL nel GS:
  - [ ] Mostra `gold_text` (riferimento)
  - [ ] Visualizza metriche (Precision, Recall, F1)

**Tecnologie**: 
- HTML + CSS (Bootstrap opzionale)
- Jinja2 (template rendering)
- Python Flask o FastAPI per servire template

**Porta**: 8004
**File**: `frontend/src/frontend.py` e `frontend/templates/index.html`

**Metriche di successo**: 
- UI responsive e intuitiva
- Caricamento dinamico dei dati
- Visualizzazione corretta delle metriche

---

### Fase 6: Containerizzazione con Docker (PRIORITÀ MEDIA)
**Obiettivo**: Pacchettizzare l'applicazione in container orchestrati.

**Task**:
- [ ] Creare `Dockerfile` per backend (FastAPI):
  - Base image: `python:3.11-slim`
  - Installa dipendenze da `requirements.txt`
  - Expose porta 8003
  - CMD: `uvicorn server:app --host 0.0.0.0 --port 8003`

- [ ] Creare `Dockerfile` per frontend:
  - Base image: `python:3.11-slim`
  - Installa dipendenze da `requirements.txt`
  - Expose porta 8004
  - CMD: esegui app frontend

- [ ] Creare `docker-compose.yaml`:
  - Servizio backend (porta 8003)
  - Servizio frontend (porta 8004)
  - Volume per code mounting (opzionale)
  - Network per comunicazione

- [ ] Verificare che funzioni con `docker compose up --build`

**Requisiti**:
- Solo path relativi (NO path assoluti)
- Deve funzionare su Ubuntu subito dopo il comando
- Nessun errore durante build e startup

**File**:
- `backend/Dockerfile`
- `backend/requirements.txt`
- `frontend/Dockerfile`
- `frontend/requirements.txt`
- `docker-compose.yaml`

**Metriche di successo**: 
- `docker compose up --build` funziona senza errori
- Backend accessibile su `http://localhost:8003`
- Frontend accessibile su `http://localhost:8004`

---

### Fase 7: Test Automatico (PRIORITÀ MEDIA)
**Obiettivo**: Validare che il progetto passi i test automatici.

**Task**:
- [ ] Scaricare script di test da Google Classroom
- [ ] Eseguire `docker compose up --build`
- [ ] Eseguire script di test
- [ ] Verificare output: **"ALL TESTS PASS!"**
- [ ] Testare anche manualmente il frontend

**Metriche di successo**: 
- Script di test passa senza modifiche
- Nessun errore 500 da parte del server

---

### Fase 8: Report e Consegna (PRIORITÀ BASSA)
**Obiettivo**: Documentare il lavoro e consegnare il progetto.

**Task**:
- [ ] Creare `report.pdf` (max 2 pagine, LaTeX):
  - **Obiettivo del progetto**: Riassunto funzionalità (1-2 frasi)
  - **Organizzazione del codice**: Struttura moduli e responsabilità
  - **Valutazione parser**: Come valutati, risultati ottenuti
  - Sezioni aggiuntive (opzionali)

- [ ] Test finale su Ubuntu VM:
  - [ ] Scarica ISO Ubuntu 22.04.5
  - [ ] Installa su VM o dual boot
  - [ ] Sposta progetto in cartella diversa
  - [ ] Esegui `docker compose up --build`
  - [ ] Esegui test automatico
  - [ ] Salva copia prima di test

- [ ] Creare zip: `matricola1_matricola2_matricola3_lab_esonero_1.zip`
  - Struttura corretta
  - Nessun file di build o cache
  - Include: parser, GS, API, UI, Docker, report

- [ ] Consegnare su Google Classroom

**File**: `report.pdf` nella root del progetto

**Metriche di successo**: 
- Report chiaro e conciso
- Progetto funziona su Ubuntu senza modifiche
- Zip contiene tutti i file necessari

---

## Struttura Directory Finale

```
progetto/
├── docker-compose.yaml
├── domains.json
├── report.pdf
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── server.py
│       ├── evaluation.py
│       ├── database.py
│       └── parsers/
│           ├── base_parser.py
│           ├── parser1.py
│           ├── parser2.py
│           ├── parser3.py
│           └── parser_wikipedia.py
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── frontend.py
│       └── templates/
│           └── index.html
└── gs_data/
    ├── dominio_x_gs.json
    ├── dominio_y_gs.json
    └── en_wikipedia_gs.json
```

---

## Timeline Consigliato

| Fase | Scadenza Interna | Priorità |
|------|------------------|----------|
| 1. Parser | 20 aprile | ⭐⭐⭐ |
| 2. Gold Standard | 22 aprile | ⭐⭐⭐ |
| 3. Valutazione | 24 aprile | ⭐⭐⭐ |
| 4. API REST | 25 aprile | ⭐⭐ |
| 5. Web UI | 26 aprile | ⭐⭐ |
| 6. Docker | 26 aprile | ⭐⭐ |
| 7. Test | 26 aprile | ⭐⭐ |
| 8. Report + Consegna | **27 aprile** | ⭐ |

**Consegna Finale**: 27 aprile 2026

---

## Note Importanti

- ⚠️ **Bloccante**: Il progetto deve passare il test automatico per essere valutato
- ⚠️ **Attenzione ai path**: Usare SOLO path relativi, nessun path assoluto
- ⚠️ **Plagio**: Ogni forma di copia comporta annullamento del progetto
- ✅ **Testare su Ubuntu**: Prima di consegnare, testare su Ubuntu VM
- ✅ **Qualità del codice**: Commentare, type hints, modularità sono importanti

---

## Checklist Pre-Consegna

- [ ] Parser personalizzati e funzionanti (F1 > 0.80)
- [ ] Gold Standard completo (min 5 URL per dominio)
- [ ] API REST implementata e testata
- [ ] Web UI funzionante
- [ ] Docker funzionante su Ubuntu
- [ ] Test automatico passa ("ALL TESTS PASS!")
- [ ] Frontend testato manualmente
- [ ] Report completato (max 2 pagine)
- [ ] Progetto testato su Ubuntu VM
- [ ] Zip creato con nome corretto
- [ ] Consegnato su Google Classroom
