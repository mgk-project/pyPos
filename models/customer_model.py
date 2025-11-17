# models/customer_model.py

import sqlite3

# Koneksi SQLite
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
DB_PATH = os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
print("DB Path customer model:", DB_PATH)
# conn_sqlite = sqlite3.connect(db_path)
# DB_PATH = r"z:/beta_desktop/db/beta_sb_pos_sqlite.db"

class CustomerModel:
    def __init__(self):
        self.db_path = DB_PATH

    def connect(self):
        from utils.path_utils import get_db_path
        return sqlite3.connect(get_db_path())

    def get_customers(self, search_term=None):
        conn = self.connect()
        cursor = conn.cursor()
        if search_term:
            cursor.execute("""
                SELECT id, nama, alamat_1, tlp_1 
                FROM per_customers 
                WHERE nama LIKE ? 
                ORDER BY id ASC
            """, ('%' + search_term + '%',))
        else:
            cursor.execute("""
                SELECT id, nama, alamat_1, tlp_1 
                FROM per_customers 
                ORDER BY id ASC
            """)
        results = cursor.fetchall()
        conn.close()
        return results

    def get_customer_by_id(self, customer_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, alamat_1, tlp_1 FROM per_customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()
        conn.close()
        return customer

    def add_customer(self, nama, alamat, telepon):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO per_customers (nama, alamat_1, tlp_1)
            VALUES (?, ?, ?)
        """, (nama, alamat, telepon))
        conn.commit()
        conn.close()

    def update_customer(self, customer_id, nama, alamat, telepon):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE per_customers
            SET nama = ?, alamat_1 = ?, tlp_1 = ?
            WHERE id = ?
        """, (nama, alamat, telepon, customer_id))
        conn.commit()
        conn.close()

    def delete_customer(self, customer_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM per_customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()

    def load_all_customers(self):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, alamat_1, tlp_1 FROM per_customers")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]  # ✅ Konversi ke list of dict

    
