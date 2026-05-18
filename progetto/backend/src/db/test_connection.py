from connection import get_connection


def main():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    print("Tabelle trovate:")
    for table in tables:
        print(table)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()