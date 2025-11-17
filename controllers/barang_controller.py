from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QTableWidgetItem
from models.barang_model import BarangModel
from views.barang_view import BarangView

class BarangController(BarangView):
    def __init__(self):
        super().__init__()
        self.model = BarangModel()
        self.current_page = 0
        self.rows_per_page = 100
        self.current_edit_id = None

        self.submit_button.clicked.connect(self.save_barang)
        self.search_button.clicked.connect(self.search)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

        self.load_data()

    def search(self):
        self.current_page = 0
        self.load_data(self.search_input.text())

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data(self.search_input.text())

    def next_page(self):
        self.current_page += 1
        self.load_data(self.search_input.text())

    def load_data(self, search_term=None):
        offset = self.current_page * self.rows_per_page
        total = self.model.get_total_count(search_term)
        if offset >= total and total > 0:
            self.current_page = max(0, self.current_page - 1)
            offset = self.current_page * self.rows_per_page

        rows = self.model.get_barang_paginated(offset, self.rows_per_page, search_term)
        self.table.setRowCount(0)
        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)
            for col_idx, val in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))

            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;  /* hijau terang */
                    color: white;
                    font-weight: bold;
                    padding: 8px 20px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #218838;  /* hijau gelap saat hover */
                }
            """)
            edit_btn.clicked.connect(lambda _, id=row[0]: self.load_for_edit(id))

            del_btn = QPushButton("Hapus")
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;  /* hijau terang */
                    color: white;
                    font-weight: bold;
                    padding: 8px 20px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #218838;  /* hijau gelap saat hover */
                }
            """)
            del_btn.clicked.connect(lambda _, id=row[0]: self.delete_barang(id))

            action_widget = QWidget()
            layout = QHBoxLayout(action_widget)
            layout.addWidget(edit_btn)
            layout.addWidget(del_btn)
            layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row_idx, 6, action_widget)

    def load_for_edit(self, produk_id):
        data = self.model.get_barang_by_id(produk_id)
        if data:
            self.nama_input.setText(data[1])
            self.hpp_input.setText(str(data[2]))
            self.harga_jual_input.setText(str(data[3]))
            self.deskripsi_input.setText(data[4])
            self.diskon_input.setText(str(data[5]))
            self.current_edit_id = produk_id
            self.submit_button.setText("Simpan Perubahan")

    def delete_barang(self, produk_id):
        if self.show_confirm("Konfirmasi", "Yakin ingin menghapus barang ini?"):
            self.model.delete_barang(produk_id)
            self.show_message("Sukses", "Barang berhasil dihapus.")
            self.load_data()

    def save_barang(self):
        nama = self.nama_input.text()
        hpp = self.hpp_input.text()
        harga_jual = self.harga_jual_input.text()
        deskripsi = self.deskripsi_input.text()
        diskon = self.diskon_input.text() or "0"

        if not all([nama, hpp, harga_jual, deskripsi]):
            self.show_message("Validasi", "Semua field harus diisi.", error=True)
            return

        try:
            if self.current_edit_id:
                self.model.update_barang(self.current_edit_id, nama, int(hpp), int(harga_jual), deskripsi, int(diskon))
                self.show_message("Berhasil", "Barang berhasil diperbarui.")
                self.current_edit_id = None
                self.submit_button.setText("Tambah Barang")
            else:
                self.model.insert_barang(nama, int(hpp), int(harga_jual), deskripsi, int(diskon))
                self.show_message("Berhasil", "Barang berhasil ditambahkan.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            self.show_message("Gagal", f"Terjadi kesalahan:\n{e}", error=True)

    def clear_form(self):
        self.nama_input.clear()
        self.hpp_input.clear()
        self.harga_jual_input.clear()
        self.deskripsi_input.clear()
        self.diskon_input.clear()
        self.current_edit_id = None
