import mysql.connector
from datetime import datetime

import pymysql

def get_mysql_connection():
    return pymysql.connect(
        host="192.168.5.14",
        user="beta",
        password="beta556699",
        database="beta_main_sb_pos",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# def get_mysql_connection():
#     return mysql.connector.connect(
#         host="192.168.5.14",
#         user="beta",
#         password="beta556699",
#         database="beta_main_sb_pos"
#     )

def lengkapi_data_mysql(cursor, table_name, data_dict):
    print('masuk ke lengkapi data mysql')

    # query = """
    #     SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT, DATA_TYPE, EXTRA
    #     FROM INFORMATION_SCHEMA.COLUMNS
    #     WHERE TABLE_NAME = '%s'
    #       AND TABLE_SCHEMA = DATABASE()
    #       AND IS_NULLABLE = 'NO'
    #       AND EXTRA NOT LIKE '%%auto_increment%%'
    # """
    
    print(f'tabelnya  = {table_name}')
    # pakai tuple beneran, PyMySQL butuh ini
    # query = """
    # SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT, DATA_TYPE, EXTRA
    # FROM INFORMATION_SCHEMA.COLUMNS
    # WHERE TABLE_NAME = ''%s''
    #   AND TABLE_SCHEMA = DATABASE()
    #   AND IS_NULLABLE = 'NO'
    #   AND EXTRA NOT LIKE '%%auto_increment%%'
    # """
    # print(f'query = {query}')
    # cursor.execute(
    #     """
    # SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT, DATA_TYPE, EXTRA
    # FROM INFORMATION_SCHEMA.COLUMNS
    # WHERE TABLE_NAME = ''%s''
    #   AND TABLE_SCHEMA = DATABASE()
    #   AND IS_NULLABLE = 'NO'
    #   AND EXTRA NOT LIKE '%%auto_increment%%'
    # """, (table_name,))
    # result = cursor.fetchall()
    # table_name = "transaksi"

    query = """
        SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT, DATA_TYPE, EXTRA
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = %s
        AND TABLE_SCHEMA = DATABASE()
        AND IS_NULLABLE = 'NO'
        AND EXTRA NOT LIKE '%%auto_increment%%'
    """

    print("Query (template):\n", query)
    print("Parameter table_name =", table_name)

    cursor.execute(query, (table_name,))
    result = cursor.fetchall()


    # print(f'querynya = {query}')
    # cursor.execute(query)
    # result = cursor.fetchall()


    print(f"[DEBUG] Jumlah kolom wajib untuk {table_name}: {len(result)}")
    print("[DEBUG] Kolom hasil INFORMATION_SCHEMA:")
# for r in result:
    # print(r)

    for row in result:
        print(row)

        col_name = row["COLUMN_NAME"]
        is_nullable = row["IS_NULLABLE"]
        default_val = row["COLUMN_DEFAULT"]
        data_type = row["DATA_TYPE"]
        extra = row["EXTRA"]

        if col_name not in data_dict:
            if default_val is not None:
                data_dict[col_name] = default_val
            else:
                if data_type in ('varchar', 'text', 'char', 'longtext', 'mediumtext'):
                    data_dict[col_name] = ''
                elif data_type in ('int', 'bigint', 'smallint', 'tinyint', 'mediumint'):
                    data_dict[col_name] = 0
                elif data_type in ('decimal', 'float', 'double'):
                    data_dict[col_name] = 0.0
                elif data_type in ('datetime', 'timestamp', 'date'):
                    data_dict[col_name] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    data_dict[col_name] = ''  # fallback aman
    return data_dict

# def lengkapi_data_mysql(cursor, table_name, data_dict):
#     """
#     Melengkapi field NOT NULL (kecuali AUTO_INCREMENT) yang belum ada di data_dict
#     berdasarkan definisi kolom di INFORMATION_SCHEMA.
#     """
#     print('masuk ke lengkapi data mysql')
#     query = """
#         SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT, DATA_TYPE, EXTRA
#         FROM INFORMATION_SCHEMA.COLUMNS
#         WHERE TABLE_NAME = %s
#         AND TABLE_SCHEMA = DATABASE()
#         AND IS_NULLABLE = 'NO'
#         AND EXTRA NOT LIKE '%auto_increment%'
#     """
#     cursor.execute(query, (table_name,))
#     result = cursor.fetchall()
#     print('cek row in result ')
#     for row in result:
#         col_name = row["COLUMN_NAME"]
#         is_nullable = row["IS_NULLABLE"]
#         default_val = row["COLUMN_DEFAULT"]
#         data_type = row["DATA_TYPE"]
#         extra = row["EXTRA"]

#         if col_name not in data_dict:
#             if default_val is not None:
#                 data_dict[col_name] = default_val
#             else:
#                 # fallback default
#                 if data_type in ('varchar', 'text', 'char', 'longtext', 'mediumtext'):
#                     data_dict[col_name] = ''
#                 elif data_type in ('int', 'bigint', 'smallint', 'tinyint', 'mediumint'):
#                     data_dict[col_name] = 0
#                 elif data_type in ('decimal', 'float', 'double'):
#                     data_dict[col_name] = 0.0
#                 elif data_type in ('datetime', 'timestamp', 'date'):
#                     data_dict[col_name] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 else:
#                     data_dict[col_name] = ''  # fallback aman
#     return data_dict

# def lengkapi_data_mysql(cursor, table_name, data_dict):
#     """
#     Melengkapi field NOT NULL (kecuali AUTO_INCREMENT) yang belum ada di data_dict
#     berdasarkan definisi kolom di INFORMATION_SCHEMA.

#     Args:
#         cursor: Kursor MySQL
#         table_name (str): Nama tabel
#         data_dict (dict): Dictionary input yang akan dilengkapi

#     Returns:
#         dict: data_dict yang telah dilengkapi
#     """
#     query = """
#         SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT, DATA_TYPE, EXTRA
#         FROM INFORMATION_SCHEMA.COLUMNS
#         WHERE TABLE_NAME = %s
#         AND TABLE_SCHEMA = DATABASE()
#         AND IS_NULLABLE = 'NO'
#         AND EXTRA NOT LIKE '%auto_increment%'
#     """
#     cursor.execute(query, (table_name,))
#     result = cursor.fetchall()

#     for col_name, is_nullable, default_val, data_type, extra in result:
#         if col_name not in data_dict:
#             if default_val is not None:
#                 data_dict[col_name] = default_val
#             else:
#                 # Fallback default berdasarkan tipe data
#                 if data_type in ('varchar', 'text', 'char', 'longtext', 'mediumtext'):
#                     data_dict[col_name] = ''
#                 elif data_type in ('int', 'bigint', 'smallint', 'tinyint', 'mediumint'):
#                     data_dict[col_name] = 0
#                 elif data_type in ('decimal', 'float', 'double'):
#                     data_dict[col_name] = 0.0
#                 elif data_type in ('datetime', 'timestamp', 'date'):
#                     data_dict[col_name] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 else:
#                     data_dict[col_name] = ''  # fallback aman
#     return data_dict


def lengkapi_detail_transaksi(cursor, table_name, data_dict):
    return lengkapi_data_mysql(cursor, table_name, data_dict)


def generate_nomer2(counter: int, kasir_username: str) -> str:
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # format: 20250603232957
    no_urut = f"{counter:08d}"  # format: 00000001
    return f"{timestamp}{no_urut}-{kasir_username}"

def get_and_increment_counter_server(self, nama="transaksi") -> int:
    cursor = self.db.cursor()
    
    # 1. Ambil nilai counter sekarang
    cursor.execute("SELECT counter FROM penomoran WHERE nama = %s", (nama,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO penomoran (nama, counter) VALUES (%s, %s)", (nama, 0))
        counter = 0
    else:
        counter = row[0]
    
    # 2. Increment dan update
    new_counter = counter + 1
    cursor.execute("UPDATE penomoran SET counter = %s, dtime_update = now() WHERE nama = %s", (new_counter, nama))
    self.db.commit()
    
    return new_counter

