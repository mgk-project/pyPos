import sqlite3, uuid
from datetime import datetime
from dataclasses import dataclass
from typing import List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox, QAbstractItemView, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QObject

# Koneksi SQLite
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
DB_PATH = os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
print("DB Path return model:", DB_PATH)
# conn_sqlite = sqlite3.connect(db_path)
# DB_PATH = "z:/beta_desktop/db/beta_sb_pos_sqlite.db"

# ---------- MODEL ---------- #
@dataclass
class ReturnItem:
    produk_id: str
    produk_nama: str
    jumlah: int
    harga: float
    jenis_return: str  # full/partial

class ReturnModel:
    def __init__(self, db_path: str = DB_PATH):
        from utils.path_utils import get_db_path
        self.conn = sqlite3.connect(get_db_path())
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS return_transaksi_penjualan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaksi_id TEXT NOT NULL,
                tanggal_return TEXT NOT NULL,
                total_return REAL NOT NULL,
                kode_voucher TEXT UNIQUE NOT NULL,
                nilai_voucher REAL NOT NULL
            );""")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS detail_return_transaksi_penjualan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_transaksi_id INTEGER NOT NULL,
                produk_id TEXT NOT NULL,
                produk_nama TEXT NOT NULL,
                jumlah INTEGER NOT NULL,
                jenis_return TEXT NOT NULL,
                harga REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (return_transaksi_id) REFERENCES return_transaksi_penjualan(id) ON DELETE CASCADE
            );""")
        self.conn.commit()

    # === Transaksi master search ===
    def search_transaksi_master(self, keyword: str):
        kw = f"%{keyword}%"
        return self.conn.execute(
            """SELECT id, nomer, dtime AS tanggal, customers_nama , transaksi_nilai
                   FROM transaksi
                   WHERE nomer LIKE ? OR tanggal LIKE ? OR customers_nama LIKE ?
                   ORDER BY tanggal DESC LIMIT 200""", (kw, kw, kw)).fetchall()

    def load_transaksi_detail(self, transaksi_id: str):
        return self.conn.execute(
            "SELECT * FROM transaksi_data WHERE transaksi_id = ?", (transaksi_id,)
        ).fetchall()

    # def generate_kode_voucher():
    #     from datetime import datetime
    #     base = datetime.now().strftime("RVCH%Y%m%d-")
    #     return base + str(random.randint(100, 999))

    # voucher_kode = generate_kode_voucher()
    # cursor.execute("""
    #     INSERT INTO voucher_return (kode, nilai, dtime_terbit)
    #     VALUES (?, ?, datetime('now'))
    # """, (voucher_kode, nilai_retur))

    # def insert_return(self, transaksi_id: str, items: List[ReturnItem]):
    def insert_return(self, transaksi_id: str, items: List[ReturnItem], jenis_return: str = 'partial'):

        total_return = sum(it.harga * it.jumlah for it in items)
        kode_voucher = "VCR" + datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:3].upper()
        # kode_voucher = generate_kode_voucher()
       
        

        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO voucher_return (kode, nilai, dtime_terbit)
            VALUES (?, ?, datetime('now'))
        """, (kode_voucher, total_return))
        print(f'total = {total_return} ')
        # 1. Ambil customers_id berdasarkan transaksi_id
        cur.execute("SELECT customers_id,transaksi_nilai FROM transaksi WHERE id = ?", (transaksi_id,))
        row = cur.fetchone()
        customers_id = row[0] if row else None
        total_return = row[1] if row else 0

        # 2. Insert ke tabel master return
        # cur.execute("""
        #     INSERT INTO return_transaksi_penjualan
        #     (transaksi_id, customer_id, tanggal_return, total_return, kode_voucher, nilai_voucher)
        #     VALUES (?,?,?,?,?,?)
        # """, (
        #     transaksi_id,
        #     customers_id,
        #     datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        #     total_return,
        #     kode_voucher,
        #     total_return
        # ))
        cur.execute("""
            INSERT INTO return_transaksi_penjualan
            (transaksi_id, customer_id, tanggal_return, total_return, kode_voucher, nilai_voucher, jenis_return)
            VALUES (?,?,?,?,?,?,?)
        """, (
            transaksi_id,
            customers_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_return,
            kode_voucher,
            total_return,
            jenis_return
        ))
        ret_id = cur.lastrowid


        # 3. Insert detail return
        for it in items:
            cur.execute("""
                INSERT INTO detail_return_transaksi_penjualan
                (return_id, produk_id, produk_nama, jumlah, jenis_return, harga, subtotal)
                VALUES (?,?,?,?,?,?,?)
            """, (
                ret_id,
                it.produk_id,
                it.produk_nama,
                it.jumlah,
                it.jenis_return,
                it.harga,
                it.harga * it.jumlah
            ))

        self.conn.commit()
        return kode_voucher

    def close(self):
        self.conn.close()

