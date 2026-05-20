import os
import mariadb


def get_connection():
    '''
    funzione per ottenere la conessione al database
    '''
    try:
        return mariadb.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "minerva_user"),
            password=os.getenv("DB_PASSWORD", "minerva_pwd"),
            database=os.getenv("DB_NAME", "minerva_db"),
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        raise