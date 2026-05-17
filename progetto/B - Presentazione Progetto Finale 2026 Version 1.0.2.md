Laboratorio di Ingegneria Informatica

Progetto Finale / Progetti Personalizzati

Prof. Roberto **Navigli**Dott. Domenico **Fedele**

Progetto Obiettivo complessivo

- **●** _Costruire una_ pipeline end-to-end _per_ acquisire _e_ analizzare documenti _dasorgenti_ web _eterogenee_
- **●** _Applicazione reale_: il vostro lavoro contribuirà direttamente alla versione chatbotdell’LLM nazionale _Minerva_ (sviluppato da _Sapienza NLP_ e _Babelscape_)
**○** Stiamo per lanciare una versione che cerca sul Web e recupera i risultati dalmotore di ricerca, li parsa e li utilizza per dare una risposta aggiornata

- **●** È una bella occasione per lavorare su un progetto concreto nel campodell’Intelligenza Artificiale, con un impatto reale e immediato
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

Progetto Architettura del sistema

**4** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Formazione dei gruppi

- **●** _Il_ progetto finale _si svolge in_ gruppi da 3 persone
- **●** I _gruppi_ definiti nel primo form pubblicato su Classroom per _l’esonero_ vanno
mantenuti _anche nel_ progetto _finale_

- **●** Eventuali richieste di _gruppi_ con numero _ridotto_ di studenti_, ben motivate ed_
**eccezionali, saranno valutate** caso per caso (non implicano una semplificazione

del progetto)

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Informazioni generali

- _●_ Consegna
**○** Il progetto completo va consegnato al massimo _8 giorni prima di ciascun appello_

**○** _Esempio:_ appello il 25 dicembre → consegna entro il 17 dicembre (mezzanotte circa)

**○** Il progetto va consegnato su Google _Classroom_ tramite l’apposito _form_, che sarà pubblicato nelle

settimane precedenti alla scadenza

- **●** Il progetto _estende_ quanto fatto con _l’esonero_, che non è obbligatorio ma copre una parte sostanziale del
lavoro. Chi ha sostenuto l’esonero segue le stesse regole di consegna del progetto completo, con il

vantaggio di avere già una parte del lavoro svolta.

- **●** Accesso alla Tesi
**○** Tutti gli studenti possono utilizzare il progetto svolto come tesi triennale_, applicando una_

personalizzazione che verrà illustrata successivamente

**○** _I migliori_ progetti _dell’_esonero 1 _potranno accedere a un_ esonero 2/progetto di tesi

personalizzato _in_ NLP

**○** Entrambe le modalità saranno presentate nel dettaglio al termine della presentazione

**6** Navigli, Fedele - Laboratorio di Ingegneria Informatica

## Progetto

Navigli, Fedele - Laboratorio di Ingegneria Informatica **7**

Progetto

Obiettivi

1. **Implementazione completa dei parser per tutti i domini web assegnati**Parser dedicati per estrarre il testo rilevante dalle pagine dei domini assegnati
2. **Costruzione di un Gold Standard (GS)**Dataset di riferimento costruito manualmente, contenente il testo corretto da confrontare con l’output del parser
3. **Valutazione automatica dei parser con metriche specifiche**Misurazione della qualità del parsing tramite metriche quantitative
4. **Valutazione automatica dei parser con LLM-as-Judge**Utilizzo di un LLM per validare la qualità del parsing
5. **Database**Memorizzazione e gestione input/output parsing
6. **Esposizione funzionalità via API REST**Endpoint per parsing, accesso ai dati e valutazione automatica
7. **Web UI Completa**Interfaccia per gestire parsing, evaluation e DB
8. **Containerizzazione** con **Docker**Ambiente multi container eseguibile in modo controllato e uniforme
**8** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Task

- **●** _Parser_: implementare un parser Python specifico per le pagine di ciascun dominio webassegnato (es. it.wikipedia.org)
- **●** Data un’_URL_ proveniente da uno dei _domini assegnati_ il parser deve _estrarre_ le seguenti
informazioni_:_

**○** "_url_": "[https://...",](https://...",)

**○** "_domain_": "esempio.it",

**○** "_title_": "Titolo della pagina web",

**○** "_html_text_": "Testo estratto della pagina web grezzo (HTML senza filtri), su cui è

possibile rieseguire il parsing per ottere di nuovo parsed_text”

**○** "_parsed_text_": "Testo estratto pulito senza tag HTML o di altro genere, in formato

MARKDOWN_”_

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Libreria per il parsing - Crawl4AI

- **●** _Per il_ download _e il_ parsing _delle_ pagine web _potete utilizzare la_ libreria Crawl4AI _con_
configurazione personalizzata _per ogni_ dominio

- **●** Crawl4AI _è una_ libreria _Python_ open-source _progettata per il_ web scraping _orientato_
all'AI

- **●** Trasforma qualsiasi _pagina web_ in dati _strutturati_ (_Markdown_, JSON, screenshot,
HTML) _pronti_ per essere consumati da _modelli linguistici_ (LLM)

- _●_ Sfruttate la libreria per estrarre direttamente il **Markdown** ed eventualmente
ripulirlo ulteriormente

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Libreria per il parsing - Crawl4AI

- **●** Potete utilizzare _librerie aggiuntive_, se ritenute utili, come ad esempio
BeautifulSoup

- **●** Tuttavia, è _preferibile_ e particolarmente apprezzato l’impiego di _Crawl4AI_ per il
**parsing**, individuando una **configurazione efficace** e adatta al caso d’uso del

progetto.

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

Obiettivo 1: Parser per Domini Web Crawl4AI - Esempio download HTML

- **●** È possibile _scaricare solo_ il contenuto _HTML_ senza alcun tipo di processamento, utile in fase di
**evaluation** e per la costruzione del GS

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 1: Parser per Domini Web Crawl4AI - Esempio di parsing da stringa HTML

- **●** È possibile _parsare_ contenuto _HTML statico_ precedentemente _scaricato_, questo vi permette anche di
gestire al meglio le fasi di **evaluation** per un sito che cambia molto rapidamente

- **●** La libreria Crawl4AI ha numerose _funzionalità_ che vi consiglio di esplorare nella
sua documentazione

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

- **●** Il _parsing_ delle pagine provenienti dal dominio _wikipedia.org_ è _uguale per tutti_
In inglese se, ordinando i cognomi del gruppo in ordine alfabetico, il primo cognome inizia

con una lettera “dispari”, ovvero A, C, E, G, I, K, M, O, Q, S, U, W, Y; in italiano altrimenti

- **●** _3 domini aggiuntivi_ saranno assegnati _casualmente_ ad ogni gruppo:
**○** Wikipedia _e_ TUTTI _i_ domini aggiuntivi _devono essere_ parsati _correttamente_

(implementare 4 parser, sfruttare la programmazione ad oggetti)

**○** _Più domini_ riuscirete a parsare correttamente _maggiore_ sarà la _valutazione_

**○** I _domini_ aggiuntivi _assegnati_ per _l’esonero_ sono gli _stessi_ del progetto finale

(vedere Assegnazione Domini)

**○** _Per i_ nuovi gruppi _i_ domini aggiuntivi _saranno_ assegnati _mediante un apposito_ script

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Assegnazione dei domini da parsare

Script automatico per i NUOVI GRUPPI

- **●** Script _automatico per_ l’assegnazione _dei_domini SOLO PER I NUOVI GRUPPI_:_
Link allo script: domains_by_surname.py

- **●** Rimpiazzate:
```
"Cognome 1", "Cognome 2", "Cognome 3"
```

**c**on i vostri cognomi ed eseguite:

```
“python domains_by_surname.py”
```

il codice stamperà la vostra **Wikipedia** e l’**ID**dei **3 domini** aggiuntivi

- **●** Ricavate il _nome_ del _dominio_ dalla _listadomini assegnati_ usando gli _ID_ che vi ha
_restituito lo script:_Link: Lista Domini & URL di Esempio

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

- **●** Gold Standard (GS)_: per ogni_ dominio assegnato_, selezionare almeno_ 10 URL
rappresentative (pagine di tipo diverso, con contenuti vari, no home page)

- **●** _Maggiore_ sarà la _qualità_ del _GS maggiore_ sarà la _valutazione._ Un GS di buona qualità è
quello che ci permette di valutare al meglio un parser

- **●** Per ogni URL: _aprire la pagina nel_ browser_, copiare_ manualmente _il solo_ testo
**informativo** (no pubblicità, contenuti collaterali o ripetuti in ogni pagina, ecc.)

**○** _Includere_: titolo e corpo dell'articolo

**○** _NON includere_: menu di navigazione, footer, sidebar, banner pubblicitari

- **●** Utilizzare il _GS_ per valutare la _qualità_ dei vostri _parser_
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard per Domini Assegnati Formato del Gold Standard

- **●** Salvare i _GS_ in file _JSON,_ uno per ogni dominio e nel vostro _Database_
Un’**entry** del vostro **GS** contiene le seguenti informazioni:

**○** "_url_": "[https://...",](https://...",)

**○** "_domain_": "esempio.it",

**○** "_title_": "Titolo della pagina web",

**○** "_html_text_": “Testo estratto della pagina web grezzo (HTML senza filtri), su cui è

possibile rieseguire il parsing per ottenere di nuovo _parsed_text_ da confrontare

con _gold_text,_ molto utile in fase di evaluation” (vedere download html e parsing

da stringa HTML)

**○** "gold_text": "Testo estratto pulito senza tag HTML o di altro genere,

non in formato MARKDOWN”

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard Esempio estrazione info - Wikipedia

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard Esempio estrazione info - Wikipedia

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard Esempi di GS

- **●** Esempi di _elementi_ del _GS_ per alcune pagine di _Wikipedia_
- **●** Dominio 1: en.wikipedia.org**○** Pagina 1: en.wikipedia.org/wiki/Minerva -> GS
**○** Pagina 2: en.wikipedia.org/wiki/BabelNet -> GS

- **●** Dominio 2: it.wikipedia.org**○** Pagina 1: it.wikipedia.org/wiki/Minerva -> GS
**○** Pagina 2: it.wikipedia.org/wiki/BabelNet -> GS

- **●** _Per i_ domini aggiuntivi _dovete_ valutare voi _quali sono le_ informazionirilevanti _per una_ pagina _web, ma in caso di_ dubbi _potete_ scrivere _su_
Classroom

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 2: Gold Standard Trovare pagine interessanti per domini aggiuntivi

- **●** Per trovare pagine interessanti per uno specifico dominio, si possonoseguire gli _esempi_ presenti nell’_elenco completo dei domini_ condiviso
_su_ Classroom

- **●** Per trovare _altre tipologie_ di _pagine_ interessanti si può usare_l’operatore_ _“site: <sito web>”_ di Google per _limitare_ la _ricerca_ sul
browser **ad un** sito specifico

- **●** L’idea è cercare _contenuti utili_ e informativi, adatti ad un _LLM_ che cercasul Web per rispondere ad una domanda di un utente
- **●** _Alcuni Esempi_ con Wikipedia in Italiano (_it.wikipedia.org_):**○** _“_città italiane _site:__it.wikipedia.org_”
**○** “energia nucleare _site:__it.wikipedia.org_”**○** “Dante Alighieri _site:__it.wikipedia.org_”

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 3: Valutazione Parser con Metriche

Valutare Qualità Parsing

- **●** _Valutare_ la _qualità_ dell'_output_ prodotto dai _parser_ implementati
- **●** La _valutazione_ sarà effettuata in prima battuta tramite _metriche quantitative_
**implementate da voi**, usate come **indicatori** oggettivi della **qualità** del parsing

- **●** I _Gold Standard_ (GS) prodotti saranno _utilizzati_ come _dataset_ di _test_ per il confronto
con l’output del parser

- **●** _Una_ metrica _di valutazione è_ obbligatoria _e_ uguale per tutti_:_ _token_level_eval_
- **●** Ci aspettiamo che esploriate e implementiate in autonomia _ulteriori tecniche di_
**valutazione** (sperimentate, cercate online, chiedete agli LLM!)

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 3: Valutazione Parser con Metriche

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

Obiettivo 3: Valutazione Parser con Metriche

Come Interpretare la ‘_token_level_eval’_ F1

Fascia Range F1 Interpretazione

**Scarso** < 0.6 Il parser perde contenuto rilevante o introduce molto rumore

**Medio** 0.6 – 0.80 Contenuto principale presente ma con omissioni o boilerplate non rimosso

**Buono** > 0.80 Il parser cattura la maggior parte del testo rilevante con poco rumore

**NOTA**: data la semplicità di questa metrica, "Buono” è condizione necessaria manon sufficiente per considerare il parser affidabile. Verificate anche manualmente.

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 3: Valutazione Parser con Metriche

Come gestire confronto tra output in Markdown e Gold Standard

- **●** Essendo _l’output_ del _parser_ in _Markdown_ e il _GS_ in _raw text_ vanno _normalizzati_ prima della valutazionerimuovendo markdown e link
- _●_ Pur non coprendo tutti i casi esistenti, una possibile soluzione per **rimuovere** il **Markdown**SOLO in fase di valutazione con la _token_level_eval_ è la seguente:
```
def remove_markdown(md: str) -> str:
"""
Rimuove il Markdown da una stringa, restituendo solo il testo pulito.
Usa la libreria mistune per convertire il Markdown in HTML, poi BeautifulSoup per estrarre solo il testo.
"""
html = mistune.html(md)
soup = BeautifulSoup(html, "html.parser")
# rimuove i tag lasciando il testo esattamente in-place (nessun separatore aggiunto, mantiene punteggiatura)
for tag in soup.find_all(True):
tag.unwrap()
text = re.sub(r'[ \t]+', ' ', str(soup)) # collassa spazi orizzontali (non \n)
text = re.sub(r'\n+', '\n', text) # collassa nuove linee multiple in una sola
return text.strip()
```

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: Valutazione Parser con LLM

LLM-as-Judge

- **●** L'idea dell’_LLM-as-Judge_ è di utilizzare un _Large Language Model_ come giudice
automatico per **valutare** la qualità del **testo** estratto dai **parser**

- **●** Il _funzionamento_ è il seguente:
**○** Il _testo parsato_ e il _Gold Standard_ vengono inviati all'_LLM_ tramite un _prompt_

strutturato

**○** Il _prompt_ chiede al modello di _valutare_ la qualità del _testo estratto_

confrontandolo _con il_ Gold Standard_,_ identificando _eventuali_ problemi _come_

boilerplate residuo, testo troncato o rumore

**○** L_'LLM restituisce_ un _giudizio_ strutturato (es. score e feedback)

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: Valutazione Parser con LLM

Pipeline di Valutazione con LLM

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: Valutazione Parser con LLM

Esempio di Prompt per il Judge

- **●** Il _prompt_ deve essere _strutturato_ in modo da _guidare l'LLM_ a restituire un giudizio in
formato **JSON**.

- **●** Un _esempio_ molto semplice e generico:
- Valuta la qualità del seguente testo estratto da una pagina web. Testo estratto dal parser:
{parsed_text} Testo di riferimento (Gold Standard):

{gold_text} Rispondi SOLO con un JSON nel seguente formato:

{

- score": <tra 1 e 5>,
- feedback": <breve descrizione della qualità del testo> } ”
- **●** È obbligatorio _gestire_ il _caso_ in cui l'_LLM non rispetti_ il _formato_ atteso,
**prevedendo un** fallback appropriato

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: Valutazione Parser con LLM

Tecnologie

- **●** Per far girare il modello in locale è _obbligatorio_ utilizzare _Ollama_, che verrà
approfondito a lezione

- **●** I modelli da utilizzare devono essere _modelli piccoli_
compatibili _con la_ CPU _del vostro_ PC

- **●** Non aspettatevi risultati perfetti_: con un modello_
più grande la qualità migliorerà sensibilmente, ma

per il progetto base sono più che sufficienti

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 4: Valutazione Parser con LLM

Modelli Da Utilizzare

- **●** Abbiamo selezionato _5 modelli_ adatti ad esecuzioni su _CPU_ (anche di un notebook):
Modello Developer Parametri RAM stimata Comando Ollama

**gemma4:e2b** _Google_ 2.3B attivi ~2GB ollama pull gemma4:e2b

| llama3.2:3b | Meta | 3B | ~2GB ollama pull llama3.2:3b |
| --- | --- | --- | --- |
| phi4-mini | Microsoft | 3.8B | ~3GB ollama pull phi4-mini |
| qwen3:4b | Alibaba | 4B | ~3GB ollama pull qwen3:4b |

**ministral-3:3b** _Mistral AI_ 3.85B ~3GB ollama pull ministral-3:3b

- **●** Sta a voi _valutare_ quale _modello utilizzare_ tra questi _5_ in base alla _qualità_ del _giudizio_ ottenuto
- **●** Vi consigliamo di fare _test_ su tutti e _5 i modelli_ prima di scegliere quello definitivo da usare nel
progetto.

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 5: Database

Scopo del Database

- **●** _Il_ database relazionale (SQL) _ha il ruolo di_ centralizzare _e rendere_ persistenti _tutte le_
informazioni prodotte _dalla_ pipeline _di_ parsing_:_

**○** I _contenuti grezzi_ scaricati dalle sorgenti web (_HTML_), utili in fase di evaluation

**○** I _testi parsati_ e puliti prodotti dai parser

**○** I _Gold Standard_ costruiti manualmente

**○** I risultati delle _valutazioni_ automatiche con _metriche_

**○** I _giudizi_ qualitativi prodotti dall'_LLM Judge_

- **●** _Senza_ un _database_, ogni _risultato_ sarebbe _temporaneo_ e andrebbe perso al riavvio del sistema
oppure andrebbe gestito _tramite file_

- **●** _Il_ DB _permette di_ consultare_,_ confrontare _e_ analizzare _i dati nel tempo_
tramite le **API REST** e la **Web UI**

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 5: Database

Schema del Database

- **●** _Lo_ schema _del_ database _è a vostra_ discrezione _fatta_ eccezione _per_ 2 tabelle _e sarà_ oggetto _di_
valutazione

- **●** Un possibile _esempio_ di come potrebbe essere _organizzato il DB_:
**○** _Risorse web_: URL, dominio, contenuto HTML grezzo

[tabella obbligatoria: web_resources]

**○** _Documenti parsati_: output del parser

**○** _Gold Standard_: testo di riferimento costruito manualmente

[tabella obbligatoria: gold_standard]

**○** _Valutazioni_: risultati delle varie valutazioni automatiche

**○** _Giudizi LLM_: score e verdetto del judge

- **●** Le _tabelle_ devono essere _collegate_ tra loro tramite _primary key_ e f_oreign key_, garantendo
_l'_integrità referenziale _dei dati_

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 5: Database

**Schema del Database -** web_resources **&** gold_standard

- **●** _Per rendere i_ test automatici _robusti, si definiscono_ 2 tabelle obbligatorie con nomi fissi_:_
- - **web_resources** (contiene le risorse web scaricate da utilizzare in locale)
- - _url_: URL della pagina, chiave primaria **●** _La_ _relazione_ _tra le due tabelle è_- _domain_: dominio della pagina _uno-a-uno__: ogni entry del gold standard_
- - _title_: titolo della pagina
- **-** _html_text_**: contenuto HTML grezzo** è associato a una risorsa web
- - **created_at**: data di acquisizione
- - **gold_standard** (contiene il testo di riferimento costruito manualmente)
- **●** _I_ test _automatici_ possono alterare
- - _url_: chiave primaria e esterna verso web_resources
- - _gold_text_: testo corretto estratto manualmente _queste tabelle e_ **sfruttarle** _per forzare_- _created_at_: data di creazione _l’utilizzo dell’_**HTML locale**
- **●** Le _altre tabelle_ del progetto restano _libere_ e possono essere progettate dal gruppo in
base alla propria architettura

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 5: Database

Popolamento Iniziale del Database

- **●** All'avvio _del_ sistema_, il_ database _deve essere_ popolato _con i_ dati necessari _al funzionamento della_
pipeline di parsing_:_

**○** I _Gold Standard_ costruiti manualmente devono essere _caricati automaticamente_ nel _DB_, in

modo che siano subito **disponibili** per le **valutazioni** tramite le API REST e la Web UI

**○** L'_HTML grezzo_ scaricato durante la _costruzione_ del _Gold Standard_ deve essere anch'esso

salvato nel DB, in modo da poter **rieseguire** il **parsing** in qualsiasi momento e **confrontare** il

risultato con il **gold_text**

**○** Il _caricamento_ deve avvenire tramite uno _script_ di _inizializzazione_ che viene eseguito

automaticamente al **primo avvio**

**NOTA**: i file _JSON_ del _Gold Standard_ prodotti, contenenti sia il gold_text che l'HTML grezzo, devono

_essere_ inclusi _nel_ progetto

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 5: Database

Tecnologie

- **●** _Per la_ gestione _del_ database _è_ obbligatorio _utilizzare:_
**○** _MariaDB_ come sistema di gestione del _database_

relazionale

**○** MariaDB Connector/Python _come_ libreria _per_

l'interazione _tra_ Python _e il database_

- **●** _MariaDB_ girerà in un container _Docker dedicato_,
coordinato tramite Docker Compose insieme agli altri

container del sistema

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST Overview API REST

Implementare con **FastAPI** un **WEB Server** per accedere ai seguenti endpoint:

- **●** _POST /parse_: esegue il parser per un documento
- **●** _GET /domains_: restituisce la lista dei domini assegnati
- **●** _GET /gold_standard_: restituisce il gold standard per un documento
- **●** _GET /gold_standard_urls_: restituisce tutti gli URL del GS
- **●** _POST /evaluate_: dato risultato parsing e gs restituisce le metriche di evaluation
- **●** _POST /evaluate_judge_: dato risultato parsing e gs restituisce l’evaluation del judge
- **●** _GET /full_gs_eval_: restituisce l’evaluation aggregata su tutto il GS
- **●** POST /add_web_resource & /add_gold_standard_: aggiungono dati al DB_
- **●** DELETE /web_resource & /gold_standard_: rimuovono dati dal DB_
- **●** _GET /db_stats_: restituisce stats generali calcolate dai dati nel DB
- **●** _GET /db_schema:_ restituisce lo schema del DB
- **●** _GET /status_: restituisce lo stato dei componenti del sistema
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST Requisiti API REST

- **●** Usare _FastAPI_ e _Pydantic_ per validazione I/O
- **●** _I_ formati di input/output _devono_ rispettare _esattamente la_ specifica_, perché saranno_
testati automaticamente

- **●** _Gestire_ esplicitamente _errori_ come dominio non supportato e URL irraggiungibile
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST POST /parse

- **●** Seleziona automaticamente il parser correttoin base al dominio in _"url"_ ed esegue il _parsing_
sull’HTML scaricato al momento. Se viene _//_ **OUTPUT - JSON**_{_passato **“local = true”**, usa la pagina nel DB _"url": "[https://...",_](https://...",_)

**senza effettuare il download (usare** _"url"_ **per** "domain": "esempio.it",**cercarla nel DB)** "title": "Titolo estratto dalla pagina web",

- html_text": "Html estratto dalla pagina web, input del parser",
- **●** _Input__:_ _{"url": str, “local”: Optional[bool]}_ "parsed_text": "Testo pulito, output del
- **●** _Output__: oggetto JSON nel formato indicato_ parser di riferimento, informato MARKDOWN"
- **●** Errori_:_ _}_
**○** Se il dominio non è supportato

**○** Se l'URL è irraggiungibile/non è nel DB

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST GET /domains

- **●** Restituisce la lista dei domini supportati
dal sistema (es. it.wikipedia.org) _//_ **OUTPUT - JSON**

{

- **●** _Input__: nessuno_ "domains": [
- **●** _Output_: oggetto JSON nel formato indicato _"esempio_1.it",_
- esempio_2.it", …
] }

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST GET /gold_standard

- **●** Restituisce l’entry del GS per l’URL dato in
input. Caricando le informazioni dal DB _//_ **OUTPUT - JSON**

{

- **●** _Input__:_ _"url": str_ "url": "[https://...",](https://...",)
- domain": "esempio.it",
- **●** _Output__: oggetto JSON nel formato indicato._ "title": "Titolo estratto dalla pagina web",
- html_text": "Html estratto dalla pagina web, input del parser",
- **●** _Errori__:_ "gold_text": "Testo pulito, estratto
**○** _Se il dominio non è supportato_ manualmente dalla pagina web,no MARKDOWN"

**○** L'URL non è nel GS (non è nel DB) _}_

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST

GET /gold_standard_urls _//_ **OUTPUT - JSON**

{

- **●** Restituisce la lista degli url di un GS per _“gold_standard_urls”:[_
un dominio specifico. Caricando le info dal

**DB** "[https://esempio_1.com/pagina_1",](https://esempio_1.com/pagina_1",)

- [https://esempio_1.com/pagina_1",](https://esempio_1.com/pagina_1",) …
- **●** _Input__:_ "domain": str
- **"[https://esempio_1.com/pagina_n"**(lo](https://esempio_1.com/pagina_n"**(lo) stesso usato nella lista get domains) **]**
- **●** _Output_: oggetto JSON nel formato _}_
indicato.

- **●** Errori_:_
**○** Se il dominio non è supportato.

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST POST /evaluate

- **●** Dato il risultato del parsing di un _//_ _OUTPUT - JSON__{_
documento e il corrispettivo testo del GS _“token_level_eval”: {_

| restituisce le metriche di evaluation | "precision": 0.87, |
| --- | --- |
| Rimuovere il markdown in fase di evaluation, | "recall": 0.91, |

- _"f1": 0.89,_confrontare solo il contenuto. _},_
- x_eval”:{
- **●** _Input__:_ {"parsed_text": str, "gold_text": str} _..._
- **●** _Output_: oggetto JSON nel formato indicato. _}}_
token_level_eval **con** precision, recall **e** f1 **è**

obbligatoria

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST POST /evaluate_judge

- **●** Dato il risultato del parsing di un documento _//_ _OUTPUT - JSON__{_
e il corrispettivo testo del GS restituisce la

| valutazione del judge. | “model_name”: “minerva:7b”, "judge_score”: 1, # intero tra 1 e 5 |
| --- | --- |
| Rimuovere il markdown in fase di evaluation, | "judge_feedback": “Feedback testuale |

confrontare solo il contenuto. _restituito dal modello”,_

- altre info” : . . . }
- **●** _Input__:_ {"parsed_text": str, "gold_text": str}
- **●** _Output_: oggetto JSON nel formato indicato.
- **●** Potete aggiungere _altri campi_ per evaluation
più strutturate ma “**model_name”**,

- **“**judge_score” **e “**judge_feedback” **sono**
obbligatori

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST GET /full_gs_eval

- _●_ Restituisce la _valutazione complessiva_ del _Gold Standard_ _//_ **OUTPUT - JSON**per il dominio dato in input. Esegue il _parsing_ di tutte le _{_
sue entry e aggrega i risultati tramite **media** delle **metriche** _“token_level_eval”: {_e del **judge_score**, calcolate sui singoli elementi del GS. _"precision": 0.87,_

Rimuovere il markdown in fase di evaluation, confrontare _"recall": 0.91,_solo il contenuto. _"f1": 0.89,_

Usare **HTML statico** salvato nel **DB**, ma calcolare il resto. _},_

| ● Input (lo stesso usato nella lista get domains) : "domain": str | “judge_score” : 2.6, |
| --- | --- |
| ● Output : oggetto JSON nel formato indicato. | “x_eval”:{ |

…

- **●** Errori_:_
}

**○** Se il dominio non è supportato.

}

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST POST /add_web_resource & /add_gold_standard

- **●** POST /add_web_resource
| ○ Aggiunge una risorsa web nella tabella web_resources con l'HTML fornito in input | // OUTPUT - JSON |
| --- | --- |
| ○ ○ Input Output : {"url": str, "html_text": str} : oggetto JSON nel formato indicato | {"status": "ok"} # oppure “error” |

- **●** POST /add_gold_standard
**○** Aggiunge un'entry nella tabella _gold_standard_, la

**web_resource** corrispondente deve già esistere nel _//_ **OUTPUT - JSON**

DB

**○** _Input_: _{"url": str, "gold_text": str}_ _{"status": "ok"} # oppure “error”_**○** _Output_: oggetto JSON nel formato indicato

**○** _Errori_: URL non presente in _web_resources_

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST DELETE /web_resource & /gold_standard

- **●** DELETE /web_resource
| ○ Rimuove una risorsa web dalla tabella web_resources e a cascata tramite FK, il | // OUTPUT - JSON |
| --- | --- |
| ○ gold_standard associato Input : {"url": str} | {"status": "ok"} # oppure “error” |

**○** _Output_: oggetto JSON nel formato indicato

- **●** DELETE /gold_standard
_○_ Rimuove solo l'entry dalla tabella gold_standard, _//_ **OUTPUT - JSON**

lasciando intatta la web_resource associata

**○** _Input_: _{"url": str}_ _{"status": "ok"} # oppure “error”_**○** _Output_: oggetto JSON nel formato indicato

- **●** _Errori_: URL non presente nel GS
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST _//_ **OUTPUT - JSON**

{

- _"_web_resources_": {_
**GET /db_stats** "esempio_1.it": 15,

- esempio_2.it": 25 },
- **●** Restituisce _stats_ e _valutazione_ complessiva dei _dati_ che _"__gold_standard__": {_
sono **salvati** nel **DB** per ogni dominio. Le metriche _"esempio_1.it": 15,_

- esempio_2.it": 25
obbligatorie e il judge_score devono essere riportati _},_

- _"_avg_eval_": {_
sempre in questa statistica. Questa funzione utilizza _"esempio_1.it": {_

- token_level_eval": { “f1”: 0.82, ...
**tutti** dati pre-calcolati e salvati nel DB**.** _"metric_2": { “score”: 0.91}_

},

- esempio_2.it": {
- **●** _Input:_ _nessuno_ "token_level_eval": { “f1”: 0.99, ...
- metric_2": { “score”: 0.95}
- **●** _Output_: oggetto JSON nel formato indicato. _}_
},

- _"_avg_eval_judge_": {_
- esempio_1.it": {
- judge_score": 2.4,
- metric_2": 0.50 },
| NOTA : ricordate di popolare il DB in fase di inizializzazione | "esempio_2.it": { |
| --- | --- |
| dei vari docker | "judge_score": 4.7, |

- metric_2": 0.80 }
_}_Navigli, Fedele - Laboratorio di Ingegneria Informatica _}_

Obiettivo 6: API REST GET /db_schema

_//_ OUTPUT - JSON_{_

- web_resources": {
- **●** Restituisce lo schema del DB. Le
| tabelle con le relative colonne, | "url": "domain": "varchar(2048), PK", "varchar(255)", |
| --- | --- |
| specificando tipo dei dati, chiavi | “title”: "varchar(2048)”, |
| primarie (PK), chiavi esterne (FK) | "html_text": "longtext", "created_at": "datetime" |

},

- gold_standard": {
- url": "varchar(2048), PK, FK(web_resources.url)",
| ● Input : nessuno | "gold_text": "longtext", |
| --- | --- |
| ● Output : oggetto JSON nel formato | }, "created_at": "datetime" |

indicato _...}_

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 6: API REST GET /status

- **●** _Restituisce lo_ stato dei componenti del sistema_._
I valori possibili per ogni componente sono _"ok"_ se il _//_ **OUTPUT - JSON**

componente è raggiungibile e funzionante, _"error"_

altrimenti _{_

- backend": "ok",
- database": "error",
| ● Input: nessuno | "ollama": "ok" |
| --- | --- |
| ● Output : oggetto JSON nel formato indicato. | } |

L'endpoint restituisce sempre HTTP 200, è il contenuto

del JSON a indicare lo stato reale dei componenti, non il

codice HTTP

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 7: Web UI Interfaccia Web

- **●** _L'interfaccia web_ permette di _interagire_ con l'intera _pipeline_ senza utilizzaredirettamente le API REST
- **●** Composta da una _home page_ e _tre sezioni principali_, ognuna con unaresponsabilità specifica:
**○** _testare_ il parser su un URL**○** _costruire_ e gestire il _Gold Standard_

**○** _monitorare_ le _statistiche_ aggregate del sistema

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 7: Web UI Interfaccia Web - Home Page

Pagina principale dell’interfaccia web:

- **●** Navigazione _verso le_ 3 pagine
- **●** _Matricole_ studenti del gruppo
- **●** _Stato_ del sistema (backend, db e ollama)
- _●_ **Domini** supportati dal sistema
**NOTA**: le immagini della UI mostrate sono

puramente esemplificative, avete totale libertà

nella scelta di stile e layout del frontend

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 7: Web UI Interfaccia Web - Pagina Parser & Evaluation

_Pagina di_ valutazione qualitativa _dei_ parser_:_

- **●** Permette di _testare_ un _parser_ inserendo un _URL_ oselezionare quelli nel GS dal menu a tendina
- **●** Modalità _Live/Local_: scarica la pagina in temporeale dal web oppure usa quella nel DB
- **●** Mostra il _confronto_ tra _html_text_ grezzo e_parsed_text_ in Markdown
- **●** Se l’_URL_ è presente nel _Gold Standard_**○** _Confronta_ anche il risultato con il _gold_text_
**○** _Visualizza_ tutte le _metriche_ di valutazioneimplementate

**○** Include anche una _valutazione_ tramite LLM_Judge_, con score e feedback testuale

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 7: Web UI Interfaccia Web - Pagina Gold Standard Builder

Pagina che permette di **gestire** il **Gold Standard** nel DB,aggiungendo e rimuovendo dati:

- **●** _Selezione_ del _dominio_ tra quelli supportati
- **●** Inserimento dell'URL: il sistema _scarica l'HTML_ elo mostra nella pagina. È possibile copiare l’HTML
statico mostrato per aprirlo in un browser per copiare manualmente il testo informativo per

costruire i GS

- **●** Area di testo per _inserire_ il _gold_text_ copiato dallapagina
- **●** Al submit, _HTML_ e _gold_text_ vengono salvatiinsieme nel _database_
- **●** Inoltre, la pagina mostra la _lista_ degli _URL_ già_presenti_ nel GS per il dominio selezionato, con
possibilità **di** eliminare **ogni entry**

Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 7: Web UI Interfaccia Web - Pagina Stats

Pagina che mostra una **panoramica** aggregata di **tutti** i **domini** in un’unica vista:

- **●** _Risorse nel DB_: numero di _entry_ in web_resources e gold_standard per ciascundominio
- **●** _Metriche medie_ calcolate sul Gold Standard di ciascun dominio
- **●** _Judge score medio_ valutazione qualitativa aggregata per ciascun dominio
- **●** Siete liberi di aggiungere _ulteriori statistiche_ che ritenete utili
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 7: Web UI Requisiti Generali

- _●_ Tecnologie obbligatorie: **Jinja2** per il templating e **HTML**/**CSS** per il frontend.È possibile utilizzare tecnologie aggiuntive purché non appesantiscano inutilmente il
sistema

- **●** La _UI_ gira in un _container Docker_ dedicato coordinato tramite _Docker Compose_
- **●** Tutta la _logica_ passa _esclusivamente_ tramite le _API REST_ del _backend._ Nella specificadel backend ci sono tutte le funzioni necessarie.
- **●** La UI deve _gestire_ e mostrare chiaramente tutti gli _errori_ restituiti dalle _API_(es. dominio non supportato, URL non raggiungibile, URL non presente nel DB)
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Obiettivo 8: Containerizzazione Architettura multi-container con Docker Compose

Il sistema è composto da **4 container Docker** orchestrati tramite **Docker Compose**, avviabili tramite

docker-compose.yaml **con un unico comando:** ”docker compose up --build”

- _●_ **Backend**: server FastAPI con i parser, le API REST e la logica di evaluation.
Esposto sulla porta **8003**

- **●** _Frontend_: server Jinja2/HTML per la Web UI. Esposto sulla porta _8004_
- **●** _Database:_ MariaDB con i dati persistenti caricati all’avvio del sistema.
Esposto sulla porta **3306**

- **●** _Ollama_: server LLM locale con il modello importato automaticamente all'avvio.
Esposto sulla porta **11434**

**NOTA**: Le _porte_ indicate sono _obbligatorie_ e devono essere _esposte_ esattamente come specificato.

I test automatici le useranno per comunicare con il sistema. Usare solo _path relativi_,

nessun path assoluto.

Navigli, Fedele - Laboratorio di Ingegneria Informatica

# Consegna

Navigli, Fedele - Laboratorio di Ingegneria Informatica **61**

Consegna

progetto/

Struttura delle Directory del Progetto **├──** _docker-compose.yaml_

**├──** domains.json

- **●** _docker-compose.yaml_: avvia l'intero sistema con un **├──** _backend/_**│ ├──** _Dockerfile_solo comando (tutti e 4 i docker)
**│ ├──** requirements.txt

| ● domains.json : lista dei domini assegnati | │ └── src/ |
| --- | --- |
| ● backend/ parser e la valutazione del parsing : server FastAPI, codice necessario per i | │ ├── └── frontend/ … (file .py) |
| ● frontend/ e codice necessario per la UI : interfaccia web HTML/Jinja2 con template | │ │ ├── ├── Dockerfile requirements.txt |
| ● gs_data/ : Gold Standard JSON per ciascun dominio | │ │ └── └── src/ … (file .py) |
| ● mariadb_data/ di MariaDB : eventuali file necessari per il database | │ ├── └── gs_data/ templates/ |
| ● ollama_data /: eventuali file necessari per Ollama | │ ├── dominio_x_gs.json |
| ● report.pdf : max 2/3 pagine, redatto in LaTeX | │ ├── └── ollama_data/ dominio_y_gs.json |

**├──** mariadb_data/**├──** report.pdf

**62** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Consegna Singolo Zip

- **●** Consegnare un _singolo file zip_ che è lo zip della _cartella_ del vostro _progetto_,con il nome che include tutte le matricole dei membri del gruppo:
matricola1_matricola2_matricola3_lab_progetto.zip

- **●** La _struttura_ delle _directory_ all’interno del file zip deve essere in linea con quella_specificata_ nelle _slide precedenti_
- **●** Potete usare più file, cartelle e sottocartelle se li reputate utili a organizzaremeglio il progetto
**63** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Test automatico

Test del Backend

- **●** Vi forniremo nei prossimi giorni su Google Classroom uno _script_ che avvierà un _testautomatico_ di tutti gli _endpoint_ definiti nella specifica del _WEB Server_ del progetto
- **●** Dovete _esporre_ il _backend_ del vostro _progetto_ sulla porta _8003_. Lo script di testing,eseguito fuori dai Docker container del vostro progetto, deve poter accedere a quella porta
per eseguire il test automatico (non modificare la porta nello script di test)

- **●** Dovete _esporre_ il _frontend_ del vostro _progetto_ sulla porta _8004_ (anche se non vieneesplicitamente testato)
- **●** _Dovete_ esporre _anche_ MariaDB 3306 _e_ Ollama 11434
- **●** Il test deve funzionare subito dopo il comando: _docker compose up --build_Non ci devono essere passaggi intermedi tra questa inizializzazione automatica e
l’esecuzione dello script di test

**64** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Test automatico

Test del Backend

- **●** Dovete riuscire ad _eseguire_ l’intero _script_ di _test_ senza modifiche arrivando a vedereil messaggio che indica che tutti i test sono stati superati:
- **“ALL TESTS PASS!”**Indispensabile prima di effettuare la consegna
- **●** _Non_ dovete _modificare_ lo _script_ di _test_, dato che noi lo useremo esattamente cosìcom’è per valutare i progetti
- **●** Se pensate di aver _trovato_ un _errore_ nello script di test _comunicarlo_ tramite_Google Classroom_
**65** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Test automatico

Test del Frontend

- **●** Ricordate di _testare_ voi stessi anche il _frontend_ del vostro _progetto_, dopo avereseguito i test automatici con successo e prima di consegnare
- **●** Il frontend _non viene valutato automaticamente_ dallo script di test
- **●** _Non_ dovete _consegnare_ lo _script di test_ insieme al vostro progetto(è uguale per tutti)
**66** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Test automatico

Docker Compose

- **●** Il vostro _progetto_ verrà _eseguito_ tramite il comando
- **“docker compose up --build”**eseguito da terminale nella directory del file
**docker-compose.yaml**che deve essere nella root del progetto, come indicato nelle slide precedenti

- **●** Il file _docker-compose.yaml_ contiene le istruzioni necessarie per avviare l’interoprogetto con il comando _“docker compose up --build”_
**○** I due moduli _frontend_ e _backend_ separati in cartelle diverse, ognuna con i suoi file_requirements.txt_ e _Dockerfile_, necessari per la costruzione dei rispettivi Docker

container

**○** I due servizi _MariaDB_ e _Ollama_

**67** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Consegna

Step Fondamentali - Docker Compose

- **●** Il comando _docker compose up --build_ deve funzionare su un qualsiasi computer, quindinon si possono usare path assoluti ma solo path relativi.
Prima di consegnare spostate il vostro progetto in un'altra cartella nel vostro computer econtrollare che _docker compose up --build_ funzioni ancora ***senza cambiare nulla*** per

assicurarvi che funzioni anche sul nostro computer che useremo per le correzioni.

- **●** Potete sviluppare su Mac/Windows ma noi eseguiremo il comando _docker compose up--build_ su Linux (Ubuntu), quindi se state sviluppando su Mac/Windows dovete
controllare che questo comando funzioni correttamente anche su **Ubuntu** prima diconsegnare (usate una **macchina virtuale**, vedere slide successive)

- **●** Ricordate di eseguire anche il test automatico e di testare il frontend dopo ognuno diquesti test
**68** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Consegna

Step Fondamentali - Macchina Virtuale

- **●** Scaricate l’ISO di _Ubuntu 22.04.5_ (desktop) da[https://releases.ubuntu.com/jammy/](https://releases.ubuntu.com/jammy/)
- **●** Installatelo o come _macchina virtuale_ o come _dual boot_. Fate il test finale in unnuovo dual boot o in nuova macchina virtuale, non nel PC in cui avete sviluppato
il progetto, questo vi garantisce che funzionerà anche nel nostro ambiente.

- **●** Tutte le _istruzioni_ seguenti vanno _eseguite_ dentro la _macchina virtuale_ o il dual_boot_.
- **●** Installate _docker_ e _docker compose_ con le versioni corrette (vedi GoogleClassroom e form di consegna).
- **●** Navigate da terminale nella _cartella_ del vostro _esonero_ esattamente come laconsegnerete, salvatene anche una copia dato che la dovete consegnare come è
prima di _eseguire_ i _test_ e non dopo

**69** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Consegna

Step Fondamentali - Permessi, Test e Consegna Zip

- **●** Eseguire il comando “_sudo chmod 777 -R ._” per dare i permessi necessari epotenzialmente altre cartelle necessarie.
- **●** Eseguire il comando “_sudo docker compose up --build_” e aspettare chel’inizializzazione termini
- **●** Eseguire lo script di test che deve funzionare dando in output
- ALL TESTS PASS”
- **●** Consegnare la copia della cartella così come era prima di eseguire il testcompressa in un unico file _.zip_
- **●** Il progetto va consegnato su Google Classroom tramite l’apposito form, chesarà pubblicato nelle settimane precedenti alla scadenza
**70** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Report del Progetto

Informazioni Generali

- **●** Realizzare un _report_ in un file _report.pdf_ (anche questo incluso nell’archivio zip) di massimo _2 pagine_(fontsize 11) che descrive il vostro progetto:
**○** _Obiettivo del Progetto_: Brevissimo riassunto della funzionalità del progetto (1-2 frasi)**○** _Organizzazione del Codice_: Come è strutturato il vostro codice e una spiegazione delle

responsabilità dei vari moduli (no snippet di codice)**○** _Valutazione Parser:_ Analisi dei dati, tecniche di valutazione dei parser, risultati ottenuti ed

eventuali problematiche riscontrate**○** _Valutazione dei Judge_: Selezione del modello e del prompt ideale

**○** _Organizzazione del DB_: Come avete strutturato il vostro database

- **●** _Bonus/Extra_: Qualora desideriate inserire contenuti ulteriori rispetto ai requisiti del progetto, è possibileaggiungere una _terza pagina_ finale in una sezione intitolata "_Bonus/Extra_" (ad esempio per
sottodomini/domini aggiuntivi o altre aggiunte rilevanti).

- **●** Il report deve essere scritto in _LaTeX_ partendo da questo template online: _link_**○** Non includere l’abstract, partite direttamente con la prima _\begin{section}_
**○** Decommentare _\aclfinalcopy_ eliminando il % davanti a quella riga del file _.tex_ per poter mostrare ilvostro nome e cognome (altrimenti verrà mostrato “anonymous submission”)

**71** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Valutazione

Criteri di valutazione

- **●** Saranno valutati:
**○** L’effettivo funzionamento del progetto (bloccante: non si passa se il progetto nonfunziona e non passa il test automatico)

**○** La qualità dei parser e dei GS**○** La corretta progettazione del DB e del prompt per il Judge

**○** L’organizzazione del progetto (cartelle, file, ecc.)**○** La qualità e la pulizia del codice (inclusi i commenti e i type hint)

**○** La modularità del progetto: la corretta suddivisione in moduli e l’uso della OOP**○** La corretta gestione dei casi limiti o di errore

**○** La qualità della UI**○** Il report

- **●** Il plagio (sia chi fa copiare che chi copia) porterà all’annullamento del progetto
Navigli, Fedele - Laboratorio di Ingegneria Informatica

### Progetto Personalizzato Tesi

Riservato ai progetti migliori

Navigli, Fedele - Laboratorio di Ingegneria Informatica **79**

Progetti personalizzati

Indicazioni generali per i progetti migliori

- **●** Gli studenti con i migliori homework 1 (vedi ranking) potranno decidere dioptare per uno dei progetti personalizzati
- **●** La scelta è possibile solo entro la fine del corso
- **●** E’ possibile consegnare il progetto personalizzato a ogni appello come il progettobase
- **●** Il progetto deve comunque essere prima discusso direttamente con il prof.Navigli
- **●** Il progetto potrà essere presentato direttamente come tesi di laurea triennale
- **●** E’ possibile creare un sottogruppo del gruppo iniziale o discutere la formazionedi nuovi gruppi, sempre a partire dai migliori studenti
Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Personalizzato Tesi (1b)

Introduzione

- _●_ **LLM2Graph:** trasformare l’output di un LLM in un grafo navigabile
**81** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Personalizzato Tesi (1b)

Introduzione

- _●_ **LLM2Graph:** trasformare l’output di un LLM in un grafo navigabile
**○** Estrarre entità dal testo**■** con LLM, spaCy o modello NER

**○** Estrarre relazioni tra entità, ovvero triple soggetto - relazione - oggetto**■** con LLM o sistemi di relation extraction

**○** Normalizzare e disambiguare le entità**■** Collegare entità duplicate o ambigue a identificativi unici (Wikidata QID o BabelNet synset)

**○** Convertire le triple in un grafo**■** Salvare nodi e archi in Neo4j o NetworkX

**○** Validare il grafo**■** Controllare inconsistenze, relazioni inventate, nodi duplicati e triple non supportate dal testo

**○** Costruire una visualizzazione navigabile**■** Usare strumenti come Neo4j Bloom, Cytoscape.js, D3.js, GraphDB o Streamlit + PyVis

**○** Aggiungere interazione e ricerca**■** Filtri per tipo di nodo, ricerca testuale, espansione dei vicini e visualizzazione delle fonti

**○** Valutare il risultato

**82** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Personalizzato Tesi (2b)

Agenti per Minerva

- **●** Sviluppare agenti da integrare nel framework agentico di Minerva:
**○** Calcolatrice**○** Matematica simbolica (es. con SymPy)

**○** Analisi dati in Python (con pandas)**○** Visualizzazione dati (grafici)

**○** Esecuzione codice Python**○** Query SQL (linguaggio naturale → database)

**○** Pulizia dati**○** Ricerca web

**○** Riassunto notizie**○** Interrogazione knowledge graph

**○** Multi-API (meteo, finanza, ecc.)**○** Pianificazione

**○** Monitoraggio finanza (azioni/crypto)**○** Generazione doc

**○** Generazione fogli excel

**83** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Personalizzato Tesi (3b)

Introduzione

- **●** Uno studio sperimentale dei _vector database_
**○** FAISS**○** Chroma

**○** Weaviate**○** Milvus

**○** Qdrant**○** Vespa

**○** Mongo DB Atlas Vector Search

- **●** Valutazione di prestazioni
**○** In termini di velocità**○** In termini di spazio in RAM / disco

**○** Per grandi / grandissimi volumi

**84** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Personalizzato Tesi (4b)

Chat Bot con info dal web

- **●** Chat Bot - Di Dominio
**○** Consentire all'utente di porre al proprio sistema una query**○** Assicurarsi che la query dell'utente possa essere risolta sfruttando i domini disponibili

**○** Ricercare online pagine (nei domini disponibili) che possano contenere informazioni utili**○** Parsare le pagine (sfruttando i parser dell'esonero) e fornire ad un LLM query+pagine

**○** Restituire risposte all'utente

**85** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Progetto Personalizzato Tesi (4b)

Chat Bot con info dal web - Sfide

- **●** Chat Bot - Di Dominio
**○** _Comprensione e disambiguazione della domanda_Gestire richieste ambigue e chiedere eventualmente chiarimenti all’utente

**○** _Filtro delle domande fuori dominio_Definire criteri di rigetto e valutare il comportamento in caso di domanda non accettabile

**○** _Recupero e selezione delle fonti_Individuare pagine web pertinenti e classificarle in base alla loro utilità (valutare anche altre domini)

**○** _Gestione del contesto e del prompt_Riassumere o selezionare contenuti rilevanti per non saturare la context window delle modello

**○** _Qualità e affidabilità della risposta_Citare le fonti, stimare l’affidabilità e gestire risposte parziali o incerte

**86** Navigli, Fedele - Laboratorio di Ingegneria Informatica

Per le tesi personalizzate

Incontro previsto per il 3 giugno

Per chi vuole consegnare il progetto da luglio in

avanti (non essendoci i tempi tecnici per un

incontro relativo a chi consegnerà a giugno)

Navigli, Fedele - Laboratorio di Ingegneria Informatica
