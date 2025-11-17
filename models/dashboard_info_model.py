import sqlite3
from datetime import date

class DashboardInfoModel:
    def __init__(self, db_path):
        self.db_path = db_path

    # def get_today_summary(self):
    #     today = date.today().isoformat()  # format: 'YYYY-MM-DD'
    #     conn = sqlite3.connect(self.db_path)
    #     cursor = conn.cursor()

    #     # Ambil jumlah transaksi penjualan hari ini
    #     cursor.execute("""
    #         SELECT COUNT(*) FROM transaksi
    #         WHERE DATE(dtime) = ? AND jenis_label = 'invoice'
    #     """, (today,))
    #     transaksi_count = cursor.fetchone()[0]

    #     # Ambil jumlah retur penjualan hari ini
    #     cursor.execute("""
    #         SELECT COUNT(*) FROM return_transaksi_penjualan
    #         WHERE DATE(tanggal_return) = ?  
    #     """, (today,))
    #     retur_count = cursor.fetchone()[0]

    #     conn.close()
    #     return transaksi_count, retur_count
    def get_today_summary(self):
        # print('masuk get_today summary')
        from utils.path_utils import get_db_path
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        # Total transaksi hari ini dari jenis 'invoice'
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(transaksi_nilai), 0)
            FROM transaksi
            WHERE DATE(dtime) = DATE('now', 'localtime') AND jenis_label = 'invoice'
        """)
        transaksi_result = cursor.fetchone() or (0, 0)
        transaksi_count, transaksi_total = transaksi_result

        # Total retur hari ini dari tabel return_transaksi_penjualan
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(total_return), 0)
            FROM return_transaksi_penjualan
            WHERE DATE(tanggal_return) = DATE('now', 'localtime')
        """)
        retur_result = cursor.fetchone() or (0, 0)
        retur_count, retur_total = retur_result

        # print(f'DEBUG: {transaksi_count=} | {transaksi_total=} | {retur_count=} | {retur_total=}')
        
        conn.close()
        return transaksi_count, transaksi_total, retur_count, retur_total
