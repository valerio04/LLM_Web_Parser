from repository import (
    add_parsed_document,
    add_evaluation,
    add_llm_judgement,
    db_schema,
    db_stats,
)


def main():
    url = "https://www.ilpost.it/2024/08/29/test-bomba-atomica-unione-sovietica/"

    parsed_document_id = add_parsed_document(
        url=url,
        parsed_text="Questo è un testo parsato di prova.",
        parser_name="IlPostParser"
    )

    add_evaluation(
        url=url,
        parsed_document_id=parsed_document_id,
        token_level_eval={
            "precision": 0.8,
            "recall": 0.9,
            "f1": 0.85
        },
        x_eval={
            "levenshtein": 0.7,
            "rouge_l": 0.75,
            "cosine_similarity": 0.92,
            "boilerplate_ratio_extracted": 0.88,
            "boilerplate_fidelity": 0.93
        }
    )

    add_llm_judgement(
        url=url,
        parsed_document_id=parsed_document_id,
        model_name="llama3.2:3b",
        judge_score=4,
        judge_feedback="Buona estrazione, testo coerente con il gold standard.",
        extra_info={
            "test": True
        }
    )

    print("DB schema:")
    print(db_schema())

    print("\nDB stats:")
    print(db_stats())


if __name__ == "__main__":
    main()