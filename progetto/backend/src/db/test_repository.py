from repository import (
    get_web_resource,
    get_gold_standard,
    list_gold_standard_urls,
)
from connection import get_connection


def print_separator(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def read_all_web_resources():
    """
    Legge tutte le righe della tabella web_resources.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT url, domain, title, created_at
        FROM web_resources
        ORDER BY domain, url
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def read_all_gold_standard():
    """
    Legge tutte le righe della tabella gold_standard insieme ai dati di web_resources.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            wr.url,
            wr.domain,
            wr.title,
            LENGTH(wr.html_text) AS html_length,
            LENGTH(gs.gold_text) AS gold_length,
            wr.created_at AS web_created_at,
            gs.created_at AS gs_created_at
        FROM gold_standard gs
        JOIN web_resources wr ON gs.url = wr.url
        ORDER BY wr.domain, wr.url
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def read_web_resources_by_domain(domain: str):
    """
    Legge tutte le web_resources di un dominio.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT url, domain, title, LENGTH(html_text) AS html_length, created_at
        FROM web_resources
        WHERE domain = ?
        ORDER BY url
        """,
        (domain,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def read_gold_standard_by_domain(domain: str):
    """
    Legge tutto il Gold Standard di un dominio.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT 
            wr.url,
            wr.domain,
            wr.title,
            LENGTH(wr.html_text) AS html_length,
            LENGTH(gs.gold_text) AS gold_length
        FROM gold_standard gs
        JOIN web_resources wr ON gs.url = wr.url
        WHERE wr.domain = ?
        ORDER BY wr.url
        """,
        (domain,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def read_db_counts():
    """
    Conta quante righe ci sono nelle tabelle principali.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS count FROM web_resources")
    web_resources_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM gold_standard")
    gold_standard_count = cursor.fetchone()["count"]

    cursor.close()
    conn.close()

    return {
        "web_resources": web_resources_count,
        "gold_standard": gold_standard_count,
    }


def read_counts_by_domain():
    """
    Conta quante web_resources e quanti gold_standard ci sono per dominio.
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
    web_resources_counts = cursor.fetchall()

    cursor.execute(
        """
        SELECT wr.domain, COUNT(*) AS count
        FROM gold_standard gs
        JOIN web_resources wr ON gs.url = wr.url
        GROUP BY wr.domain
        ORDER BY wr.domain
        """
    )
    gold_standard_counts = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "web_resources": web_resources_counts,
        "gold_standard": gold_standard_counts,
    }


def print_rows_preview(rows, limit: int = 5):
    """
    Stampa solo le prime righe per non riempire troppo il terminale.
    """
    if not rows:
        print("[INFO] Nessuna riga trovata")
        return

    for row in rows[:limit]:
        print(row)

    if len(rows) > limit:
        print(f"... altre {len(rows) - limit} righe non mostrate")


def test_read_all_tables():
    """
    Test lettura completa delle tabelle principali.
    """
    print_separator("TEST 1 - Conteggio righe nelle tabelle")

    counts = read_db_counts()
    print(counts)

    print_separator("TEST 2 - Lettura di tutte le web_resources")

    web_resources = read_all_web_resources()
    print(f"Numero web_resources trovate: {len(web_resources)}")
    print_rows_preview(web_resources)

    print_separator("TEST 3 - Lettura di tutto il gold_standard")

    gold_standard = read_all_gold_standard()
    print(f"Numero gold_standard trovati: {len(gold_standard)}")
    print_rows_preview(gold_standard)


def test_read_by_domain(domain: str):
    """
    Test lettura per dominio.
    """
    print_separator(f"TEST 4 - Lettura web_resources per dominio: {domain}")

    web_resources = read_web_resources_by_domain(domain)
    print(f"Numero web_resources per {domain}: {len(web_resources)}")
    print_rows_preview(web_resources)

    print_separator(f"TEST 5 - Lettura gold_standard per dominio: {domain}")

    gold_standard = read_gold_standard_by_domain(domain)
    print(f"Numero gold_standard per {domain}: {len(gold_standard)}")
    print_rows_preview(gold_standard)

    print_separator(f"TEST 6 - list_gold_standard_urls per dominio: {domain}")

    urls = list_gold_standard_urls(domain)
    print(f"Numero URL trovati: {len(urls)}")
    print_rows_preview(urls)


def test_read_by_url(url: str):
    """
    Test lettura partendo da un URL.
    """
    print_separator(f"TEST 7 - Lettura web_resource da URL")

    web_resource = get_web_resource(url)

    if web_resource:
        print("[OK] Web resource trovata")
        print({
            "url": web_resource.get("url"),
            "domain": web_resource.get("domain"),
            "title": web_resource.get("title"),
            "html_length": len(web_resource.get("html_text") or ""),
            "created_at": web_resource.get("created_at"),
        })
    else:
        print("[WARNING] Web resource non trovata")

    print_separator(f"TEST 8 - Lettura gold_standard da URL")

    gold_standard = get_gold_standard(url)

    if gold_standard:
        print("[OK] Gold standard trovato")
        print({
            "url": gold_standard.get("url"),
            "domain": gold_standard.get("domain"),
            "title": gold_standard.get("title"),
            "html_length": len(gold_standard.get("html_text") or ""),
            "gold_length": len(gold_standard.get("gold_text") or ""),
            "created_at": gold_standard.get("created_at"),
        })

        print("\nAnteprima gold_text:")
        print((gold_standard.get("gold_text") or "")[:500])

    else:
        print("[WARNING] Gold standard non trovato")


def test_counts_by_domain():
    """
    Test conteggi divisi per dominio.
    """
    print_separator("TEST 9 - Conteggi per dominio")

    counts = read_counts_by_domain()

    print("\nweb_resources:")
    for row in counts["web_resources"]:
        print(row)

    print("\ngold_standard:")
    for row in counts["gold_standard"]:
        print(row)


def main():
    # Cambia questi due valori con un dominio e un URL reali presenti nel vostro GS
    domain = "www.ilpost.it"
    url = "https://www.ilpost.it/2024/12/03/newsletter-regali-natale-consumismi-2/"

    test_read_all_tables()
    test_read_by_domain(domain)
    test_read_by_url(url)
    test_counts_by_domain()

    print_separator("TEST COMPLETATI")


if __name__ == "__main__":
    main()