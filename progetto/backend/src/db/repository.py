try:
    from .connection import get_connection
except ImportError:
    from connection import get_connection

import json

def get_web_resource(url: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT url, domain, title, html_text, created_at
        FROM web_resources
        WHERE url = ?
        """,
        (url,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result


def get_gold_standard(url: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            wr.url,
            wr.domain,
            wr.title,
            wr.html_text,
            gs.gold_text,
            gs.created_at
        FROM gold_standard gs JOIN web_resources wr ON gs.url = wr.url
        WHERE gs.url = ?
        """,
        (url,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result


def list_gold_standard_urls(domain: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT gs.url
        FROM gold_standard gs JOIN web_resources wr ON gs.url = wr.url
        WHERE wr.domain = ?
        ORDER BY gs.url
        """,
        (domain,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [row[0] for row in rows]


def add_web_resource(url: str, domain: str, title: str, html_text: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO web_resources (url, domain, title, html_text)
        VALUES (?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE 
            domain = VALUES(domain),
            title = VALUES(title),
            html_text = VALUES(html_text)
        """,
        (url, domain, title, html_text)
    )

    conn.commit()

    cursor.close()
    conn.close()


def add_gold_standard(url: str, gold_text: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO gold_standard (url, gold_text)
        VALUES (?, ?)
        ON DUPLICATE KEY UPDATE
            gold_text = VALUES(gold_text)
        """,
        (url, gold_text)
    )

    conn.commit()

    cursor.close()
    conn.close()


def delete_web_resource(url: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM web_resources WHERE url = ?",
        (url,)
    )

    conn.commit()

    affected = cursor.rowcount

    cursor.close()
    conn.close()

    return affected > 0


def delete_gold_standard(url: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM gold_standard WHERE url = ?",
        (url,)
    )

    conn.commit()

    affected = cursor.rowcount

    cursor.close()
    conn.close()

    return affected > 0


def add_parsed_document(url: str, parsed_text: str, parser_name: str = None):
    """
    Salva o aggiorna nel DB il testo parsato prodotto da un parser.
    Ritorna l'id del documento parsato.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO parsed_documents (url, parsed_text, parser_name)
        VALUES (?, ?, ?)
        ON DUPLICATE KEY UPDATE
            parsed_text = VALUES(parsed_text),
            parser_name = VALUES(parser_name),
            created_at = CURRENT_TIMESTAMP
        """,
        (url, parsed_text, parser_name)
    )

    conn.commit()

    cursor.execute(
        """
        SELECT id
        FROM parsed_documents
        WHERE url = ?
        """,
        (url,)
    )

    row = cursor.fetchone()
    parsed_document_id = row[0] if row else None

    cursor.close()
    conn.close()

    return parsed_document_id


def add_evaluation(url: str, token_level_eval: dict, x_eval: dict = None, parsed_document_id: int = None):
    """
    Salva o aggiorna nel DB le metriche di evaluation per un URL.
    """
    conn = get_connection()
    cursor = conn.cursor()

    precision_score = token_level_eval.get("precision", 0)
    recall_score = token_level_eval.get("recall", 0)
    f1_score = token_level_eval.get("f1", 0)

    cursor.execute(
        """
        INSERT INTO evaluations (
            url,
            parsed_document_id,
            precision_score,
            recall_score,
            f1_score,
            x_eval
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
            parsed_document_id = VALUES(parsed_document_id),
            precision_score = VALUES(precision_score),
            recall_score = VALUES(recall_score),
            f1_score = VALUES(f1_score),
            x_eval = VALUES(x_eval),
            created_at = CURRENT_TIMESTAMP
        """,
        (
            url,
            parsed_document_id,
            precision_score,
            recall_score,
            f1_score,
            json.dumps(x_eval or {}, ensure_ascii=False),
        )
    )

    conn.commit()

    cursor.close()
    conn.close()


def add_llm_judgement(
    url: str,
    model_name: str,
    judge_score: float,
    judge_feedback: str,
    extra_info: dict = None,
    parsed_document_id: int = None
):
    """
    Salva o aggiorna nel DB il giudizio LLM per un URL.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO llm_judgements (
            url,
            parsed_document_id,
            model_name,
            judge_score,
            judge_feedback,
            extra_info
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
            parsed_document_id = VALUES(parsed_document_id),
            model_name = VALUES(model_name),
            judge_score = VALUES(judge_score),
            judge_feedback = VALUES(judge_feedback),
            extra_info = VALUES(extra_info),
            created_at = CURRENT_TIMESTAMP
        """,
        (
            url,
            parsed_document_id,
            model_name,
            judge_score,
            judge_feedback,
            json.dumps(extra_info or {}, ensure_ascii=False)
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

def db_stats():
    """
    Restituisce statistiche generali sui dati salvati nel DB.
    Usa dati pre-calcolati e salvati nelle tabelle.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT domain, COUNT(*) AS count
        FROM web_resources
        GROUP BY domain
        ORDER BY domain
        """
    )
    web_resources_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT wr.domain, COUNT(*) AS count
        FROM gold_standard gs
        JOIN web_resources wr ON gs.url = wr.url
        GROUP BY wr.domain
        ORDER BY wr.domain
        """
    )
    gold_standard_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT 
            wr.domain,
            AVG(ev.precision_score) AS avg_precision,
            AVG(ev.recall_score) AS avg_recall,
            AVG(ev.f1_score) AS avg_f1,
            AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(ev.x_eval, '$.cosine_similarity')) AS DOUBLE)) AS avg_cosine_similarity,
            AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(ev.x_eval, '$.boilerplate_ratio_extracted')) AS DOUBLE)) AS avg_boilerplate_ratio_extracted,
            AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(ev.x_eval, '$.boilerplate_fidelity')) AS DOUBLE)) AS avg_boilerplate_fidelity
        FROM evaluations ev
        JOIN web_resources wr ON ev.url = wr.url
        GROUP BY wr.domain
        ORDER BY wr.domain
        """
    )
    eval_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT 
            wr.domain,
            AVG(j.judge_score) AS avg_judge_score
        FROM llm_judgements j
        JOIN web_resources wr ON j.url = wr.url
        GROUP BY wr.domain
        ORDER BY wr.domain
        """
    )
    judge_rows = cursor.fetchall()

    cursor.close()
    conn.close()

    web_resources_stats = {}
    gold_standard_stats = {}
    avg_eval = {}
    avg_eval_judge = {}

    for row in web_resources_rows:
        web_resources_stats[row["domain"]] = row["count"]

    for row in gold_standard_rows:
        gold_standard_stats[row["domain"]] = row["count"]

    for row in eval_rows:
        avg_eval[row["domain"]] = {
            "token_level_eval": {
                "precision": float(row["avg_precision"] or 0),
                "recall": float(row["avg_recall"] or 0),
                "f1": float(row["avg_f1"] or 0),
            },
            "x_eval": {
                "cosine_similarity": float(row["avg_cosine_similarity"] or 0),
                "boilerplate_ratio_extracted": float(row["avg_boilerplate_ratio_extracted"] or 0),
                "boilerplate_fidelity": float(row["avg_boilerplate_fidelity"] or 0),
            }
        }

    for row in judge_rows:
        avg_eval_judge[row["domain"]] = {
            "judge_score": float(row["avg_judge_score"] or 0)
        }

    return {
        "web_resources": web_resources_stats,
        "gold_standard": gold_standard_stats,
        "avg_eval": avg_eval,
        "avg_eval_judge": avg_eval_judge,
    }

def db_schema():
    """
    Restituisce lo schema del database.
    Serve per GET /db_schema.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            COLUMN_TYPE,
            COLUMN_KEY
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    schema = {}

    for row in rows:
        table_name = row["TABLE_NAME"]
        column_name = row["COLUMN_NAME"]
        column_type = row["COLUMN_TYPE"]
        column_key = row["COLUMN_KEY"]

        if table_name not in schema:
            schema[table_name] = {}

        description = column_type

        if column_key == "PRI":
            description += ", PK"

        if table_name == "gold_standard" and column_name == "url":
            description += ", FK(web_resources.url)"
        elif table_name == "parsed_documents" and column_name == "url":
            description += ", FK(web_resources.url)"
        elif table_name == "evaluations" and column_name == "url":
            description += ", FK(web_resources.url)"
        elif table_name == "evaluations" and column_name == "parsed_document_id":
            description += ", FK(parsed_documents.id)"
        elif table_name == "llm_judgements" and column_name == "url":
            description += ", FK(web_resources.url)"
        elif table_name == "llm_judgements" and column_name == "parsed_document_id":
            description += ", FK(parsed_documents.id)"

        schema[table_name][column_name] = description

    return schema