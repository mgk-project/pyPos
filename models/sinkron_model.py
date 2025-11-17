import pymysql
# import sqlite3
# from datetime import datetime, timedelta
# from decimal import Decimal

# tambahan untuk cek update ke server dengan api yang tersedia server
import sqlite3, requests
from datetime import datetime, timedelta
from decimal import Decimal
from utils.path_utils import get_db_path

BASE_URL = "https://beta.mayagrahakencana.com"
CHECK_URL = f"{BASE_URL}/main_sb/eusvc/NonRest/server_checkUpdate"
SYNC_URL = f"{BASE_URL}/main_sb/eusvc/DataSync/serverSync"

class SinkronModel:
    def __init__(self, db_path=get_db_path()):
        self.db_path = db_path
        self.sqlite_conn = sqlite3.connect(self.db_path)
        self.sqlite_conn.row_factory = sqlite3.Row

# class SinkronModel:
#     def __init__(self):
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
        print("DB Path sinkron model:", DB_PATH)        # conn_sqlite = sqlite3.connect(db_path)

        # # self.sqlite_conn = sqlite3.connect("z:/beta_desktop/db/beta_sb_pos_sqlite.db")
        # self.sqlite_conn = sqlite3.connect(DB_PATH)
        # self.sqlite_conn.execute("PRAGMA foreign_keys = ON")

    def close_connections(self):
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.mysql_conn:
            self.mysql_conn.close()

    # def close_connections(self):
    #     self.mysql_conn.close()
    #     self.sqlite_conn.close()

    def get_last_sync_info(self):
        """Ambil info last_update & lastID dari SQLite tracking table"""
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sync_tracking (
                tabel TEXT PRIMARY KEY,
                last_update TEXT,
                last_id INTEGER
            )
        """)
        cur.execute("SELECT * FROM sync_tracking")
        data = {row["tabel"]: dict(row) for row in cur.fetchall()}
        return data
    
    def save_last_sync_info(self, table_name, last_update, last_id):
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            INSERT INTO sync_tracking (tabel, last_update, last_id)
            VALUES (?, ?, ?)
            ON CONFLICT(tabel) DO UPDATE SET
                last_update=excluded.last_update,
                last_id=excluded.last_id
        """, (table_name, last_update, last_id))
        self.sqlite_conn.commit()

    def check_update_server(self, machine_id, cabang_id):
        """Panggil API checkUpdate"""
        last_info = self.get_last_sync_info()

        payload = {
            "machine_id": machine_id,
            "cabang_id": cabang_id
        }
        for tbl in ["produk", "diskon", "per_cabang", "per_cabang_device", "company_profile"]:
            info = last_info.get(tbl, {"last_update": "2000-01-01 00:00:00", "last_id": 0})
            payload[f"date_last[{tbl}][dtime]"] = info["last_update"]
            payload[f"date_last[{tbl}][lastID]"] = info["last_id"]

        resp = requests.post(CHECK_URL, data=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    
    def sync_data_server(self, machine_id, cabang_id, tables):
        """Ambil data update via API"""
        last_info = self.get_last_sync_info()
        payload = {
            "machine_id": machine_id,
            "cabang_id": cabang_id
        }
        for tbl in tables:
            info = last_info.get(tbl, {"last_update": "2000-01-01 00:00:00", "last_id": 0})
            payload[f"date_last[{tbl}][dtime]"] = info["last_update"]
            payload[f"date_last[{tbl}][lastID]"] = info["last_id"]

        resp = requests.post(SYNC_URL, data=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
    
    def apply_sync_result(self, table_name, data_new):
        """Masukkan data API ke SQLite lokal"""
        if not data_new:
            return 0
        cur = self.sqlite_conn.cursor()

        # --- cek kolom lokal ---
        cur.execute(f"PRAGMA table_info(`{table_name}`)")
        local_cols = [row[1] for row in cur.fetchall()]

        # --- cek kolom server (dari data API) ---
        server_cols = list(data_new[0].keys())

        # --- tambahkan kolom baru kalau belum ada ---
        for col in server_cols:
            if col not in local_cols:
                print(f"🆕 Menambahkan kolom baru '{col}' ke tabel '{table_name}'")
                cur.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" TEXT')

        # --- siapkan insert ---
        col_names = ",".join([f'"{c}"' for c in server_cols])
        placeholders = ",".join(["?" for _ in server_cols])

        for row in data_new:
            values = [row.get(c) for c in server_cols]
            cur.execute(f"""
                INSERT OR REPLACE INTO {table_name} ({col_names})
                VALUES ({placeholders})
            """, values)
            # update tracking
            if "last_update" in row and "id" in row:
                self.save_last_sync_info(table_name, row["last_update"], int(row["id"]))

        self.sqlite_conn.commit()
        return len(data_new)

    # def apply_sync_result(self, table_name, data_new):
    #     """Masukkan data API ke SQLite lokal"""
    #     if not data_new:
    #         return 0
    #     cur = self.sqlite_conn.cursor()
    #     # Ambil kolom dari data
    #     cols = list(data_new[0].keys())
    #     col_names = ",".join([f'"{c}"' for c in cols])
    #     placeholders = ",".join(["?" for _ in cols])

    #     for row in data_new:
    #         values = [row[c] for c in cols]
    #         cur.execute(f"""
    #             INSERT OR REPLACE INTO {table_name} ({col_names})
    #             VALUES ({placeholders})
    #         """, values)
    #         # update tracking
    #         self.save_last_sync_info(table_name, row["last_update"], int(row["id"]))

    #     self.sqlite_conn.commit()
    #     return len(data_new)
    # akhir dari tambahan pakai api yang tersedia di server
    
    def sync_table_last_update(self, table_name, key_column='id'):
        print(f'butuh sinkron tabelnya {table_name} ')

        def parse_datetime_safe(dt_val):
            if not dt_val or dt_val in ("0000-00-00 00:00:00", "last_update"):
                return None

            if isinstance(dt_val, datetime):
                return dt_val  # langsung kembalikan

            if isinstance(dt_val, str):
                try:
                    return datetime.strptime(dt_val, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        return datetime.strptime(dt_val, "%Y-%m-%d")
                    except Exception as e:
                        print(f"⚠️ Gagal parse datetime: {dt_val}, error: {e}")
                        print(f'TIM 2')
                        return None

            return None

        # def parse_datetime_safe(dt_str):
        #     if dt_str in ("0000-00-00 00:00:00", None, "", "last_update"):
        #         return None
        #     try:
        #         return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        #     except ValueError:
        #         try:
        #             return datetime.strptime(dt_str, "%Y-%m-%d")
        #         except Exception as e:
        #             print(f"⚠️ Gagal parse datetime: {dt_str}, error: {e}")
        #             return None

        
        cursor_mysql = self.mysql_conn.cursor()   # tanpa dictionary=True
        cursor_sqlite = self.sqlite_conn.cursor()

        try:
            # --- Ambil data dari server ---
            cursor_mysql.execute(f"SELECT * FROM `{table_name}`")
            columns = [col[0] for col in cursor_mysql.description]
            server_rows = [dict(zip(columns, row)) for row in cursor_mysql.fetchall()]
            if not server_rows:
                return 0

            # --- Cek kolom di server & lokal ---
            server_columns = list(server_rows[0].keys())
            cursor_sqlite.execute(f"PRAGMA table_info(`{table_name}`)")
            local_columns = [row[1] for row in cursor_sqlite.fetchall()]

            # Tambahkan kolom yang belum ada
            for col in server_columns:
                if col not in local_columns:
                    print(f"🆕 Menambahkan kolom baru '{col}' ke tabel lokal '{table_name}'")
                    cursor_sqlite.execute(f'ALTER TABLE `{table_name}` ADD COLUMN "{col}" TEXT')

            # --- Ambil data lokal (id + last_update) ---
            try:
                cursor_sqlite.execute(f"SELECT {key_column}, last_update FROM `{table_name}`")
                local_rows = cursor_sqlite.fetchall()

                local_map = {}
                for row in local_rows:
                    row_id, raw_time = row
                    if not raw_time:
                        continue
                    parsed_time = parse_datetime_safe(raw_time)
                    if parsed_time:
                        local_map[row_id] = parsed_time

            except sqlite3.OperationalError:
                local_map = {}

            # --- Bandingkan last_update ---
            updated_rows = []
            for row in server_rows:
                row_id = row[key_column]
                server_last_update = parse_datetime_safe(row.get("last_update"))

                if not server_last_update:
                    continue

                local_last_update = local_map.get(row_id)
                if not local_last_update or server_last_update > local_last_update:
                    row_values = []
                    for value in row.values():
                        if isinstance(value, Decimal):
                            value = float(value)
                        elif isinstance(value, timedelta):
                            value = str(value)
                        elif isinstance(value, datetime):
                            value = value.strftime("%Y-%m-%d %H:%M:%S")
                        row_values.append(value)
                    updated_rows.append(tuple(row_values))

            # updated_rows = []
            # for row in server_rows:
            #     row_id = row[key_column]
            #     server_last_update = row.get("last_update")
            #     if not server_last_update:
            #         continue

            #     # if isinstance(server_last_update, str):
            #     #     server_last_update = datetime.strptime(server_last_update, "%Y-%m-%d %H:%M:%S")
            #     if isinstance(server_last_update, str):
            #         server_last_update = parse_datetime_safe(server_last_update)


            #     local_last_update = local_map.get(row_id)
            #     if not local_last_update or server_last_update > local_last_update:
            #         row_values = []
            #         for value in row.values():
            #             if isinstance(value, Decimal):
            #                 value = float(value)
            #             elif isinstance(value, timedelta):
            #                 value = str(value)
            #             elif isinstance(value, datetime):
            #                 value = parse_datetime_safe(value) #value.strftime("%Y-%m-%d %H:%M:%S")
            #             row_values.append(value)
            #         updated_rows.append(tuple(row_values))

            # --- Masukkan ke SQLite ---
            if updated_rows:
                columns = ', '.join([f'"{c}"' for c in server_columns])
                placeholders = ', '.join(['?' for _ in server_columns])
                cursor_sqlite.executemany(
                    f'INSERT OR REPLACE INTO `{table_name}` ({columns}) VALUES ({placeholders})',
                    updated_rows
                )
                self.sqlite_conn.commit()

            print(f'✅ Jumlah data tersinkronisasi = {len(updated_rows)}')
            return len(updated_rows)

        except Exception as e:
            self.sqlite_conn.rollback()
            raise e



# kreasi tim 2 , fungsi is_data_updated digunakan untuk mengecek perlu tidak nya background sinkron
    def ensure_mysql_connection(self):
        try:
            self.mysql_conn.ping(reconnect=True)
        except Exception as e:
            print(f"[WARNING] Reconnect MySQL: {e}")
            self.mysql_conn = pymysql.connect(
                host='192.168.5.14',
                user='beta',
                password='beta556699',
                database='beta_main_sb_pos',
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor
            )

    def is_data_updated(self, table_name, key_column='id'):
        print(f'mengecek apakah tabel {table_name} butuh disinkron tidak')
        def parse_datetime_safe(dt_val):
            if not dt_val or dt_val in ("0000-00-00 00:00:00", "last_update"):
                return None

            if isinstance(dt_val, datetime):
                return dt_val  # langsung kembalikan

            if isinstance(dt_val, str):
                try:
                    return datetime.strptime(dt_val, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        return datetime.strptime(dt_val, "%Y-%m-%d")
                    except Exception as e:
                        print(f"⚠️ Gagal parse datetime: {dt_val}, error: {e}")
                        print(f'IS DATA UPDATED TIM 2')
                        return None

            return None
        # def parse_datetime_safe(dt_str):
        #     if dt_str in ("0000-00-00 00:00:00", None, ""):
        #         return None  # atau default datetime.now(), sesuai kebutuhanmu
        #     try:
        #         return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        #     except Exception as e:
        #         print(f"⚠️ Gagal parse datetime: {dt_str}, error: {e}")
        #         print('is data updated tim 2')
        #         return None

        self.ensure_mysql_connection()
        # mysql_cursor = self.mysql_conn.cursor()
        # sqlite_cursor = self.sqlite_conn.cursor()

        cursor_mysql = self.mysql_conn.cursor()
        cursor_sqlite = self.sqlite_conn.cursor()

        try:
            # Ambil semua data dari server
            cursor_mysql.execute(f"SELECT * FROM `{table_name}`")
            server_rows = cursor_mysql.fetchall()

            if not server_rows:
                return 0


            try:
                cursor_sqlite.execute(f"SELECT {key_column}, last_update FROM `{table_name}`")
                local_rows = cursor_sqlite.fetchall()

                local_map = {}
                for row in local_rows:
                    row_id = row[0]
                    raw_time = row[1]
                    if not raw_time:
                        continue
                    try:
                        # parsed_time = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                        parsed_time = parse_datetime_safe(raw_time)

                    except ValueError:
                        try:
                            parsed_time = datetime.strptime(raw_time, "%Y-%m-%d")
                            parsed_time = parsed_time.replace(hour=0, minute=0, second=0)
                        except ValueError:
                            continue
                    local_map[row_id] = parsed_time

            except sqlite3.OperationalError:
                local_map = {}

            updated_rows = []
            for row in server_rows:
                row_id = row[key_column]
                server_last_update = row.get("last_update")
                if not server_last_update:
                    continue

                if isinstance(server_last_update, str):
                    server_last_update = datetime.strptime(server_last_update, "%Y-%m-%d %H:%M:%S")

                local_last_update = local_map.get(row_id)
                if not local_last_update or server_last_update > local_last_update:
                    row_values = []
                    for value in row.values():
                        if isinstance(value, Decimal):
                            value = float(value)
                        elif isinstance(value, timedelta):
                            value = str(value)
                        elif isinstance(value, datetime):
                            value = value.strftime("%Y-%m-%d %H:%M:%S")
                        row_values.append(value)
                    updated_rows.append(tuple(row_values))

            if updated_rows:
                return True
            else:
                return False

        except Exception as e:
            self.sqlite_conn.rollback()
            raise e
