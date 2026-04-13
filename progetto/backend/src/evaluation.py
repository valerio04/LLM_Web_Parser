"""
Modulo di valutazione per il parsing.
Implementa metriche di valutazione a livello token (token_level_eval).
"""

from typing import Dict, List, Tuple
from pathlib import Path
from parsers.parser_wikipedia import WikipediaParser
from parsers.parser1 import IlPostParser
from parsers.parser2 import StatMuseParser
from parsers.parser3 import EurLexParser
import asyncio

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
 

    def calculate_precision(self, exctracted_tokens: List[str], gold_tokens: List[str]) -> float:
        """
        Calcola la precisione a livello token.
        Parametri: exctracted_tokens, gold_tokens
        Ritorna: float - valore di precisione [0, 1]
        """
        common_tokens= set(exctracted_tokens) & set(gold_tokens)
        if(len(set(exctracted_tokens)) == 0):
            return 0    
        precision= len(common_tokens) / len(set(exctracted_tokens))
        return precision
        

    def calculate_recall(self, exctracted_tokens: List[str], gold_tokens: List[str]) -> float:
        """
        Calcola il recall a livello token.
        Parametri: exctracted_tokens, gold_tokens
        Ritorna: float - valore di recall [0, 1]
        """
        common_tokens= set(exctracted_tokens) & set(gold_tokens)
        if(len(set(gold_tokens)) == 0):
            return 0
        recall= len(common_tokens) / len(set(gold_tokens))
        return recall

    def calculate_f1(self, precision: float, recall: float) -> float:
        """
        Calcola l'F1 score combinando precisione e recall.
        Parametri: precision, recall
        Ritorna: float - F1 score [0, 1]
        """
        if precision +recall == 0:
            return 0
        f1 = (2 * precision * recall) / (precision + recall)

        return f1

    def token_level_eval(self, exctracted_text: str, gold_text: str) -> Dict[str, float]:
        """
        Esegue la valutazione completa a livello token.
        Calcola precision, recall, F1.
        
        Parametri:
            exctracted_text (str) - testo estratto dal parser
            gold_text (str) - testo di riferimento (gold standard)
        
        Ritorna: Dict con chiavi 'precision', 'recall', 'f1'
        """
        exctracted_tokens = self.tokenize(exctracted_text)
        gold_tokens = self.tokenize(gold_text)
        precision = self.calculate_precision(exctracted_tokens,gold_tokens)
        recall = self.calculate_recall(exctracted_tokens,gold_tokens)
        f1 = self.calculate_f1(precision,recall)

        result = {"precision" : precision,
                  "recall" : recall,
                  "f1" : f1}
        
        return result



  
def evaluate_gold_standard(gold_data: List[Dict]) -> Dict[str, Dict]:
    """
    Valuta tutto il Gold Standard.
    
    Parametri:
        gold_data (List[Dict]) - lista di entry Gold Standard con parser output
    
    Ritorna: Dict con risultati per ogni entry
    """
    if not gold_data:
        return {}
    
    domain = gold_data[0]['domain']
    if domain == "wikipedia.org":
        parser = WikipediaParser()
    elif domain == "ilpost.it":
        parser = IlPostParser()
    elif domain == "statmuse.com":
        parser = StatMuseParser()
    elif domain == "eur-lex.europa.eu":
        parser = EurLexParser()
    else:
        raise ValueError(f"Dominio non riconosciuto: {domain}")

    result = dict()
    evaluator = Evaluator()
    
    for entry in gold_data:
        try:

            #TODO: risolvere problema indirizzo file gold standard (attualmente è relativo alla cartella src, ma dovrebbe essere relativo alla cartella progetto)
            # Estrai il testo usando il parser
            extracted_result = asyncio.run(parser.run(entry['url']))
            extracted_text = extracted_result.get('parsed_text', '')
            
            # Leggi il contenuto del file gold standard
            script_dir = Path(__file__).parent.resolve()

            # Salì 2 livelli: src -> backend -> progetto
            base_dir = script_dir.parent.parent

            # Costruisci il path corretto
            gold_file_path = base_dir / entry['gold_file']

            with open(gold_file_path, 'r', encoding='utf-8') as f:
                gold_text = f.read()
            
            # Calcola le metriche
            token_eval_result = evaluator.token_level_eval(extracted_text, gold_text)
            result[entry['title']] = token_eval_result
        except Exception as e:
            print(f"Errore nella valutazione di {entry['title']}: {e}")
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
