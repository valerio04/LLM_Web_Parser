"""
Modulo di valutazione per il parsing.
Implementa metriche di valutazione a livello token (token_level_eval).
"""

from typing import Dict, List
from pathlib import Path

from aiohttp import request
from parsers.parser_wikipedia import WikipediaParser
from parsers.parser1 import IlPostParser
from parsers.parser2 import StatMuseParser
from parsers.parser3 import EurLexParser
import asyncio
import markdown2
import re
import mistune
from bs4 import BeautifulSoup
from parsers.base_parser import BaseParser

class Evaluator:
    """Classe per valutare la qualità del parsing."""

    def __init__(self):
        pass

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizza il testo in token (parole).
        Parametri: text (str) - testo da tokenizzare
        Ritorna: List[str] - lista di token
        """
        text = text.lower()  # Converti tutto in minuscolo per uniformità
        tokens = text.split()  # Semplice tokenizzazione basata su spazi
        return tokens
 

    def calculate_precision(self, extracted_tokens: List[str], gold_tokens: List[str]) -> float:
        """
        Calcola la precisione a livello token.
        Parametri: extracted_tokens, gold_tokens
        Ritorna: float - valore di precisione [0, 1]
        """
        # Versione con SET (senza contare le ripetizioni):
        # if len(extracted_tokens) == 0:
        #     return 0
        # common_tokens = set(extracted_tokens) & set(gold_tokens)
        # precision = len(common_tokens) / len(set(extracted_tokens))
        # return precision
        
        # Versione con Counter (conta le ripetizioni):
        from collections import Counter
        if len(extracted_tokens) == 0:
            return 0
        extracted_count = Counter(extracted_tokens)
        gold_count = Counter(gold_tokens)
        common = sum((extracted_count & gold_count).values())
        precision = common / len(extracted_tokens)
        return precision
        

    def calculate_recall(self, extracted_tokens: List[str], gold_tokens: List[str]) -> float:
        """
        Calcola il recall a livello token.
        Parametri: extracted_tokens, gold_tokens
        Ritorna: float - valore di recall [0, 1]
        """
        # Versione con SET (senza contare le ripetizioni):
        # if len(gold_tokens) == 0:
        #     return 0
        # common_tokens = set(extracted_tokens) & set(gold_tokens)
        # recall = len(common_tokens) / len(set(gold_tokens))
        # return recall
        
        # Versione con Counter (conta le ripetizioni):
        from collections import Counter
        if len(gold_tokens) == 0:
            return 0
        extracted_count = Counter(extracted_tokens)
        gold_count = Counter(gold_tokens)
        common = sum((extracted_count & gold_count).values())
        recall = common / len(gold_tokens)
        return recall

    def calculate_f1(self, precision: float, recall: float) -> float:
        """
        Calcola l'F1 score combinando precisione e recall.
        Parametri: precision, recall
        Ritorna: float - F1 score [0, 1]
        """  
        if precision + recall == 0:
            return 0
        f1 = (2 * precision * recall) / (precision + recall)
        return f1

    def token_level_eval(self, extracted_text: str, gold_text: str) -> Dict[str, float]:
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
        print("=============testo dopo la pulizia da markdown:===============\n", cleaned_extracted_text[:500])
        print("=============gold text:===============\n", gold_text[:500])
        extracted_tokens = self.tokenize(cleaned_extracted_text)
        gold_tokens = self.tokenize(gold_text)
        precision = self.calculate_precision(extracted_tokens, gold_tokens)
        recall = self.calculate_recall(extracted_tokens, gold_tokens)
        f1 = self.calculate_f1(precision, recall)

        result = {"precision": precision,
                  "recall": recall,
                  "f1": f1}
        
        return result



  
async def evaluate_gold_standard(gold_data: List[Dict]) -> Dict[str, Dict]:
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
        if domain == "wikipedia.org":
            parser = WikipediaParser()
        elif domain == "ilpost.it":
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
            
        
            
           
            
           
            
            # Calcola le metriche
            token_eval_result = evaluator.token_level_eval(extracted_text, gold_text)
            result[entry['title']] = token_eval_result
        except Exception as e:
            print(f"[ERROR] Errore nella valutazione di {entry['title']}: {e}")
            result[entry['title']] = {"precision": 0, "recall": 0, "f1": 0}

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