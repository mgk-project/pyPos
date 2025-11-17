from dataclasses import dataclass
from datetime import datetime
import sqlite3

@dataclass
class InfoTransaksi:
    tanggal: str
    jenis_item: int
    total_qty: int
    total_belanja: float
@dataclass
class PaymentResult:
    metode: str
    total: float
    bayar: float
    kembalian: float
    no_kartu: str = ""
    approval_code: str = ""
    edc: str = ""
    jenis_kartu: str = ""

class PembayaranModel:
    def __init__(self):
        self.metode = "tunai"
        self.info_transaksi = InfoTransaksi(
            tanggal=datetime.now().strftime("%Y-%m-%d"),
            jenis_item=0,
            total_qty=0,
            total_belanja=0
        )
def cek_voucher_valid(self, kode):
    from utils.path_utils import get_db_path

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # cursor = self.db.cursor()
    cursor.execute("""
        SELECT nilai FROM voucher_return
        WHERE kode = ? AND is_used = 0
    """, (kode,))
    row = cursor.fetchone()
    if row:
        return {"nilai": row[0]}
    return None

