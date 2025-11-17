
# from PySide6.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QGroupBox,
#     QLabel, QLineEdit, QComboBox, QPushButton, QSpinBox, QMessageBox
# )

# from PySide6.QtWidgets import QPushButton, QHBoxLayout , QDialog

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QLineEdit, 
    QComboBox, QPushButton, QSpinBox, QMessageBox, QDialog
)

class PrinterSettingView(QDialog):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.current_printer_id = None   # <--- tambahan penting
        self.setWindowTitle("⚙️ Setting Printer")
        self.setMinimumSize(600, 400)

        self.init_ui()

# class PrinterSettingView(QDialog):
#     def __init__(self, model):
#         super().__init__()
#         self.model = model
#         self.setWindowTitle("⚙️ Setting Printer")
#         self.setMinimumSize(600, 400)

#         self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # List printer
        self.list_printer = QListWidget()
        layout.addWidget(self.list_printer, 1)

        # Detail printer
        detail_box = QVBoxLayout()

        self.input_nama = QLineEdit()
        self.combo_koneksi = QComboBox()
        self.combo_koneksi.addItems(["usb", "lan", "bluetooth", "serial"])
        self.input_address = QLineEdit()
        self.combo_kertas = QComboBox()
        self.combo_kertas.addItems(["56", "80"])
        self.spin_margin = QSpinBox()
        self.spin_margin.setRange(0, 20)

        detail_box.addWidget(QLabel("Nama"))
        detail_box.addWidget(self.input_nama)
        detail_box.addWidget(QLabel("Koneksi"))
        detail_box.addWidget(self.combo_koneksi)
        detail_box.addWidget(QLabel("Alamat (IP:Port / USB VID:PID)"))
        detail_box.addWidget(self.input_address)
        detail_box.addWidget(QLabel("Lebar Kertas"))
        detail_box.addWidget(self.combo_kertas)
        detail_box.addWidget(QLabel("Margin"))
        detail_box.addWidget(self.spin_margin)

        # Tombol aksi
        btn_layout = QHBoxLayout()
        self.btn_tambah = QPushButton("Tambah")
        self.btn_simpan = QPushButton("Simpan")
        self.btn_hapus = QPushButton("Hapus")
        self.btn_set_default = QPushButton("Set Default")
        self.btn_test = QPushButton("Test Print")

        for btn in [
            self.btn_tambah, self.btn_simpan, 
            self.btn_hapus, self.btn_set_default, self.btn_test
        ]:
            btn_layout.addWidget(btn)

        detail_box.addLayout(btn_layout)
        layout.addLayout(detail_box, 2)

    def connect_signals(self):
        """Hubungkan tombol ke fungsi masing-masing"""
        self.btn_tambah.clicked.connect(self.tambah_printer)
        self.btn_simpan.clicked.connect(self.simpan_printer)
        self.btn_hapus.clicked.connect(self.hapus_printer)
        self.btn_set_default.clicked.connect(self.set_default_printer)
        self.btn_test.clicked.connect(self.test_printer)

    # --- Fungsi aksi tombol ---
    def tambah_printer(self):
        self.list_printer.addItem(self.input_nama.text())
        QMessageBox.information(self, "Tambah Printer", "Printer berhasil ditambahkan!")

    def simpan_printer(self):
        QMessageBox.information(self, "Simpan", "Konfigurasi printer berhasil disimpan!")

    def hapus_printer(self):
        item = self.list_printer.currentItem()
        if item:
            row = self.list_printer.row(item)
            self.list_printer.takeItem(row)
            QMessageBox.information(self, "Hapus", f"Printer '{item.text()}' berhasil dihapus!")
        else:
            QMessageBox.warning(self, "Hapus", "Pilih printer dulu!")

    def set_default_printer(self):
        item = self.list_printer.currentItem()
        if item:
            QMessageBox.information(self, "Set Default", f"Printer '{item.text()}' diset sebagai default!")
        else:
            QMessageBox.warning(self, "Set Default", "Pilih printer dulu!")

    def test_printer(self):
        try:
            # pakai model untuk test koneksi print dummy
            success = self.model.test_connection(
                self.combo_koneksi.currentText(),
                self.input_address.text()
            )
            if success:
                QMessageBox.information(self, "Test Print", "✅ Printer berhasil mencetak test dummy!")
            else:
                QMessageBox.warning(self, "Test Print", "❌ Gagal mencetak ke printer.")
        except Exception as e:
            QMessageBox.critical(self, "Test Print", f"⚠️ Error: {e}")

# class PrinterSettingView(QDialog):
#     def __init__(self, model):
#         super().__init__()
#         self.model = model
#         self.setWindowTitle("⚙️ Setting Printer")
#         self.setMinimumSize(600, 400)

#         self.init_ui()


# # class PrinterSettingView(QWidget):
# #     def __init__(self):
# #         super().__init__()
# #         self.setWindowTitle("Setting Printer")
# #         self.setMinimumSize(700, 500)
#     def init_ui(self):
#             # layout = QVBoxLayout()

#             # ... form input printer (nama, koneksi, dsb) ...

#             # # Tombol aksi
#             # button_layout = QHBoxLayout()
#             # self.test_button = QPushButton("🖨️ Test Print")
#             # self.save_button = QPushButton("💾 Simpan")
#             # self.cancel_button = QPushButton("❌ Batal")

#             # button_layout.addWidget(self.test_button)
#             # button_layout.addWidget(self.save_button)
#             # button_layout.addWidget(self.cancel_button)

#             # layout.addLayout(button_layout)
#             # self.setLayout(layout)


#             layout = QHBoxLayout(self)

#             # List printer
#             self.list_printer = QListWidget()
#             layout.addWidget(self.list_printer, 1)

#             # Detail printer
#             detail_box = QVBoxLayout()

#             self.input_nama = QLineEdit()
#             self.combo_koneksi = QComboBox()
#             self.combo_koneksi.addItems(["usb", "lan", "bluetooth", "serial"])
#             self.input_address = QLineEdit()
#             self.combo_kertas = QComboBox()
#             self.combo_kertas.addItems(["56", "80"])
#             self.spin_margin = QSpinBox()
#             self.spin_margin.setRange(0, 20)

#             detail_box.addWidget(QLabel("Nama"))
#             detail_box.addWidget(self.input_nama)
#             detail_box.addWidget(QLabel("Koneksi"))
#             detail_box.addWidget(self.combo_koneksi)
#             detail_box.addWidget(QLabel("Alamat (IP:Port / USB VID:PID)"))
#             detail_box.addWidget(self.input_address)
#             detail_box.addWidget(QLabel("Lebar Kertas"))
#             detail_box.addWidget(self.combo_kertas)
#             detail_box.addWidget(QLabel("Margin"))
#             detail_box.addWidget(self.spin_margin)

#             # Tombol aksi
#              # Tombol aksi
#             # button_layout = QHBoxLayout()
#             # self.test_button = QPushButton("🖨️ Test Print")
#             # self.save_button = QPushButton("💾 Simpan")
#             # self.cancel_button = QPushButton("❌ Batal")

#             # button_layout.addWidget(self.test_button)
#             # button_layout.addWidget(self.save_button)
#             # button_layout.addWidget(self.cancel_button)

#             # layout.addLayout(button_layout)

#             btn_layout = QHBoxLayout()
#             self.btn_tambah = QPushButton("Tambah")
#             self.btn_simpan = QPushButton("Simpan")
#             self.btn_hapus = QPushButton("Hapus")
#             self.btn_set_default = QPushButton("Set Default")
#             # self.test_button = QPushButton("🖨️ Test Print")
#             self.btn_test = QPushButton("Test Print")

#             for btn in [self.btn_tambah, self.btn_simpan, self.btn_hapus, self.btn_set_default, self.btn_test]:
#                 btn_layout.addWidget(btn)

#             detail_box.addLayout(btn_layout)
#             layout.addLayout(detail_box, 2)
