from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QFormLayout,
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QMessageBox
)

class BarangView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setup Barang")
        self.main_layout = QVBoxLayout(self)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Masukkan nama barang")
        self.search_button = QPushButton("Cari")

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Cari Barang:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        self.main_layout.addLayout(search_layout)

        # Form input
        form_layout = QFormLayout()
        self.nama_input = QLineEdit()
        self.hpp_input = QLineEdit()
        self.harga_jual_input = QLineEdit()
        self.deskripsi_input = QLineEdit()
        self.diskon_input = QLineEdit()
        self.submit_button = QPushButton("Tambah Barang")

        form_layout.addRow("Nama:", self.nama_input)
        form_layout.addRow("Harga Pokok:", self.hpp_input)
        form_layout.addRow("Harga Jual:", self.harga_jual_input)
        form_layout.addRow("Keterangan:", self.deskripsi_input)
        form_layout.addRow("Diskon:", self.diskon_input)
        form_layout.addWidget(self.submit_button)

        self.main_layout.addLayout(form_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nama", "HPP", "Harga Jual", "Deskripsi", "Diskon", "", ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table)

        # Pagination
        self.prev_button = QPushButton("⬅ Previous")
        self.next_button = QPushButton("Next ➡")
        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.next_button)
        self.main_layout.addLayout(pagination_layout)

    def show_message(self, title, message, error=False):
        if error:
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def show_confirm(self, title, message):
        return QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes
