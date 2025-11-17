import pymysql
import sqlite3
from datetime import datetime, timedelta
from decimal import Decimal

class SinkronPenjualanModel:
    def __init__(self):
        self.mysql_conn = pymysql.connect(
            host='192.168.5.14',
            user='beta',
            password='beta556699',
            database='beta_main_sb_pos',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
        # Koneksi SQLite
        import sys
        import os
        from utils.path_utils import get_db_path
        BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
        DB_PATH = get_db_path() # os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
        print("DB Path sinkron penjualan model:", DB_PATH)        # conn_sqlite = sqlite3.connect(db_path)

        # self.sqlite_conn = sqlite3.connect("z:/beta_desktop/db/beta_sb_pos_sqlite.db")
        self.sqlite_conn = sqlite3.connect(DB_PATH)
        self.sqlite_conn.execute("PRAGMA foreign_keys = ON")

    def close_connections(self):
        self.mysql_conn.close()
        self.sqlite_conn.close()

    def quote_identifier(self, name):
        # Quoting for SQLite identifiers (handles reserved keywords like "limit")
        return f'"{name}"'

    def sync_table(self, table_name, days=30):
        batas_waktu = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        cursor_mysql = self.mysql_conn.cursor()
        cursor_sqlite = self.sqlite_conn.cursor()

        try:
            # Recreate table in SQLite first
            # self.recreate_sqlite_table(table_name)
            cursor_mysql.execute(f"SELECT * FROM `{table_name}` WHERE dtime >= %s", (batas_waktu,))
            rows = cursor_mysql.fetchall()
            if not rows:
                return 0  # Tidak ada data

            # Ambil nama kolom
            keys = list(rows[0].keys())
            quoted_columns = ', '.join(self.quote_identifier(k) for k in keys)
            placeholders = ','.join(['?'] * len(keys))
            values = []

            # Convert Decimal dan timedelta
            for row in rows:
                row_values = []
                for k in keys:
                    v = row[k]
                    if isinstance(v, Decimal):
                        v = float(v)
                    elif isinstance(v, timedelta):
                        v = str(v)
                    row_values.append(v)
                values.append(tuple(row_values))

            # Hapus data lama dalam waktu tersebut
            cursor_sqlite.execute(
                f'DELETE FROM {self.quote_identifier(table_name)} WHERE dtime >= ?', (batas_waktu,)
            )

            # Masukkan data baru
            cursor_sqlite.executemany(
                f'INSERT OR REPLACE INTO {self.quote_identifier(table_name)} ({quoted_columns}) VALUES ({placeholders})',
                values
            )
            # print(f'INSERT OR REPLACE INTO {self.quote_identifier(table_name)} ({quoted_columns}) VALUES ({placeholders})',
            #     values
            # )

            self.sqlite_conn.commit()
            return len(values)
        except Exception as e:
            self.sqlite_conn.rollback()
            raise e
        
        
    def recreate_sqlite_table(self, table_name):
        cursor_mysql = self.mysql_conn.cursor()
        cursor_sqlite = self.sqlite_conn.cursor()

        # Ambil struktur kolom dari MySQL
        cursor_mysql.execute(f"SHOW COLUMNS FROM `{table_name}`")
        columns = cursor_mysql.fetchall()

        # Buat definisi kolom untuk SQLite
        column_defs = []
        for col in columns:
            name = col['Field']
            type_mysql = col['Type'].lower()

            # Map tipe data MySQL ke SQLite
            if 'int' in type_mysql:
                type_sqlite = 'INTEGER'
            elif 'decimal' in type_mysql or 'double' in type_mysql or 'float' in type_mysql:
                type_sqlite = 'REAL'
            elif 'date' in type_mysql or 'time' in type_mysql:
                type_sqlite = 'TEXT'
            else:
                type_sqlite = 'TEXT'

            column_defs.append(f'"{name}" {type_sqlite}')

        column_defs_str = ', '.join(column_defs)

        # Hapus tabel jika ada, lalu buat ulang
        cursor_sqlite.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        cursor_sqlite.execute(f'CREATE TABLE "{table_name}" ({column_defs_str})')

        self.sqlite_conn.commit()

    def sync_table_last_update(self, table_name, key_column='id'):
        cursor_mysql = self.mysql_conn.cursor()
        cursor_sqlite = self.sqlite_conn.cursor()

        try:
            # Ambil data dari server (MySQL)
            cursor_mysql.execute(f"SELECT * FROM {table_name}")
            server_rows = cursor_mysql.fetchall()

            if not server_rows:
                return 0

            # Ambil data lokal
            cursor_sqlite.execute(f"SELECT {key_column}, last_update FROM {table_name}")
            local_data = {row[0]: row[1] for row in cursor_sqlite.fetchall()}

            keys = server_rows[0].keys()
            columns = ','.join([f'"{k}"' for k in keys])
            placeholders = ','.join(['?'] * len(keys))
            values_to_insert = []

            updated = 0
            for row in server_rows:
                row_id = row[key_column]
                row_update_time = row['last_update']
                local_update_time = local_data.get(row_id)

                # Konversi untuk SQLite compare
                if isinstance(row_update_time, datetime):
                    row_update_time = row_update_time.strftime('%Y-%m-%d %H:%M:%S')
                if local_update_time and isinstance(local_update_time, str):
                    try:
                        local_update_time = datetime.strptime(local_update_time, '%Y-%m-%d %H:%M:%S')
                    except:
                        local_update_time = None

                if not local_update_time or str(row_update_time) > str(local_update_time):
                    row_values = []
                    for k in keys:
                        v = row[k]
                        if isinstance(v, Decimal):
                            v = float(v)
                        elif isinstance(v, timedelta):
                            v = str(v)
                        row_values.append(v)
                    values_to_insert.append(tuple(row_values))
                    updated += 1

            # Masukkan data baru / update ke SQLite
            if values_to_insert:
                cursor_sqlite.executemany(
                    f'INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})',
                    values_to_insert
                )
                self.sqlite_conn.commit()

            return updated

        except Exception as e:
            self.sqlite_conn.rollback()
            raise e
