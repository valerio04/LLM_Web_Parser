"""
Modulo di valutazione per il parsing.
Implementa metriche di valutazione a livello token (token_level_eval).
"""

from typing import Dict, List
from pathlib import Path

from aiohttp import request
from .parsers.parser_wikipedia import WikipediaParser
from .parsers.parser1 import IlPostParser
from .parsers.parser2 import StatMuseParser
from .parsers.parser3 import EurLexParser
from .parsers.base_parser import BaseParser
from collections import Counter
import re
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import math



class Evaluator:
    
    """
    Classe per valutare la qualità del parsing.
    """

    def __init__(self):
        pass
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenizza il testo in token (parole).
        Parametri: text (str) - testo da tokenizzare
        Ritorna: List[str] - lista di token
        """   
        text = re.sub(r'[^\w\s]', ' ', text)
        text = text.lower()  
        tokens = text.split()  
        return tokens
 
    @staticmethod
    def calculate_precision(extracted_tokens: List[str], gold_tokens: List[str]) -> float:
        """
        Calcola la precisione a livello token.
        Parametri: extracted_tokens, gold_tokens
        Ritorna: float - valore di precisione [0, 1]
        """
        # Versione con Counter (conta le ripetizioni):
        if len(extracted_tokens) == 0:
            return 0.0
        extracted_count = Counter(extracted_tokens)
        gold_count = Counter(gold_tokens)
        common = sum((extracted_count & gold_count).values())
        precision = common / len(extracted_tokens)
        return precision
        
    
    @staticmethod
    def calculate_recall(extracted_tokens: List[str], gold_tokens: List[str]) -> float:
        """
        Calcola il recall a livello token.
        Parametri: extracted_tokens, gold_tokens
        Ritorna: float - valore di recall [0, 1]
        """
        if len(gold_tokens) == 0:
            return 0.0
        extracted_count = Counter(extracted_tokens)
        gold_count = Counter(gold_tokens)
        common = sum((extracted_count & gold_count).values())
        recall = common / len(gold_tokens)
        return recall

    @staticmethod
    def calculate_f1(precision: float, recall: float) -> float:
        """
        Calcola l'F1 score combinando precisione e recall.
        Parametri: precision, recall
        Ritorna: float - F1 score [0, 1]
        """  
        if precision + recall == 0:
            return 0
        f1 = (2 * precision * recall) / (precision + recall)
        return f1

    @staticmethod
    def token_level_eval(extracted_text: str, gold_text: str) -> Dict[str, float]:
        """
        Esegue la valutazione completa a livello token.
        Calcola precision, recall, F1.
        Parametri: extracted_tokens, gold_tokens
        Ritorna: Dict con chiavi 'precision', 'recall', 'f1'
        """
        # Pulisce il testo Markdown prima della valutazione
        cleaned_extracted_text = BaseParser.remove_markdown(extracted_text) 
        # tookenizza entrambi i testi
        extracted_tokens = Evaluator.tokenize(cleaned_extracted_text)
        gold_tokens = Evaluator.tokenize(gold_text)
        # Calcola le metriche
        precision = Evaluator.calculate_precision(extracted_tokens, gold_tokens)
        recall = Evaluator.calculate_recall(extracted_tokens, gold_tokens)
        f1 = Evaluator.calculate_f1(precision, recall)

        result = {"precision": precision,
                  "recall": recall,
                  "f1": f1}
        
        return result


#======================EXTRA====================

    #Metriche aggiuntive di valutazione per analizzare diversi aspetti della qualità del parsing

    
    @staticmethod    
    def levenshtein_dist(extracted_tokens: List[str], gold_tokens: List[str]) -> int:
        '''
        Misura il numero minimo di modifiche (inserimenti, cancellazioni, sostituzioni)
        necessarie per trasformare un testo nell'altro.
        parametri: extracted_tokens, gold_tokens
        ritorna: float - valore di distanza di Levenshtein [0, 1]
        '''
        if not extracted_tokens and not gold_tokens:
            return 1.0
        
        max_len = max(len(extracted_tokens), len(gold_tokens))
        if max_len == 0:
            return 1.0


        # Operiamo direttamente su liste di token (parole)
        if len(extracted_tokens) < len(gold_tokens):
            extracted_tokens, gold_tokens = gold_tokens, extracted_tokens

        if len(gold_tokens) == 0:
            return len(extracted_tokens)

        previous_row = list(range(len(gold_tokens) + 1))
        for i, ta in enumerate(extracted_tokens, start=1):
            current_row = [i]
            for j, tb in enumerate(gold_tokens, start=1):
                insertions = previous_row[j] + 1
                deletions = current_row[j-1] + 1
                substitutions = previous_row[j-1] + (0 if ta == tb else 1)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return 1.0 - (previous_row[-1] / max_len)  # Normalizza in [0, 1]



    @staticmethod
    def lcs(gold_tokens: List[str], extracted_tokens: List[str]) -> int:
        '''
        Calcola la lunghezza della sottosequenza comune più lunga
        parametri: gold_tokens, extracted_tokens
        ritorna: int - lunghezza della sottosequenza comune più lunga
        '''
        m, n = len(gold_tokens), len(extracted_tokens)
        L = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    L[i][j] = 0
                elif gold_tokens[i-1] == extracted_tokens[j-1]:
                    L[i][j] = L[i-1][j-1] + 1
                else:
                    L[i][j] = max(L[i-1][j], L[i][j-1])
        return L[m][n]

    @staticmethod
    def rouge_l_simplified(gold_tokens: List[str], parsed_tokens: List[str]) -> float:
        '''
        Verifica se l'ordine delle parole è mantenuto
        parametri: gold_tokens, parsed_tokens
        ritorna: float - valore di ROUGE-L [0, 1]
        '''

        if not gold_tokens or not parsed_tokens:
            return 0.0
        
        lcs_count = Evaluator.lcs(gold_tokens, parsed_tokens)
        
        # Calcoliamo la F-measure di ROUGE-L
        precision = lcs_count / len(parsed_tokens)
        recall = lcs_count / len(gold_tokens)
        
        if (precision + recall) == 0: return 0.0
        return (2 * precision * recall) / (precision + recall)


    
    

    @staticmethod
    def cosine_similarity_manual(gold_tokens: List[str], parsed_tokens: List[str]) -> float:
        '''
        Capisce se il tema del discorso è lo stesso, 
        dando meno importanza alle parole comuni e più a quelle chiave.
        parametri: gold_tokens, parsed_tokens
        ritorna: float - valore di cosine similarity [0, 1]
        '''

        # Creiamo i "vettori" contando le frequenze delle parole
        vec1 = Counter(gold_tokens)
        vec2 = Counter(parsed_tokens)

        # Troviamo l'unione di tutte le parole (vocabolario)
        words = set(vec1.keys()) | set(vec2.keys())
        
        # Calcoliamo il prodotto scalare (dot product)
        dot_product = sum(vec1.get(w, 0) * vec2.get(w, 0) for w in words)
        
        # Calcoliamo le magnitudo (norme) dei vettori
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if not norm1 or not norm2:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    

    

    @staticmethod
    def boilerplate_ratio(text: str) -> float:
        """
        Calcola il rapporto tra caratteri alfanumerici e lunghezza totale.
        Un ratio basso indica molto 'rumore' (simboli, spazi eccessivi, boilerplate).
        parametri: text (str) - testo da analizzare
        ritorna: float - rapporto alfanumerico [0, 1]
        """
        if not text:
            return 0.0
        
        # Conta solo lettere e numeri
        alphanumeric_chars = len(re.sub(r'[^\w]', '', text))
        total_chars = len(text)
        
        return alphanumeric_chars / total_chars if total_chars > 0 else 0.0

    


    @staticmethod
    def x_eval_fast(extracted_text: str, gold_text: str) -> Dict[str, float]:
        """
        Esegue una valutazione rapida combinando metriche veloci come cosine similarity e boilerplate ratio.
        Parametri: extracted_text (str), gold_text (str) 
        Ritorna: Dict con chiavi 'cosine_similarity', 'boilerplate_ratio, 'boilerplate_fidelity'
        """
        # pulisce e tokenizza entrambi i testi        
        cleaned_extracted_text = BaseParser.remove_markdown(extracted_text)
        extracted_tokens = Evaluator.tokenize(cleaned_extracted_text)
        gold_tokens = Evaluator.tokenize(gold_text)
            
        #Metriche Veloci
        cosine_sim = 0
        bp_extracted = 0
        bp_gold = 0

        #N e M sono il numero di token nei due testi
        # O(N + M) 
        cosine_sim = Evaluator.cosine_similarity_manual(gold_tokens, extracted_tokens)

        # O(N) + O(M)
        # Boilerplate Ratio: la calcoliamo per entrambi per vedere quanto è "sporco" il parser
        bp_extracted = Evaluator.boilerplate_ratio(cleaned_extracted_text)
        bp_gold = Evaluator.boilerplate_ratio(gold_text)
        # La differenza ci dice quanto boilerplate il parser ha lasciato dentro (o tolto troppo)
        bp_fidelity = 1.0 - abs(bp_extracted - bp_gold)

        return {
            "cosine_similarity": cosine_sim,
            "boilerplate_ratio_extracted": bp_extracted,
            "boilerplate_fidelity": bp_fidelity
        }




    @staticmethod
    def x_eval_complete(extracted_text: str, gold_text: str) -> Dict[str, float]:
        """
        Esegue una valutazione completa combinando metriche veloci come cosine similarity e boilerplate ratio
        con metriche più lente ma più precise come Levenshtein e ROUGE-L.
        Parametri: extracted_text (str), gold_text (str) 
        Ritorna: Dict con chiavi 'levenshtein', 'rouge_l', 'cosine_similarity', 'boilerplate_ratio, 'boilerplate_fidelity'
        """
        # pulisce e tokenizza entrambi i testi
        cleaned_extracted_text = BaseParser.remove_markdown(extracted_text)
        extracted_tokens = Evaluator.tokenize(cleaned_extracted_text)
        gold_tokens = Evaluator.tokenize(gold_text)
            
        # --- Metriche Veloci O(N + M)---
        #cosine similarity
        cosine_sim = Evaluator.cosine_similarity_manual(gold_tokens, extracted_tokens)
        # Boilerplate Ratio
        bp_extracted = Evaluator.boilerplate_ratio(cleaned_extracted_text)
        bp_gold = Evaluator.boilerplate_ratio(gold_text)
        # La differenza ci dice quanto boilerplate il parser ha lasciato dentro (o tolto troppo)
        bp_diff = abs(bp_extracted - bp_gold) 
        bp_fidelity = 1.0 - bp_diff

        # --- Metriche Lente O(N * M) ---
        #lenshtein
        levenshtein = Evaluator.levenshtein_dist(extracted_tokens, gold_tokens)
        #rouge_l
        rouge_l = Evaluator.rouge_l_simplified(gold_tokens, extracted_tokens)
       

        return {
            "levenshtein": levenshtein,
            "rouge_l": rouge_l,
            "cosine_similarity": cosine_sim, 
            "boilerplate_ratio_extracted": bp_extracted,
            "boilerplate_fidelity": bp_fidelity
        }

#=================fine extra======================



#funzione per parser offline, usando html gia scarivcati
async def evaluate_gold_standard(gold_data: List[Dict]) -> Dict[str, Dict]:
    '''
    Esegue il parsing dell'URL selezionato, recupera il gold standard associato e calcola le metriche di valutazione.
    Restituisce un dizionario con i risultati di valutazione per ogni entry.
    Parametri: gold_data (List[Dict]) - lista di dizionari con chiavi 'title', 'url', 'html_file', 'gold_file', 'domain'
    Ritorna: Dict[str, Dict] - dizionario con chiavi il titolo dell'entry e valori un altro dizionario con le metriche di valutazione (precision, recall, f1, x_eval)
    '''
    if not gold_data:
        return {}

    result = dict()
    
    # percorso del file di questo script e del progetto
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent

    # Itera su ogni entry del gold standard
    for entry in gold_data:
        if not entry.get('title'):
            continue
        if not entry.get('gold_file'):
            continue
        if not entry.get('url'):
            continue
        
        # Selezione del parser in base al dominio
        domain = entry.get('domain')
        if "en.wikipedia.org" in domain:
            parser = WikipediaParser()
        elif "www.ilpost.it" in domain:
            parser = IlPostParser()
        elif "www.statmuse.com" in domain:
            parser = StatMuseParser()
        elif "eur-lex.europa.eu" in domain:
            parser = EurLexParser()
        else:
            print(f"[WARNING] Dominio non riconosciuto: {domain}")
            continue

        try:
            # Definizione percorsi e verifica Gold Standard
            html_file_path = base_dir / "gs_data" / entry['html_file']
            gold_file_path = base_dir / "gs_data" / entry['gold_file']

            if not gold_file_path.exists():
                print(f"[WARNING] Gold Standard mancante: {gold_file_path}")
                continue

            gold_text = gold_file_path.read_text(encoding='utf-8')
            extracted_result = None

            # Tentativo di Parsing Locale 
            if html_file_path.exists():
                try:
                    html_text = html_file_path.read_text(encoding='utf-8')
                    extracted_result = await parser.run_from_html(entry['url'], html_text)
                    print(f"[INFO] Parsing LOCALE completato per {entry['url']}")
                except Exception as e:
                    print(f"[WARNING] run_from_html fallito per {entry['url']}: {e}")

            # Se il locale non esiste o ha fallito, prova online
            if not extracted_result:
                try:
                    extracted_result = await parser.run(entry['url'])
                    print(f"[INFO] Parsing ONLINE completato per {entry['url']}")
                except Exception as e:
                    print(f"[ERROR] Anche il parsing online è fallito per {entry['url']}: {e}")

            # Estrazione e validazione del testo
            extracted_text = (extracted_result or {}).get('parsed_text', '').strip()

            if not extracted_text:
                print(f"[WARNING] Testo estratto vuoto o nullo per: {entry['url']}")
                continue
            
            # Valutazione
            token_eval_result = Evaluator.token_level_eval(extracted_text, gold_text)
            x_eval_result = {}
            x_eval_result = Evaluator.x_eval_fast(extracted_text, gold_text)
            print(f"[INFO] {entry['title']}: {token_eval_result} | x_eval: {x_eval_result}")
           
            merged = {
                "precision": token_eval_result.get("precision", 0),
                "recall": token_eval_result.get("recall", 0),
                "f1": token_eval_result.get("f1", 0),
                "x_eval": x_eval_result,
            }
            result[entry['title']] = merged
            
        except Exception as e:
            print(f"[ERROR] Errore per {entry['title']}: {e}")
            result[entry['title']] = {"precision": 0, "recall": 0, "f1": 0, "x_eval": {}}

    return result

