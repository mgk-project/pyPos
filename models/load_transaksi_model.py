import sqlite3

class LoadTransaksiModel:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_tersimpan_transaksi_list(self):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nomer, dtime, customers_nama, transaksi_nilai as total_harga
            FROM transaksi
            WHERE jenis_label = 'simpan_transaksi'
            ORDER BY dtime DESC
        """)
        return cursor.fetchall()

    def get_detail_transaksi(self, transaksi_id):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT produk_id, produk_nama, produk_ord_hrg, produk_ord_jml, produk_ord_diskon,satuan
            FROM transaksi_data
            WHERE transaksi_id = ?
        """, (transaksi_id,))
        return cursor.fetchall()

    def get_transaksi_header(self, transaksi_id):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT customers_id, customers_nama, diskon_persen, ppn_persen, transaksi_nilai as total_harga
            FROM transaksi
            WHERE id = ?
        """, (transaksi_id,))
        return cursor.fetchone()

    def delete_transaksi_by_id(self, transaksi_id):
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM transaksi_data WHERE transaksi_id = ?", (transaksi_id,))
            cursor.execute("DELETE FROM transaksi WHERE id = ?", (transaksi_id,))
            conn.commit()
        finally:
            conn.close()
