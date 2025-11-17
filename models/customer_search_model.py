import sqlite3

class CustomerSearchModel:
    # Koneksi SQLite
    import sys
    import os

    BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
    DB_PATH = os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
    print("DB Path customer search model:", DB_PATH)
    # conn_sqlite = sqlite3.connect(db_path)
    # def __init__(self, db_path="z:/beta_desktop/db/beta_sb_pos_sqlite.db"):
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def load_all_customers(self):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, alamat_1, tlp_1 FROM per_customers")
        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]
