import sqlite3

# Koneksi SQLite
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
DB_PATH = os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
print("DB Path barang model:", DB_PATH)
# DB_PATH = r"z:/beta_desktop/db/beta_sb_pos_sqlite.db"

class BarangModel:
    def get_total_count(self, search_term=None):
        from utils.path_utils import get_db_path

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        if search_term:
            cursor.execute("SELECT COUNT(*) FROM produk WHERE nama LIKE ?", ('%' + search_term + '%',))
        else:
            cursor.execute("SELECT COUNT(*) FROM produk")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    def get_barang_paginated(self, offset, limit, search_term=None):
        from utils.path_utils import get_db_path

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        if search_term:
            cursor.execute("""
                SELECT id, nama, hpp, harga_jual, deskripsi, diskon_persen
                FROM produk
                WHERE nama LIKE ?
                ORDER BY id ASC
                LIMIT ? OFFSET ?
            """, ('%' + search_term + '%', limit, offset))
        else:
            cursor.execute("""
                SELECT id, nama, hpp, harga_jual, deskripsi, diskon_persen
                FROM produk
                ORDER BY id ASC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_barang_by_id(self, produk_id):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, hpp, harga_jual, deskripsi, diskon_persen FROM produk WHERE id = ?", (produk_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def delete_barang(self, produk_id):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produk WHERE id = ?", (produk_id,))
        conn.commit()
        conn.close()

    def update_barang(self, produk_id, nama, hpp, harga_jual, deskripsi, diskon):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE produk
            SET nama=?, hpp=?, harga_jual=?, deskripsi=?, diskon_persen=?
            WHERE id=?
        """, (nama, hpp, harga_jual, deskripsi, diskon, produk_id))
        conn.commit()
        conn.close()

    def insert_barang(self, nama, hpp, harga_jual, deskripsi, diskon):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO produk (nama, hpp, harga_jual, deskripsi, diskon_persen)
            VALUES (?, ?, ?, ?, ?)
        """, (nama, hpp, harga_jual, deskripsi, diskon))
        conn.commit()
        conn.close()
