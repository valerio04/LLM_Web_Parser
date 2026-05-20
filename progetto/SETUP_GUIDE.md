# 🚀 Guida Setup Progetto - Laboratorio Ingegneria Informatica

## 📥 PRIMO SETUP (Una sola volta dopo aver scaricato il progetto)

### **Step 1: Clona il repository**
```bash
git clone https://github.com/valerio04/progetto_lab_info.git
cd progetto_lab_info/progetto
```

### **Step 2: Crea l'ambiente virtuale**
```bash
python3 -m venv venv
```

### **Step 3: Attiva l'ambiente virtuale**
```bash
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```
Dovresti vedere `(venv)` all'inizio del terminale.

### **Step 4: Installa le dipendenze**
```bash
pip install -U -r backend/requirements.txt  # Installa e aggiorna le dipendenze
```

### **Step 5: Configura Playwright e Crawl4AI**
```bash
pip install -U "crawl4ai[setup]"  # Assicura il supporto per il setup
crawl4ai-setup                     # Configura i browser headless
```

### **Step 6: Installa i prerequisiti di sistema per MariaDB**
MariaDB Connector/Python richiede il pacchetto di sistema `libmariadb-dev` per funzionare correttamente. Installa il prerequisito con il seguente comando:
```bash
sudo apt update
sudo apt install libmariadb-dev
```

### **Step 7: Verifica l'installazione di MariaDB Connector/Python**
Dopo aver installato il prerequisito, verifica che il pacchetto Python `mariadb` sia installato correttamente:
```bash
pip install mariadb
python3 -c "import mariadb; print('MariaDB Connector installed successfully')"
```
Se vedi il messaggio "MariaDB Connector installed successfully", l'installazione è completa.

**Fatto!** Setup completato! 🎉

---

## 💻 LAVORO QUOTIDIANO (Ogni volta che lavori al progetto)

### **Ogni giorno: Attiva l'ambiente**
```bash
cd /path/to/progetto_lab_info/progetto
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

Vedrai `(venv)` nel terminale = sei pronto a lavorare ✅

### **Modifica il codice**
- Edita i file `.py`, `.json`, ecc.
- Testa localmente

### **Finito? Fai commit e push**
```bash
git add .
git commit -m "Descrizione delle modifiche"
git push origin main
```

### **Quando finisci di lavorare: Disattiva l'ambiente**
```bash
deactivate
```

---

## 🆕 SE UN COMPAGNO HA AGGIUNTO NUOVE DIPENDENZE

Quando fai `git pull` e vedi che `requirements.txt` è cambiato:
```bash
git pull origin main
pip install -U -r backend/requirements.txt  # Installa e aggiorna le nuove dipendenze
```

---

## 📋 Note importanti

- ❌ **NON** fare `git add venv/` - Il `.gitignore` lo esclude automaticamente
- ❌ **NON** fare `git add __pycache__/` - Escluso dal `.gitignore`
- ✅ **Fai sempre commit** dei file: `.py`, `.json`, `Dockerfile`, `requirements.txt`, `*.md`
- � **Se aggiungi una libreria nuova:**
  ```bash
  pip install nome_libreria
  pip freeze > backend/requirements.txt  # Aggiorna il file
  git add backend/requirements.txt && git commit -m "Aggiunta nuova dipendenza"
  ```

---

## 🐛 Troubleshooting

### "venv not found" o "(venv) non appare"
```bash
source venv/bin/activate
```

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -U -r backend/requirements.txt
```

### "playwright: command not found"
```bash
playwright install
```

### "Permission denied" (su Linux/Mac)
```bash
sudo chmod 755 venv/bin/activate
source venv/bin/activate
```

### "RequestsDependencyWarning: urllib3 o charset_normalizer non supportati"
```bash
pip install -U requests urllib3 charset_normalizer
```

---

## 📚 Struttura del progetto

```
progetto/
├── backend/                    # API REST (FastAPI)
│   ├── src/
│   │   └── server.py          # Server principale
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Web UI (per dopo)
│   ├── src/
│   ├── templates/
│   ├── Dockerfile
│   └── requirements.txt
├── gs_data/                    # Gold Standard (dati di test)
│   ├── en_wikipedia_gs.json
│   └── ...
├── docker-compose.yaml
├── domains.json
└── .gitignore
```

---

https://eur-lex.europa.eu/IT/legal-content/summary/exchange-rate-mechanism-between-the-euro-and-other-participating-national-currencies.html?fromSummary=14

**Per domande o problemi: Contattare il team!** 💬

---

## **Gestione del container MariaDB**

## 🐳 Avviare il progetto con Docker Compose

### **Build (prima volta o dopo modifiche ai Dockerfile)**
```bash
docker compose build
```

### **Avvio in background**
```bash
docker compose up -d
```

### **Avvio con build automatico**
```bash
docker compose up -d --build
```

### **Avvio in foreground (per vedere i log in tempo reale)**
```bash
docker compose up
```

### **Stop dei container (senza rimuovere i volumi)**
```bash
docker compose down
```

### **Stop + rimozione volumi (cancella dati persistenti)**
```bash
docker compose down -v
```

### **Stato dei servizi**
```bash
docker compose ps
```

### **Log di tutti i servizi**
```bash
docker compose logs -f
```

### **Log di un singolo servizio (es. backend)**
```bash
docker compose logs -f backend
```

#### **Chiudere il container senza cancellare i dati**
Per fermare il container MariaDB senza eliminare i dati persistenti:
```bash
docker compose stop mariadb
```
Questo comando ferma il servizio MariaDB, ma i dati rimangono salvati nel volume `mariadb_data`.

#### **Chiudere il container e cancellare i dati**
Per fermare il container e rimuovere i dati:
```bash
docker compose down -v
```
Il flag `-v` rimuove anche i volumi associati, cancellando tutti i dati salvati.

#### **Avviare il container MariaDB**
Per avviare il container MariaDB:
```bash
docker compose up -d mariadb
```
Il flag `-d` esegue il container in background.


