from PySide6.QtCore import QThread, Signal, QObject
import pymysql
import sqlite3
from datetime import datetime, timedelta
from decimal import Decimal

class SinkronisasiWorker(QObject):
    progress_changed = Signal(int)
    status_message = Signal(str)
    selesai = Signal()
    gagal = Signal(str)

    def run(self):
            self.status_message.emit("[INFO] Mulai sinkronisasi")
    # Koneksi MySQL
            conn_mysql = pymysql.connect(
                host='192.168.5.14',
                user='beta',
                password='beta556699',
                database='boga_gnt',
                charset='utf8'
            )
            cur_mysql = conn_mysql.cursor(pymysql.cursors.DictCursor)
            print('[INFO] Terhubung ke MySQL.')

            # Koneksi SQLite
            import sys
            import os
            from utils.path_utils import get_db_path
            BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
            DB_PATH = get_db_path() #os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
            print("DB Path sinkronisasi worker:", DB_PATH)
            # conn_sqlite = sqlite3.connect(db_path)

            # conn_sqlite = sqlite3.connect("z:/beta_desktop/db/beta_sb_pos_sqlite.db")
            conn_sqlite = sqlite3.connect(DB_PATH)
            cur_sqlite = conn_sqlite.cursor()
            print('[INFO] Terhubung ke SQLite.')

            tabel_list = ['produk', 'price', 'diskon', 'per_customers']
            batas_waktu = (datetime.now() - timedelta(days=1065)).strftime('%Y-%m-%d %H:%M:%S')

            for tabel in tabel_list:
                print(f'[SYNC] Mulai sinkronisasi tabel: {tabel}')

                # Ambil struktur kolom dari MySQL
                cur_mysql.execute(f"SHOW COLUMNS FROM {tabel}")
                kolom_info = cur_mysql.fetchall()

                kolom_mysql = []
                for kolom in kolom_info:
                    nama = kolom['Field']
                    tipe_mysql = kolom['Type'].lower()
                    if 'int' in tipe_mysql:
                        tipe_sqlite = 'INTEGER'
                    elif 'char' in tipe_mysql or 'text' in tipe_mysql:
                        tipe_sqlite = 'TEXT'
                    elif 'decimal' in tipe_mysql or 'float' in tipe_mysql or 'double' in tipe_mysql:
                        tipe_sqlite = 'REAL'
                    elif 'date' in tipe_mysql or 'time' in tipe_mysql:
                        tipe_sqlite = 'TEXT'
                    else:
                        tipe_sqlite = 'TEXT'
                    kolom_mysql.append((nama, tipe_sqlite))

                # Hapus tabel jika sudah ada
                cur_sqlite.execute(f'DROP TABLE IF EXISTS {tabel}')
                print(f'[SYNC] Tabel {tabel} dihapus dari SQLite.')

                # Buat ulang tabel
                kolom_definisi = ','.join([f'"{nama}" {tipe}' for nama, tipe in kolom_mysql])
                cur_sqlite.execute(f'CREATE TABLE {tabel} ({kolom_definisi})')
                print(f'[SYNC] Tabel {tabel} dibuat ulang dengan struktur baru.')

                # Ambil data dari MySQL berdasarkan waktu
                # for tabel in tabel_list:
                print(f'nama tabel yang dicopy = {tabel}')
                if tabel == 'per_customers':
                    cur_mysql.execute(f"SELECT * FROM {tabel}")
                else:
                    cur_mysql.execute(f"SELECT * FROM {tabel} WHERE dtime >= %s", (batas_waktu,))

                # cur_mysql.execute(f"SELECT * FROM {tabel} WHERE dtime >= %s", (batas_waktu,))
                rows = cur_mysql.fetchall()
                print(f'[SYNC] {len(rows)} baris data diambil dari MySQL.')

                # Masukkan data ke SQLite
                if rows:
                    keys = rows[0].keys()
                    quoted_columns = ','.join([f'"{k}"' for k in keys])
                    placeholders = ','.join(['?'] * len(keys))

                    # def convert_value(val):
                    #     if isinstance(val, Decimal):
                    #         return float(val)
                    #     return val
                    def convert_value(val):
                        if isinstance(val, Decimal):
                            return float(val)
                        elif isinstance(val, timedelta):
                            return str(val)  # atau val.total_seconds() jika ingin numerik
        #                 elif isinstance(val, timedelta):
        # return val.total_seconds()

                        return val


                    values = [tuple(convert_value(row[k]) for k in keys) for row in rows]
                    cur_sqlite.executemany(
                        f'INSERT INTO {tabel} ({quoted_columns}) VALUES ({placeholders})', values)
                    print(f'[SYNC] {len(values)} baris data dimasukkan ke SQLite.')

            conn_sqlite.commit()
            print('[INFO] Sinkronisasi selesai dan disimpan.')
            cur_mysql.close()
            conn_mysql.close()
            conn_sqlite.close()
            print('[INFO] Koneksi ditutup.')

