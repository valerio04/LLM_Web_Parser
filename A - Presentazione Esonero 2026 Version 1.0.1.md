## Laboratorio di Ingegneria Informatica

Presentazione Esonero

Prof. Roberto **Navigli**Dott. Domenico **Fedele**

Progetto Obiettivo complessivo

- **●** _Costruire una_ pipeline end-to-end _per_ acquisire _e_ analizzare documenti _dasorgenti_ web _eterogenee_
- **●** _Applicazione reale_: il vostro lavoro contribuirà direttamente alla versione chatbotdell’LLM nazionale _Minerva_ (sviluppato da _Sapienza NLP_ e _Babelscape_)
**○** Stiamo per lanciare una versione che cerca sul Web e recupera i risultati dalmotore di ricerca, li parsa e li utilizza per dare una risposta aggiornata

- **●** E’ una bella occasione per lavorare su un progetto concreto nel campodell’Intelligenza Artificiale, con un impatto reale e immediato
+

**2** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto

Funzionalità del sistema

- **●** Acquisizione _di_ documenti _da sorgenti_ web _eterogenee_
- **●** Estrazione _del_ testo pulito _dai documenti acquisiti tramite_ parsing automatico
- **●** Archiviazione _strutturata dei documenti in un_ database relazionale
- **●** Valutazione automatica _della_ qualità _del testo_
- **●** Giudizio qualitativo _aggiuntivo tramite un_ LLM
- _●_ Interfaccia **REST API** e **Web UI** per la consultazione, il testing e la gestione dellapipeline
- **●** _Architettura multi_-_container_ orchestrata con Docker Compose(backend, frontend, database, LLM)
**3** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto

Architettura del sistema

**4** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Formazione dei gruppi

- **●** _Gli_ esoneri _e/o_ progetto finale _si svolgono in_ gruppi da 3 persone
(devono essere mantenuti gli stessi gruppi)

- **●** Entro il _9 aprile_ è necessario compilare il _form_ su _Classroom_ per _formalizzare_ il
gruppo - un gruppo un solo invio!!!

- **●** _Chi ha_ difficoltà _a_ trovare _un_ gruppo, si presenti il 9 aprile in aula per _un_
matchmaking.

- **●** Eventuali richieste di _gruppi_ con numero _ridotto_ di studenti_, ben motivate ed_
**eccezionali, saranno valutate** caso per caso (non implicano una semplificazione

del progetto)

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Esoneri Informazioni generali

- **●** _Consegna:_ la consegna per l’esonero 1 è prevista _il giorno 27 aprile 2026_
- **●** Il primo esonero viene assegnato oggi. Il secondo esonero concluderà il progetto, con consegna
al massimo 8 giorni prima di ciascun appello (ENTRO SETTEMBRE)

- **●** Gli esoneri non sono obbligatori
**○** E’ possibile _consegnare_ il _progetto completo_ in un’unica soluzione al massimo _8 giorni_

prima di ciascun appello

**○** _Esempio:_ appello il 25 dicembre → consegna entro il 17 dicembre (mezzanotte circa)

- **●** Accesso alla tesi
**○** Tutti gli studenti possono utilizzare il progetto svolto come tesi triennale_, applicando_

una personalizzazione che sarà illustrata nelle prossime settimane

**○** _I migliori_ ~10 studenti _potranno accedere a un_ esonero 2 e progetto di tesi personalizzato

_in_ NLP

- **●** _Perché fare l’esonero?_ Perché copre una parte sostanziale del lavoro progettuale, è seguito con
attenzione dai docenti e offre una base già pronta per la prova finale

**6** Navigli, Fedele - Laboratorio di Ingegneria Informatica

# Esonero 1

Navigli, Fedele - Laboratorio di Ingegneria Informatica **7**

Esonero 1 5 obiettivi

1. **Implementazione iniziale dei parser per i domini web assegnati**Parser dedicati per estrarre il testo rilevante dalle pagine dei domini assegnati
2. **Costruzione di un gold standard (GS)**Dataset di riferimento costruito manualmente, contenente il testo corretto da confrontare
_con l’output del parser3._ Valutazione automatica dei parser con metriche specifiche

Misurazione della qualità del parsing tramite metriche quantitative4. **Esposizione dei dati via API REST**

Endpoint per parsing, accesso ai dati e valutazione automatica5. **Web UI** e **Containerizzazione** con **Docker**

Interfaccia di test e ambiente eseguibile in modo semplice e uniforme

**NOTA**: Database e LLM as a Judge fanno parte dell’architettura complessiva del progetto,non sono richiesti in questo esonero

**8** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Task

- **●** _Parser_: implementare un parser Python specifico per le pagine di ciascun dominioweb assegnato (es. it.wikipedia.org)
- **●** Dato un _URL_ proveniente da uno dei _domini assegnati_ il parser deve _estrarre_ le
_seguenti_ informazioni_:_

**○** "url": "https//...",

**○** "domain": "esempio.it",

**○** "title": "Titolo della pagina web",

**○** "html_text": "Testo estratto della pagina web grezzo (HTML senza filtri), su

cui è possibile rieseguire il parsing per ottere di nuovo parsed_text”

**○** "parsed_text": "Testo estratto pulito senza tag HTML o di altro genere, in

formato **MARKDOWN**”

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Libreria per il parsing - Crawl4AI

- **●** Per il _download_ e il _parsing_ delle _pagine web_ potete utilizzare la _libreria_
Crawl4AI _con_ configurazione personalizzata _per ogni_ dominio

- **●** Crawl4AI _è una_ libreria _Python_ open-source _progettata per il_ web scraping
orientato all'AI

- **●** Trasforma qualsiasi _pagina web_ in dati _strutturati_ (_Markdown_, JSON,
screenshot, HTML) _pronti_ per essere consumati da _modelli linguistici_ (LLM)

- _●_ Sfruttate la libreria per estrarre direttamente il **Markdown** ed eventualmente
ripulirlo ulteriormente

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Crawl4AI - Installazione

- **●** Installare la libreria
pip install -U crawl4ai

- **●** Setup del browser (Chromium scaricato automaticamente)
crawl4ai-setup

- **●** Verificare l’installazione
**○** crawl4ai-doctor

**○** python -c "import crawl4ai; print('OK')"

- **●** Per eventuali problematiche potete consultare la documentazione
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Crawl4AI - Esempio di download e parsing

- **●** BrowserConfig
Configura il browser

(headless, proxy, viewport)

- **●** CrawlerRunConfig
Configura la singola richiesta. Agire sulla

configurazione per migliorare l’output del

parsing della libreria

- **●** AsyncWebCrawler
Il motore del crawler; usato come context

**manager** apre e chiude il browser in modo

sicuro _.arun()_ **visita l'URL e** restituisce il

contenuto estratto usando la config scelta_._

Dovete agire anche sull’output del parsing

per migliorare la qualità.

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Pipeline di Parsing

1. **Selezione** manuale delle **pagine** più **rilevanti** del **dominio** assegnato2. **Parser Python** dedicato per ciascun dominio
3. **Crawl4AI** con configurazione personalizzata per il dominio specifico(modificare _CrawlerRunConfig_ e/o l’output del parsing)
4. Estrazione di **metadati** e **testo pulito** dall’output di Crawl4AI5. **Output** strutturato: _url, domain, title, html_text, parsed_text_
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Assegnazione dei domini da parsare

- **●** Ogni gruppo dovrà _parsare pagine_ provenienti da _domini_ web _specifici_
(es. it.wikipedia.org , [https://www.reddit.com,](https://www.reddit.com,) [https://stackoverflow.com](https://stackoverflow.com) e altri)

**○** NOTA: non dovete parsare la home page del sito, ma solo le pagine informative

- **●** Il _parsing_ delle pagine provenienti dal dominio _wikipedia.org_ è uguale e _obbligatorio_ per
tutti (in inglese se, ordinando i cognomi del gruppo in ordine alfabetico, il primo cognome

inizia con una lettera “dispari”, ovvero A, C, E, G, I, K, M, O, Q, S, U, W, Y; in italiano altrimenti)

- **●** 3 domini aggiuntivi _saranno assegnati_ randomicamente _ad ogni gruppo:_
**○** Almeno _1 su 3_ dei domini _aggiuntivi_ vanno parsati correttamente per l’esonero

**○** _Più domini_ riuscirete a parsare correttamente _maggiore_ sarà la _valutazione_

**○** _I_ domini aggiuntivi _saranno_ assegnati _alla_ chiusura _del_ form _per la formazione dei_

**gruppi** (dopo il 9 aprile, potete comunque cominciare con it.wikipedia.org o

en.wikipedia.org)

**○** Saranno comunicati su _Google Classroom_

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard per Domini Assegnati Cos’è un Gold Standard?

- **●** Un _Gold Standard (GS)_ è un insieme di _dati_ di riferimento, costruito e verificato
manualmente_, considerato come_ corretto

- **●** Serve a _valutare_ la _qualità_ dei risultati _prodotti_ da un sistema automatico,
fornendo un termine di confronto affidabile

- **●** Si _confronta l’output del sistema_ con il _GS,_ così da misurare in modo oggettivo
quanto il risultato prodotto sia corretto

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard per Domini Assegnati Gold Standard per il parsing di pagine Web

- **●** Gold Standard (GS)_: per ogni_ dominio assegnato_, selezionare almeno_ 5 URL
rappresentative (pagine di tipo diverso, con contenuti vari, no home page)

- **●** Per ogni URL: _aprire la pagina nel_ browser_, copiare_ manualmente _il solo_ testo
**informativo** (no pubblicità, contenuti collaterali o ripetuti in ogni pagina, ecc.)

**○** _Includere_: titolo e corpo dell'articolo

**○** _NON includere_: menu di navigazione, footer, sidebar, banner pubblicitari

- **●** Utilizzare il _GS_ per valutare la _qualità_ dei vostri _parser_
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard per Domini Assegnati Formato del Gold Standard

- **●** _Salvare i_ GS _in file_ JSON, uno per ogni dominio
- **●** Un _entry_ del vostro _GS_ contiene le seguenti informazioni:
**○** "url": "https//...",

**○** "domain": "esempio.it",

**○** "title": "Titolo della pagina web",

**○** "html_text": “Testo estratto della pagina web grezzo (HTML senza filtri),

su cui è possibile rieseguire il parsing per ottere di nuovo **parsed_text** da

confrontare con _gold_text_”

**○** "gold_text": "Testo estratto pulito senza tag HTML o di altro genere”

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard

Esempio Estrazione Info - Wikipedia

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard

Esempio Estrazione Info - reddit

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard Esempi di GS

- **●** Esempi di _elementi_ del _GS_ per alcune pagine di _Wikipedia_
- **●** Dominio 1: en.wikipedia.org**○** Pagina 1: en.wikipedia.org/wiki/Minerva -> GS
**○** Pagina 2: en.wikipedia.org/wiki/BabelNet -> GS

- **●** Dominio 2: it.wikipedia.org**○** Pagina 1: it.wikipedia.org/wiki/Minerva -> GS
**○** Pagina 2: it.wikipedia.org/wiki/BabelNet -> GS

Navigli, Fedele - Laboratorio di Ingegneria Informatica

### Obiettivo 3: Valutazione Parser

Valutare Qualità Parsing

- **●** _Valutare_ la _qualità_ dell'_output_ prodotto dai _parser_ implementati
- **●** _La_ valutazione _sarà effettuata tramite_ metriche quantitative implementate da voi_,_
usate come _indicatori_ oggettivi della _qualità_ del parsing

- **●** I _Gold Standard_ (GS) prodotti saranno _utilizzati_ come _dataset_ di _test_ per il confronto
con l’output del parser

- **●** _Solo_ una valutazione _è_ obbligatoria _(__token_level_eval__), ma sono_ apprezzate _anche_
eventuali **altre tecniche** di valutazione (sperimentate, cercate online, chiedete agli

LLM!)

Navigli, Fedele - Laboratorio di Ingegneria Informatica

### Obiettivo 3: Valutazione Parser

Valutare Qualità Parsing

- **●** Evaluation obbligatoria _da implementare “__token_level_eval__”:_
**○** La valutazione avviene a _livello_ di _token_

**■** parole separate per spazio in lowercase

**■** senza markdown, in questa fase la parte rilevante da valutare è il testo estratto

**○** _tokens_estratti_ = insieme dei token nel testo prodotto dal parser

**○** _tokens_gs_ = insieme dei token nel testo del Gold Standard

**○** Metriche

_■_ _Precision_ = |tokens_estratti **∩** tokens_gs| / |tokens_estratti|

Tra i token trovati dal modello, quanti sono davvero corretti?

_■_ _Recall_ = |tokens_estratti **∩** tokens_gs| / |tokens_gs|

Tra tutti i token corretti possibili, quanti il modello è riuscito a trovare?

**■** _F1_ = 2 × precision × recall / (precision + recall)

Media armonica tra precision e recall, utile per avere un unico indicatore bilanciato

Navigli, Fedele - Laboratorio di Ingegneria Informatica

### Obiettivo 3: Valutazione Parser

Come Interpretare la ‘_token_level_eval’_ F1

Fascia Range F1 Interpretazione

**Scarso** < 0.6 Il parser perde contenuto rilevante o introduce molto rumore

**Medio** 0.6 – 0.80 Contenuto principale presente ma con omissioni o boilerplate non rimosso

**Buono** > 0.80 Il parser cattura la maggior parte del testo rilevante con poco rumore

**NOTA**: data la semplicità di questa metrica, "Buono” è condizione necessaria manon sufficiente per considerare il parser affidabile. Verificate anche manualmente.

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: API REST Overview API REST

- **●** Implementare con _FastAPI_ un _WEB Server_ per accedere ai seguenti endpoint:
**○** _GET /parse_: esegue il parser per un documento di un dominio

**○** _GET /domains_: restituisce la lista dei domini assegnati

**○** _GET /gold_standard_: restituisce il gold standard per un documento

**○** _GET /full_gold_standard_: restituisce tutto il GS del dominio

**○** _POST /evaluate_: dato risultato parsing e gs restituisce le metriche di evaluation

**○** _GET /full_gs_eval_: restituisce l’evaluation aggregata su tutto il GS

- **●** Usare _Pydantic_ per validazione I/O
- **●** _I_ formati di input/output _devono_ rispettare _esattamente la_ specifica_, perché saranno_
testati automaticamente

- **●** _Gestire_ esplicitamente _errori_ come dominio non supportato e URL irraggiungibile
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: API REST GET /parse

- **●** Seleziona automaticamente il parsercorretto in base al dominio dell'URL ed
esegue il parsing _//_ **OUTPUT - JSON**_{_

- url": "[https://...",](https://...",)
- **●** _Input__:_ _"url": str_ _(tramite url)_ "domain": "esempio.it",
- title": "Titolo estratto dalla pagina web",
- **●** _Output_: oggetto JSON nel formato indicato
- html_text": "Html estratto dalla pagina web, input del parser",
- parsed_text": "Testo pulito, output del
- **●** _Errori__:_ parser di riferimento, in
**○** Se il dominio non è supportato _formato MARKDOWN"_

**○** Se l'URL è irraggiungibile _}_

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: API REST GET /domains

- **●** Restituisce la lista dei domini supportati
dal sistema (es. it.wikipedia.org) _//_ **OUTPUT - JSON**

{

- **●** _Input__: nessuno_ "domains": [
- **●** _Output_: oggetto JSON nel formato indicato _"esempio_1.it",_
- esempio_2.it", …
}

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: API REST GET /gold_standard

- **●** Restituisce l’entry del GS per l’URL dato in
**input.** _//_ OUTPUT - JSON

{

- **●** _Input__:_ _"url": str_ _(tramite url)_ "url": "[https://...",](https://...",)
- domain": "esempio.it",
- **●** _Output__: oggetto JSON nel formato indicato._ "title": "Titolo estratto dalla pagina web",
- html_text": "Html estratto dalla pagina web, input del parser",
- **●** _Errori__:_ "gold_text": "Testo pulito, estratto
**○** _Se il dominio non è supportato_ manualmente dalla pagina web,no MARKDOWN"

**○** L'URL non è nel GS. _}_

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: API REST

GET /full_gold_standard _//_ **OUTPUT - JSON**

{

- **●** Restituisce la lista degli elementi di un _“gold_standard”:[_
GS per un dominio specifico _{_

- url": "[https://...",](https://...",)
- **●** _Input__:_ _"domain": str_ _(tramite url)_ "domain": "esempio.it",
- "title": "Titolo estratto dalla pagina web",**(lo stesso usato nella lista get domains)**
- html_text": "Html estratto dalla
- **●** _Output__: oggetto JSON nel formato_ pagina web, input del parser",
**indicato.** "gold_text": "Testo pulito, estrattomanualmente dalla pagina web,

no MARKDOWN"

- **●** Errori_:_ _},_
**○** Se il dominio non è supportato. _...]_

}

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: API REST POST /evaluate

- **●** Dato il risultato del parsing di un _//_ _OUTPUT - JSON__{_
documento e il corrispettivo testo del GS _“token_level_eval”: {_

| restituisce le metriche di evaluation | "precision": 0.87, |
| --- | --- |
| (rimuovere il markdown in fase di evaluation, | "recall": 0.91, |

- _"f1": 0.89,_confrontare solo il contenuto) _},_
- x_eval”:{
- **●** _Input__:_ {"parsed_text": str, "gold_text": str} _}_
- **●** _Output_: oggetto JSON nel formato indicato. _}_
_Attenzione_**:** token_level_eval **con** precision,

_recall_ e _f1_ è obbligatorio

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: API REST GET /full_gs_eval

- **●** Restituisce la valutazione complessiva del Gold _//_ _OUTPUT - JSON_
Standard per il dominio dato in input. Esegue il _{_

parsing di tutte le sue entry e aggrega i risultati _“token_level_eval”: {_

| tramite media delle metriche, calcolate sui singoli | "precision": 0.87, "recall": 0.91, |
| --- | --- |
| elementi del GS (rimuovere il markdown in fase di | "f1": 0.89, |

evaluation, confrontare solo il contenuto) _},_

- x_eval”:{ }
- **●** _Input_: _"domain": str_ (tramite url) _}_
- **●** _Output_: oggetto JSON nel formato indicato.
- **●** Errori_:_
**○** Se il dominio non è supportato.

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 5: Web UI e Containerizzazione Web UI

- **●** Implementazione _della_ Web UI
Realizzare **l’interfaccia web** in **HTML**, utilizzando **Jinja2** per il rendering dinamico dei

contenuti.

- **●** Funzionalità principali
**○** Consentire _l’inserimento_ di un URL per mostrare un _confronto_ tra testo della

**pagina web grezzo** (HTML) e **testo pulito** senza tag HTML o di altro genere

**○** Mettere a disposizione un _menù a tendina_ con tutti gli _URL_ presenti nel _Gold_

**Standard** (GS), in modo da eseguire rapidamente la UI

_○_ Se per l’**URL** selezionato è disponibile il **GS**:

**■** _confrontare_ il risultato con il testo pulito presente nel GS

**■** _mostrare_ la _valutazione_ tramite le _metriche_ già implementate.

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 5: Web UI e Containerizzazione Containerizzazione con Docker

- **●** _Containerizzazione_ del sistema con _Docker_ (vedi lezione del 9 aprile)
- **●** Requisiti
_○_ **Backend** containerizzato (FastAPI) sulla porta _8003_

**○** _Frontend_ containerizzato (HTML + Jinja2) sulla porta _8004_

**○** _docker-compose.yaml_ per avviare tutto con un solo comando

(come visto a lezione)

**○** Usare solo path relativi (nessun path assoluto)

**○** Deve funzionare su Ubuntu subito dopo:

docker compose up --build

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Struttura delle Directory del Progetto

progetto/

| ● docker-compose.yaml sistema con un solo comando : avvia l'intero | ├── ├── ├── docker-compose.yaml domains.json gs_data/ |
| --- | --- |
| ● backend/ modulo di valutazione : server FastAPI, parser, | │ │ ├── └── dominio_x_gs.json dominio_y_gs.json |

**├──** backend/

| ● frontend/ HTML/Jinja2 con template : interfaccia web | │ │ ├── ├── Dockerfile requirements.txt |
| --- | --- |
| ● gs_data/ ciascun dominio : Gold Standard JSON per | │ │ ├── └── └── frontend/ src/ server.py |

- **●** _domains.json_: lista dei domini **│ ├──** _Dockerfile_assegnati **│ ├──** _requirements.txt_
│ └── _src/_

- **●** _report.pdf_: max 2 pagine, redatto in **│ └──** _frontend.py_LaTeX **│ └──** _templates/_
**└──** report.pdf

**33** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Test automatico

Test del backend

- **●** Vi forniremo nei prossimi giorni su Google Classroom uno _script_ che avvierà un _testautomatico_ di tutti gli _endpoint_ definiti nella specifica del _WEB Server_ del progetto
- **●** Dovete _esporre_ la _backend_ del vostro _progetto_ sulla porta _8003_. Lo script di testing,eseguito fuori dai Docker container del vostro progetto, deve poter accedere a quella porta
per eseguire il test automatico (non modificare la porta nello script di test)

- **●** Dovete _esporre_ la _frontend_ del vostro _progetto_ sulla porta _8004_ (anche se non vieneesplicitamente testato)
- **●** Il test deve funzionare subito dopo il comando: _docker compose up --build_Non ci devono essere passaggi intermedi tra questa inizializzazione automatica e
l’esecuzione dello script di test

**34** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Test automatico

Test del backend

- **●** Dovete riuscire ad _eseguire_ l’intero _script_ di _test_ senza modifiche arrivando avedere:
- **“ALL TESTS PASS!”**Indispensabile prima di effettuare la consegna
- **●** _Non_ dovete _modificare_ lo _script_ di _test_, dato che noi lo useremo esattamente cosìcom’è per valutare i progetti
- **●** Se pensate di aver _trovato_ un _errore_ nello script di test _comunicarlo_ tramite_Google Classroom_
**35** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Test automatico Test del frontend

- **●** Ricordate di _testare_ voi stessi anche il _frontend_ del vostro _progetto_, dopo avereseguito i test automatici con successo e prima di consegnare
- **●** Il frontend _non viene valutato automaticamente_ dallo script di test
- **●** _Non_ dovete _consegnare_ lo _script di test_ insieme al vostro progetto(è uguale per tutti)
**36** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Test automatico

Test finali prima della consegna

- **●** Il comando _docker compose up --build_ deve funzionare su un qualsiasi computer, quindinon si possono usare path assoluti ma solo path relativi.
Prima di consegnare spostate il vostro progetto in un'altra cartella nel vostro computer econtrollare che _docker compose up --build_ funzioni ancora ***senza cambiare nulla*** per

assicurarvi che funzioni anche sul nostro computer che useremo per le correzioni.

- **●** Potete sviluppare su Mac/Windows ma noi eseguiremo il comando _docker compose up--build_ su Linux (Ubuntu), quindi se state sviluppando su Mac/Windows dovete
controllare che questo comando funzioni correttamente anche su **Ubuntu** prima diconsegnare (usate un **macchina virutale**, vedere slide successive)

- **●** Ricordate di eseguire anche il test automatico e di testare il frontend dopo ognuno diquesti test
**37** Navigli, Fedele - Laboratorio di Ingegneria Informatica

# Consegna

Navigli, Fedele - Laboratorio di Ingegneria Informatica **38**

Consegna

Singolo Zip

- **●** Consegnare un _singolo file zip_ che è lo zip della _cartella_ del vostro _progetto_,con il nome che include tutte le matricole dei membri del gruppo:
matricola1_matricola2_matricola3_lab_esonero_1.zip

- **●** La _struttura_ delle _directory_ all’interno del file zip deve essere in linea con quella_specificata_ nelle _slide precedenti_
- **●** Potete usare più file, cartelle e sottocartelle se li reputate utili a organizzaremeglio il progetto
**39** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Consegna

Docker Compose

- **●** Il vostro _progetto_ verrà _eseguito_ tramite il comando_docker compose up --build_
eseguito da terminale nella directory del file**docker-compose.yaml**

- **●** Il file _docker-compose.yaml_ contiene le istruzioni necessarie per avviare l’interoprogetto con il comando _docker compose up --build_
- **●** I due moduli _frontend_ e _backend_ sono separati in cartelle diverse, ognuna con ilsui file _requirements.txt_ e _Dockerfile_, necessari per la costruzione del loro Docker
container. Nel modulo **frontend** c’è la cartella **templates** per i file HTML necessariper creare l’interfaccia web.

**40** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Consegna

Step da Seguire (1)

- **●** Scaricate l’ISO di _Ubuntu 22.04.5_ (desktop) da[https://releases.ubuntu.com/jammy/](https://releases.ubuntu.com/jammy/)
- **●** Installarlo o come _macchina virtuale_ o come _dual boot_. Fate il test finale in unnuovo dual boot o in nuova macchina virtuale, non nel PC in cui avete sviluppato
il progetto, questo vi garantisce che funzionerà anche nel mio.

- **●** Tutte le _istruzioni_ seguenti vanno _eseguite_ dentro la _macchina virtuale_ o il dual_boot_.
- **●** Installate _docker_ e _docker compose_ con le versioni corrette (vedi GoogleClassroom e form di consegna).
- **●** Navigate da terminale nella _cartella_ del vostro _esonero_ esattamente come laconsegnerete, salvatene anche una copia dato che la dovete consegnare come è
prima di _eseguire_ i _test_ e non dopo

**41** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Consegna

Step da Seguire (2)

- **●** Eseguire il comando “_sudo chmod 777 -R ._” per dare i permessi necessari epotenzialmente altre cartelle necessarie.
- **●** Eseguire il comando “_sudo docker compose up --build_” e aspettare chel’inizializzazione termini
- **●** Eseguire il comando lo script di test che deve funzionare dando in output
- ALL TESTS PASS”
- **●** Consegnare la copia della cartella così come era prima di eseguire il testcompressa in un unico file _.zip_
**42** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Consegna

Report

- **●** Realizzare un _report_ in un file _report.pdf_ (anche questo incluso nell’archivio zip) di massimo _2 pagine_(fontsize 11) che descrive il vostro progetto:
**○** _Obiettivo del progetto_: Brevissimo riassunto della funzionalità del progetto (1-2 frasi)**○** _Organizzazione del codice_: Come è strutturato il vostro codice e una spiegazione della (singola)

responsabilità di ogni modulo**○** _Valutazione parser:_ Come sono stati valutati i parser e i risultati ottenuti

**○** Siete liberi di aggiungere anche altre sezioni (all’interno del limite totale di due pagine)**○** Il report può essere anche più breve di due pagine (apprezziamo la sintesi)

- **●** Il report deve essere scritto in Latex partendo da questo template online**○** Non includere l’abstract, partite direttamente con la prima _\begin{section}_
**○** Decommentare _\aclfinalcopy_ eliminando il % davanti a quella riga del file _.tex_ per poter mostrare ilvostro nome e cognome (altrimenti verrà mostrato “anonymous submission”)

- **●** Il progetto va consegnato su _Google Classroom_ (tramite l’apposito form)
**43** Navigli, Fedele - Laboratorio di Ingegneria Informatica

### Valutazione

- **●** L’esonero conterà metà del progetto
- **●** Saranno valutati:
**○** L’effettivo funzionamento del progetto (bloccante: non si passa se il progetto nonfunziona e non passa il test automatico)

**○** L’organizzazione del progetto (cartelle, file, ecc.)**○** La qualità e la pulizia del codice (inclusi i commenti e i type hint)

**○** La modularità del progetto: la corretta suddivisione in moduli**○** La corretta gestione dei casi limiti o di errore

**○** Il report

- **●** Il plagio (sia chi fa copiare che chi copia) porterà all’annullamento del progetto
Navigli, Fedele - Laboratorio di Ingegneria Informatica
