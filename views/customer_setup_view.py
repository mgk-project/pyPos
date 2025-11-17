# view/customer_setup_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from controllers.customer_controller import CustomerController

class CustomerSetupView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = CustomerController()
        self.current_page = 0
        self.items_per_page = 100
        self.editing_id = None

        self.setup_ui()
        self.load_customer()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Header
        header = QLabel("Setup Customer")
        header.setStyleSheet("font-weight: bold; font-size: 20px; margin: 10px;")
        self.layout.addWidget(header)

        # Pencarian
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari Nama Customer...")
        search_button = QPushButton("Cari")
        search_button.clicked.connect(self.search_customer)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        self.layout.addLayout(search_layout)

        # Form
        form_layout = QVBoxLayout()
        self.nama_input = QLineEdit()
        self.alamat_input = QLineEdit()
        self.telepon_input = QLineEdit()
        self.submit_button = QPushButton("Tambah Customer")
        self.submit_button.clicked.connect(self.submit_form)

        form_layout.addWidget(QLabel("Nama:"))
        form_layout.addWidget(self.nama_input)
        form_layout.addWidget(QLabel("Alamat:"))
        form_layout.addWidget(self.alamat_input)
        form_layout.addWidget(QLabel("Telepon:"))
        form_layout.addWidget(self.telepon_input)
        form_layout.addWidget(self.submit_button)
        self.layout.addLayout(form_layout)

        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Alamat", "Telepon", "Aksi"])
        self.layout.addWidget(self.table)

        # Paginasi
        bottom_layout = QHBoxLayout()
        self.prev_button = QPushButton("⬅ Previous")
        self.next_button = QPushButton("Next ➡")
        self.prev_button.clicked.connect(self.go_previous)
        self.next_button.clicked.connect(self.go_next)
        bottom_layout.addWidget(self.prev_button)
        bottom_layout.addWidget(self.next_button)
        self.layout.addLayout(bottom_layout)

    def load_customer(self, search_term=None):
        self.table.setRowCount(0)
        all_data = self.controller.get_customers(search_term)
        self.total_data = len(all_data)
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        for row_idx, row in enumerate(all_data[start:end]):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            # Tombol Aksi
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda _, id=row[0]: self.edit_customer(id))

            hapus_button = QPushButton("Hapus")
            hapus_button.clicked.connect(lambda _, id=row[0]: self.hapus_customer(id))

            action_layout = QHBoxLayout()
            action_layout.addWidget(edit_button)
            action_layout.addWidget(hapus_button)
            action_layout.setContentsMargins(0, 0, 0, 0)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row_idx, 4, action_widget)

    def submit_form(self):
        nama = self.nama_input.text()
        alamat = self.alamat_input.text()
        telepon = self.telepon_input.text()

        if not (nama and alamat and telepon):
            QMessageBox.warning(self, "Validasi", "Semua field harus diisi.")
            return

        if self.editing_id:
            self.controller.update_customer(self.editing_id, nama, alamat, telepon)
            self.submit_button.setText("Tambah Customer")
            QMessageBox.information(self, "Sukses", "Data customer diperbarui.")
            self.editing_id = None
        else:
            self.controller.add_customer(nama, alamat, telepon)
            QMessageBox.information(self, "Sukses", "Customer ditambahkan.")

        self.reset_form()
        self.load_customer()

    def edit_customer(self, customer_id):
        customer = self.controller.get_customer_by_id(customer_id)
        if customer:
            self.editing_id = customer[0]
            self.nama_input.setText(customer[1])
            self.alamat_input.setText(customer[2])
            self.telepon_input.setText(customer[3])
            self.submit_button.setText("Simpan Perubahan")

    def hapus_customer(self, customer_id):
        self.controller.delete_customer(customer_id)
        QMessageBox.information(self, "Sukses", "Customer berhasil dihapus.")
        self.load_customer()

    def search_customer(self):
        self.current_page = 0
        self.load_customer(self.search_input.text())

    def go_next(self):
        if (self.current_page + 1) * self.items_per_page < self.total_data:
            self.current_page += 1
            self.load_customer(self.search_input.text())

    def go_previous(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_customer(self.search_input.text())

    def reset_form(self):
        self.nama_input.clear()
        self.alamat_input.clear()
        self.telepon_input.clear()
