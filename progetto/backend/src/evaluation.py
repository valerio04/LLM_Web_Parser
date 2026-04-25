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
import asyncio
import markdown2
import re
import mistune
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import math



class Evaluator:
    """Classe per valutare la qualità del parsing."""

    def __init__(self):
        pass
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenizza il testo in token (parole).
        Parametri: text (str) - testo da tokenizzare
        Ritorna: List[str] - lista di token
        """
        #TODO: da lasciare o no la regex per togliere puntegiatura?

        text = re.sub(r'[^\w\s]', ' ', text)
        text = text.lower()  # Converti tutto in minuscolo per uniformità
        tokens = text.split()  # Semplice tokenizzazione basata su spazi
        return tokens
 
    @staticmethod
    def calculate_precision(extracted_tokens: List[str], gold_tokens: List[str]) -> float:
        """
        Calcola la precisione a livello token.
        Parametri: extracted_tokens, gold_tokens
        Ritorna: float - valore di precisione [0, 1]
        """
        ''' # Versione con SET (senza contare le ripetizioni):
        if len(extracted_tokens) == 0:
            return 0
        common_tokens = set(extracted_tokens) & set(gold_tokens)
        precision = len(common_tokens) / len(set(extracted_tokens))
        return precision'''
        
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
        '''# Versione con SET (senza contare le ripetizioni):
        if len(gold_tokens) == 0:
            return 0
        common_tokens = set(extracted_tokens) & set(gold_tokens)
        recall = len(common_tokens) / len(set(gold_tokens))
        return recall'''
        
        # Versione con Counter (conta le ripetizioni):
        
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
        
        Parametri:
            extracted_text (str) - testo estratto dal parser
            gold_text (str) - testo di riferimento (gold standard)
        
        Ritorna: Dict con chiavi 'precision', 'recall', 'f1'
        """
        #TODO: capire se va messa qui o in server

        # Pulisci il testo Markdown prima della valutazione
        cleaned_extracted_text = BaseParser.remove_markdown(extracted_text)
        print("=============testo dopo la pulizia da markdown:===============\n", cleaned_extracted_text[:1500])
        print("=============gold text:===============\n", gold_text[:1500])
        extracted_tokens = Evaluator.tokenize(cleaned_extracted_text)
        gold_tokens = Evaluator.tokenize(gold_text)
        precision = Evaluator.calculate_precision(extracted_tokens, gold_tokens)
        recall = Evaluator.calculate_recall(extracted_tokens, gold_tokens)
        f1 = Evaluator.calculate_f1(precision, recall)

        result = {"precision": precision,
                  "recall": recall,
                  "f1": f1}
        
        return result


#======================EXTRA====================


    #extra
    @staticmethod
    def jaccard_similarity(extracted_tokens: List[str], gold_tokens: List[str]) -> float:
        
        '''Misura quanto il vocabolario usato è lo stesso, senza contare le ripetizioni.'''
        
        set1 = set(extracted_tokens)
        set2 = set(gold_tokens)

        intersezione = len(set1.intersection(set2))
        unione = len(set1.union(set2))
        
        if unione == 0:
            return 0.0
        
        return intersezione / unione 



    #0 è identico, più alto è il numero più sono diversi
    @staticmethod    
    def levenshtein_dist(extracted_tokens: List[str], gold_tokens: List[str]) -> int:

        '''Misura il numero minimo di modifiche (inserimenti, cancellazioni, sostituzioni)
        necessarie per trasformare un testo nell'altro. 
        0 indica testi identici; valori più alti indicano maggiore differenza a livello di caratteri.'''

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

   

    

    @staticmethod    # è l unica cvhe mantiene la punteggiatura cosi da valutarla nella similarità in quanto analizza le stringhe intere e non i token
    def similarity_ratio(gold_text: str, extracted_text: str) -> float:
        return SequenceMatcher(None, gold_text, extracted_text).ratio()



    @staticmethod
    def lcs(gold_tokens: List[str], extracted_tokens: List[str]) -> int:
        # Calcola la lunghezza della sottosequenza comune più lunga
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
        
        '''Verifica se l'ordine delle parole è mantenuto'''

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
        
        '''parole	Capisce se il tema del discorso è lo stesso, 
        dando meno importanza alle parole comuni e più a quelle chiave.'''

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
        """
        if not text:
            return 0.0
        
        # Conta solo lettere e numeri
        alphanumeric_chars = len(re.sub(r'[^\w]', '', text))
        total_chars = len(text)
        
        return alphanumeric_chars / total_chars if total_chars > 0 else 0.0

    


    @staticmethod
    def x_eval_fast(extracted_text: str, gold_text: str) -> Dict[str, float]:
        
        # Esempio di valutazione combinata
        
        cleaned_extracted_text = BaseParser.remove_markdown(extracted_text)
        extracted_tokens = Evaluator.tokenize(cleaned_extracted_text)
        gold_tokens = Evaluator.tokenize(gold_text)
            
        
        cosine_sim = 0
        bp_extracted = 0
        bp_gold = 0
        bp_diff = 0

      
        
        # O(N + M) 
        cosine_sim = Evaluator.cosine_similarity_manual(gold_tokens, extracted_tokens)

        # O(N) + O(M)
        # Boilerplate Ratio: la calcoliamo per entrambi per vedere quanto è "sporco" il parser
        bp_extracted = Evaluator.boilerplate_ratio(cleaned_extracted_text)
        bp_gold = Evaluator.boilerplate_ratio(gold_text)
        # La differenza ci dice quanto boilerplate il parser ha lasciato dentro (o tolto troppo)
        bp_diff = abs(bp_extracted - bp_gold) 
        bp_fidelity = 1.0 - bp_diff

        return {
            "cosine_similarity": cosine_sim,
            "boilerplate_ratio_extracted": bp_extracted,
            "boilerplate_fidelity": bp_fidelity
        }




    @staticmethod
    def x_eval_complete(extracted_text: str, gold_text: str) -> Dict[str, float]:
        
        cleaned_extracted_text = BaseParser.remove_markdown(extracted_text)
        extracted_tokens = Evaluator.tokenize(cleaned_extracted_text)
        gold_tokens = Evaluator.tokenize(gold_text)
            
        # --- Metriche Veloci ---
        cosine_sim = Evaluator.cosine_similarity_manual(gold_tokens, extracted_tokens)
        
        # Boilerplate Ratio: la calcoliamo per entrambi per vedere quanto è "sporco" il parser
        bp_extracted = Evaluator.boilerplate_ratio(cleaned_extracted_text)
        bp_gold = Evaluator.boilerplate_ratio(gold_text)
        # La differenza ci dice quanto boilerplate il parser ha lasciato dentro (o tolto troppo)
        bp_diff = abs(bp_extracted - bp_gold) 
        bp_fidelity = 1.0 - bp_diff

        
        
        # --- Metriche Molto Lente ---
        levenshtein = Evaluator.levenshtein_dist(extracted_tokens, gold_tokens)
        rouge_l = Evaluator.rouge_l_simplified(gold_tokens, extracted_tokens)
       

        return {
            "levenshtein": levenshtein,
            "rouge_l": rouge_l,
            "cosine_similarity": cosine_sim, 
            "boilerplate_ratio_extracted": bp_extracted,
            "boilerplate_fidelity": bp_fidelity
        }

#=================fine extra======================




  
'''async def evaluate_gold_standard(gold_data: List[Dict]) -> Dict[str, Dict]:
    """
    Valuta tutto il Gold Standard.
    
    Parametri:
        gold_data (List[Dict]) - lista di entry Gold Standard con parser output
    
    Ritorna: Dict con risultati per ogni entry
    """
    if not gold_data:
        return {}

    result = dict()
    evaluator = Evaluator()

    for entry in gold_data:
        # Controllo sui campi obbligatori
        if not entry.get('title'):
            print(f"[WARNING] Entry senza titolo: {entry}")
            continue
        if not entry.get('gold_file'):
            print(f"[WARNING] Entry senza gold_file: {entry}")
            continue
        if not entry.get('url'):
            print(f"[WARNING] Entry senza URL: {entry}")
            continue

        # Seleziona il parser in base al dominio
        domain = entry.get('domain')
        if domain == "en.wikipedia.org":
            parser = WikipediaParser()
        elif domain == "www.ilpost.it":
            parser = IlPostParser()
        elif domain == "statmuse.com":
            parser = StatMuseParser()
        elif domain == "eur-lex.europa.eu":
            parser = EurLexParser()
        else:
            print(f"[WARNING] Dominio non riconosciuto: {domain}")
            continue

        try:
            # Estrai il testo usando il parser
            extracted_result = await parser.run(entry['url']) # usare async invece di asyncio.run(parser.run(entry['url'])) per evitare problemi di event loop
            extracted_text = extracted_result.get('parsed_text', '')

            # Controllo sul testo parsato
            if not extracted_text:
                print(f"[WARNING] Testo parsato vuoto per l'URL: {entry['url']}")
                continue

            # Controllo sull'esistenza del file gold standard
            script_dir = Path(__file__).parent.resolve()
            base_dir = script_dir.parent.parent
            gold_file_path = base_dir / "gs_data" / entry['gold_file']
            if not gold_file_path.exists():
                print(f"[WARNING] File gold standard mancante: {gold_file_path}")
                continue

            # Leggi il contenuto del file gold standard
            with open(gold_file_path, 'r', encoding='utf-8') as f:
                gold_text = f.read()
            
        
            
            print(f"=== PARSED ({entry['title']}) ===\n{extracted_text[:1000]}")
            print(f"=== GOLD ({entry['title']}) ===\n{gold_text[:1000]}")
            
           
            
            # Calcola le metriche
            token_eval_result = evaluator.token_level_eval(extracted_text, gold_text)
            print(f"[INFO] Valutazione completata per {entry['title']}: {token_eval_result}")
            result[entry['title']] = token_eval_result
        except Exception as e:
            print(f"[ERROR] Errore nella valutazione di {entry['title']}: {e}")
            result[entry['title']] = {"precision": 0, "recall": 0, "f1": 0}

    return result
'''

#funzione per parser offline, usando html gia scarivcati
async def evaluate_gold_standard(gold_data: List[Dict]) -> Dict[str, Dict]:
    if not gold_data:
        return {}

    result = dict()
    

    # Definisci base_dir UNA VOLTA, FUORI dal loop
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir.parent.parent

    

    for entry in gold_data:
        if not entry.get('title'):
            continue
        if not entry.get('gold_file'):
            continue
        if not entry.get('url'):
            continue

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
            # 1. Definizione percorsi e verifica Gold Standard
            html_file_path = base_dir / "gs_data" / entry['html_file']
            gold_file_path = base_dir / "gs_data" / entry['gold_file']

            if not gold_file_path.exists():
                print(f"[WARNING] Gold Standard mancante: {gold_file_path}")
                continue

            gold_text = gold_file_path.read_text(encoding='utf-8')
            extracted_result = None

            # 2. Tentativo di Parsing (Locale -> Online)
            if html_file_path.exists():
                try:
                    html_text = html_file_path.read_text(encoding='utf-8')
                    extracted_result = await parser.run_from_html(entry['url'], html_text)
                except Exception as e:
                    print(f"[WARNING] run_from_html fallito per {entry['url']}: {e}")

            # Se il locale non esiste o ha fallito, prova online
            if not extracted_result:
                try:
                    extracted_result = await parser.run(entry['url'])
                except Exception as e:
                    print(f"[ERROR] Anche il parsing online è fallito per {entry['url']}: {e}")

            # 3. Estrazione e validazione del testo
            extracted_text = (extracted_result or {}).get('parsed_text', '').strip()

            if not extracted_text:
                print(f"[WARNING] Testo estratto vuoto o nullo per: {entry['url']}")
                continue
            
            # 4. Valutazione
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






def generate_evaluation_report(results: Dict[str, Dict]) -> str:
    """
    Genera un report testuale dei risultati di valutazione.
    
    Parametri:
        results (Dict) - risultati della valutazione
    
    Ritorna: str - report formattato
    """
    report = "=" * 60 + "\n"
    report += "EVALUATION REPORT - Gold Standard\n"
    report += "=" * 60 + "\n\n"
    
    # Calcola statistiche per ogni entry
    precisions = []
    recalls = []
    f1_scores = []
    
    for entry_name, metrics in results.items():
        precision = metrics.get("precision", 0)
        recall = metrics.get("recall", 0)
        f1 = metrics.get("f1", 0)
        
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        
        report += f"Entry: {entry_name}\n"
        report += f"  Precision: {precision:.4f}\n"
        report += f"  Recall:    {recall:.4f}\n"
        report += f"  F1:        {f1:.4f}\n\n"
    
    # Aggiungi statistiche aggregate
    report += "-" * 60 + "\n"
    report += "OVERALL STATISTICS\n"
    report += "-" * 60 + "\n"
    
    if precisions:
        avg_precision = sum(precisions) / len(precisions)
        avg_recall = sum(recalls) / len(recalls)
        avg_f1 = sum(f1_scores) / len(f1_scores)
        
        report += f"Average Precision: {avg_precision:.4f}\n"
        report += f"Average Recall:    {avg_recall:.4f}\n"
        report += f"Average F1:        {avg_f1:.4f}\n"
        report += f"Total Entries:     {len(precisions)}\n"
    
    report += "=" * 60 + "\n"
    
    return report