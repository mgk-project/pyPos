import pymysql
import sqlite3
from datetime import datetime, timedelta
from decimal import Decimal
    # import pymysql
    # import sqlite3
    # from datetime import datetime, timedelta
from decimal import Decimal
from datetime import timedelta
class SinkronDataController:
    def __init__(self, view):
        self.view = view
        self.view.sinkronkan_ditekan.connect(self.mulai_sinkronisasi)

    def mulai_sinkronisasi(self):
        self.view.mulai_progress()
        try:

            hasil = self.sinkronkan_data()
            print(f'hasil = {hasil}')
            self.view.tampilkan_info(True, "Sinkronisasi berhasil!")
        except Exception as e:
            self.view.tampilkan_info(False, str(e))
        finally:
            self.view.selesai_progress()


    def sinkronkan_data(self):
        # Koneksi MySQL
        # jenis database yang dipakai 
        # database='beta' , 'beta_main_sb_pos'
        conn_mysql = pymysql.connect(
            host='192.168.5.14',
            user='beta',
            password='beta556699',
            database='beta_main_sb_pos',
            charset='utf8'
        )
        cur_mysql = conn_mysql.cursor(pymysql.cursors.DictCursor)
        print('[INFO] Terhubung ke MySQL.')

        # Koneksi SQLite
        import sys
        import os

        BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
        DB_PATH = os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
        print("DB Path sinkron data controller:", DB_PATH)

        from utils.path_utils import get_db_path
        # conn = sqlite3.connect(get_db_path())

        conn_sqlite = sqlite3.connect(get_db_path())
        # conn_sqlite = sqlite3.connect("z:/beta_desktop/db/beta_sb_pos_sqlite.db")
        cur_sqlite = conn_sqlite.cursor()
        print('[INFO] Terhubung ke SQLite.')

        tabel_list = ['produk','price', 'diskon', 'diskon_customer','per_customers','bank']
        # tabel_list = ['_rek_pembantu_customer_cache']
        # tabel_list = ['per_cabang_device' , 'per_cabang' , 'per_customers', 'per_employee', 'bank', 'produk', 'price' , 'price_per_area' ,
            #  'diskon' , 'diskon_customer' , '_rek_pembantu_customer_cache' , 'setting_struk' , 'tmp_diskon']
        # tabel_list = ['per_cabang' , 'per_customers', 'per_employee', 'bank', 'produk', 'price' , 'price_per_area' ,
        #      'diskon' , 'diskon_customer' , '_rek_pembantu_customer_cache' , 'setting_struk' , 'tmp_diskon']

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
            # if tabel == 'per_customers':
            cur_mysql.execute(f"SELECT * FROM {tabel}")
            # else:
                # cur_mysql.execute(f"SELECT * FROM {tabel} WHERE dtime >= %s", (batas_waktu,))

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
