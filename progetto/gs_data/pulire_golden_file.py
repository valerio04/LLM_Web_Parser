import re

class GoldenFileParser:
    def __init__(self):
        pass

    def clean_text(self, file_path):

        #apri il file e leggi il contenuto
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()  

            # Rimuovi parentesi quadre contenenti numeri o "edit"
            text = re.sub(r'\[\d+\]', '', text)  # Rimuovi [numero]
            text = re.sub(r'\[edit\]', '', text)  # Rimuovi [edit] (corretto: usa 'text' invece di 'content')
            #text = re.sub(r'\n', '', content)
            #text = text.replace('"', "'")
            #text= re.sub(r'\"',r'\'', text) #raddoppia le virgolette per evitare problemi con csv
            #sostituisci il testo originale con quello pulito
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

#questa funzione serve per levare [edit], e [numeri] per aiutare a fare il goldenstandrad
if __name__ == "__main__":
    parser = GoldenFileParser()
    parser.clean_text('progetto/gs_data/wikipedia_org/texts/gs_2_gold.txt')    