# models/sinkron_data_model.py

import sqlite3
import pymysql
from datetime import datetime, timedelta


class SinkronDataModel:
    def __init__(self):
        self.mysql = None
        self.sqlite = None
        self.mysql_config = {
            "host": "192.168.5.14",
            "user": "beta",
            "password": "beta556699",
            "database": "beta"
        }
        # Koneksi SQLite
        import sys
        import os
        from utils.path_utils import get_db_path
        BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
        DB_PATH = get_db_path()
        print("DB Path sinkron data model:", DB_PATH)
        # conn_sqlite = sqlite3.connect(db_path)
        # self.sqlite_path = "z:/beta_desktop/db/beta_sb_pos_sqlite.db"
        
        self.sqlite_path = DB_PATH

    def connect_db(self):
        self.mysql = pymysql.connect(**self.mysql_config)
        self.sqlite = sqlite3.connect(self.sqlite_path)

    def sync_all(self, update_progress_callback):
        tabels = ["produk", "price", "diskon", "customer", "employee"]
        total = len(tabels)
        for i, tabel in enumerate(tabels):
            self.sync_tabel(tabel)
            update_progress_callback(int(((i + 1) / total) * 100))

    def sync_tabel(self, tabel_nama):
        now = datetime.now()
        five_days_ago = now - timedelta(days=5)
        date_str = five_days_ago.strftime('%Y-%m-%d')

        cursor_mysql = self.mysql.cursor(pymysql.cursors.DictCursor)
        cursor_sqlite = self.sqlite.cursor()

        cursor_mysql.execute(f"SELECT * FROM {tabel_nama} WHERE dtime >= %s", (date_str,))
        rows = cursor_mysql.fetchall()

        if not rows:
            return

        # Bersihkan tabel lokal (bisa diubah jadi update/merge jika perlu)
        cursor_sqlite.execute(f"DELETE FROM {tabel_nama}")

        kolom = rows[0].keys()
        placeholders = ",".join(["?"] * len(kolom))
        insert_sql = f"INSERT INTO {tabel_nama} ({','.join(kolom)}) VALUES ({placeholders})"

        for row in rows:
            cursor_sqlite.execute(insert_sql, list(row.values()))

        self.sqlite.commit()
