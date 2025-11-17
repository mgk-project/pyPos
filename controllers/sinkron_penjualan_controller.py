from PySide6.QtCore import QThread, Signal
from models.sinkron_penjualan_model import SinkronPenjualanModel

class SinkronPenjualanController(QThread):
    progress = Signal(str)
    selesai = Signal(str)

    def run(self):
        self.progress.emit("Memulai sinkronisasi data penjualan...")
        model = SinkronPenjualanModel()

        try:
            tabel_penjualan = ['produk', 'diskon', 'price']
            total_sync = 0

            for tabel in tabel_penjualan:
                self.progress.emit(f"[SYNC] Sinkronisasi tabel: {tabel}")
                count = model.sync_table(tabel, days=1000)
                self.progress.emit(f"[SYNC] {count} baris disinkron dari tabel {tabel}.")
                total_sync += count

            model.close_connections()
            self.selesai.emit(f"Selesai sinkronisasi. Total data: {total_sync}")
        except Exception as e:
            self.selesai.emit(f"Gagal sinkronisasi: {str(e)}")
