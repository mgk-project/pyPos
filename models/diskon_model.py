import requests
import sqlite3
from flask import request, jsonify

class DiskonModel:
    def __init__(self, base_url):
        self.base_url = base_url
        # Koneksi SQLite
        import sys
        import os

        BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
        from utils.path_utils import get_db_path
        # self.db_path = os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
        self.db_path = get_db_path()
        
# # untuk ambil dari url
#     def get_keterangan_grosir(self, produk_id):
#         url = f"{self.base_url}/keterangan_produk_grosir?id={produk_id}"
#         print(f'masuk ke diskon model get keterangan grosir nilai url = {url}')
#         try:
#             response = requests.get(url)
#             response.raise_for_status()
#             # print("ISI RESPONSE TEXT = ", response.text)

#             return response.json()
#         except Exception as e:
#             print("Error saat ambil data grosir:", e)
#             return []

    def get_keterangan_grosir(self,produk_id):
        id = produk_id
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Supaya hasilnya seperti dictionary
        cursor = conn.cursor()

        try:
            query_ket = """
                SELECT
                    diskon.id AS diskon_id,
                    produk.barcode,
                    diskon.kelipatan,
                    produk.id AS produk_id,
                    produk.nama,
                    diskon.persen,
                    diskon.dtime AS diskon_dtime,
                    diskon.minim,
                    CASE 
                        WHEN diskon.maxim = 0 THEN 100000 
                        ELSE diskon.maxim 
                    END AS maxim,
                    diskon.harga AS harga_diskon,
                    diskon.jenis AS jenis_diskon,
                    diskon.nilai + diskon.harga AS harga_jual,
                    diskon.nilai 
                FROM produk
                INNER JOIN diskon ON produk.id = diskon.produk_id
                WHERE produk.id = ? 
                AND diskon.jenis = 'produk_grosir'
                ORDER BY diskon.id DESC
            """
            
            cursor.execute(query_ket, (id,))
            keterangan_result = cursor.fetchall()

            # Ubah hasil menjadi list of dict
            result_list = [dict(row) for row in keterangan_result]
            return result_list# jsonify(result_list)

        except Exception as e:
            print(f"Error: {e}")
            # return jsonify([]), 500
            return []
        
        finally:
            cursor.close()
            conn.close()


    def get_keterangan_free(self,produk_id):
        id = produk_id
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Supaya hasilnya seperti dictionary
        cursor = conn.cursor()

        try:
            query_ket = """
                SELECT diskon.free_produk_nama, diskon.kelipatan, diskon.minim , produk.barcode,produk.hpp,produk.satuan
                FROM produk
                INNER JOIN diskon ON produk.id = diskon.produk_id
                WHERE produk.id = ? AND diskon.jenis = 'free_produk'
                  AND DATE('now') BETWEEN diskon.dtime_start AND diskon.dtime_end
                   
                ORDER BY diskon.id DESC LIMIT 1
            """
            
            cursor.execute(query_ket, (id,))
            keterangan_result = cursor.fetchall()

            # Ubah hasil menjadi list of dict
            result_list = [dict(row) for row in keterangan_result]
            return result_list# jsonify(result_list)

        except Exception as e:
            print(f"Error: {e}")
            # return jsonify([]), 500
            return []
        
        finally:
            cursor.close()
            conn.close()
