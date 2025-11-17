from models.load_transaksi_model import LoadTransaksiModel
from views.load_transaksi_view import LoadTransaksiView
from PySide6.QtWidgets import QMessageBox,QTableWidgetItem

class LoadTransaksiController:
    def __init__(self, parent, transaksi_controller, db_path):
        self.model = LoadTransaksiModel(db_path)
        self.transaksi_controller = transaksi_controller  # inject controller utama
        self.view = LoadTransaksiView(self)
        self.parent = parent
        self.transaksi_terpilih_id = None

        self.load_list_transaksi()

    def show(self):
        return self.view.exec()

    def load_list_transaksi(self):
        self.view.table.setRowCount(0)
        rows = self.model.get_tersimpan_transaksi_list()
        for row_data in rows:
            row = self.view.table.rowCount()
            self.view.table.insertRow(row)
            for col, val in enumerate(row_data[:5]):
                self.view.table.setItem(row, col, QTableWidgetItem(str(val)))

    def transaksi_diklik(self, row, column):
        transaksi_id = self.view.table.item(row, 0).text()
        self.transaksi_terpilih_id = int(transaksi_id)
        detail_rows = self.model.get_detail_transaksi(transaksi_id)
        self.view.detail_table.setRowCount(0)
        for item in detail_rows:
            row = self.view.detail_table.rowCount()
            self.view.detail_table.insertRow(row)
            for col, val in enumerate(item):
                self.view.detail_table.setItem(row, col, QTableWidgetItem(str(val)))

    # def load_dipilih(self):
    #     if not self.transaksi_terpilih_id:
    #         QMessageBox.warning(self.view, "Pilih Transaksi", "Pilih transaksi untuk diload.")
    #         return

    #     # Load detail transaksi ke form penjualan
    #     detail_rows = self.model.get_detail_transaksi(self.transaksi_terpilih_id)
    #     self.transaksi_controller.load_transaksi_ke_view(detail_rows)
    #     self.view.accept()

    def load_dipilih(self):
        if not self.transaksi_terpilih_id:
            QMessageBox.warning(self.view, "Pilih Transaksi", "Pilih transaksi untuk diload.")
            return

        header = self.model.get_transaksi_header(self.transaksi_terpilih_id)
        detail_rows = self.model.get_detail_transaksi(self.transaksi_terpilih_id)

        if header:
            customers_id, customers_nama, diskon, ppn, total_harga = header
            self.transaksi_controller.load_transaksi_ke_view(
                detail_rows, customers_id, customers_nama, diskon, ppn, total_harga
            )

            # Hapus data setelah dimuat
            self.model.delete_transaksi_by_id(self.transaksi_terpilih_id)

        self.view.accept()
