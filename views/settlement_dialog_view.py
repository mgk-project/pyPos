from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QHBoxLayout, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt

# class SettlementDialogView(QDialog):
#     def __init__(self, controller):
#         super().__init__()
#         self.controller = controller
#         self.setWindowTitle("🔒 Settlement Transaksi")
#         self.setMinimumSize(900, 600)

#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout()

#         # Label info
#         label_info = QLabel("Daftar Transaksi yang Belum Disettle (Sebelum Jam 20:00 Hari Ini):")
#         layout.addWidget(label_info)

#         # Tabel transaksi master
#         self.table_transaksi = QTableWidget()
#         # total tidak perlu ditampilkan
#         self.table_transaksi.setColumnCount(3)
#         self.table_transaksi.setHorizontalHeaderLabels(["ID", "Tgl", "Customer"])
#         # Atur lebar kolom manual
#         self.table_transaksi.setColumnWidth(0, 60)   # ID
#         self.table_transaksi.setColumnWidth(1, 200)  # Tgl (kolom tanggal, disesuaikan agar muat)
#         self.table_transaksi.setColumnWidth(2, 150)  # Customer
#         # self.table_transaksi.setColumnCount(4)
#         # self.table_transaksi.setHorizontalHeaderLabels(["ID", "Tgl", "Customer", "Total"])
#         self.table_transaksi.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table_transaksi.setEditTriggers(QTableWidget.NoEditTriggers)
#         layout.addWidget(self.table_transaksi)

#         # Detail transaksi
#         self.detail_label = QLabel("Detail Transaksi:")
#         self.detail_text = QLabel("-")
#         self.detail_text.setStyleSheet("font-family: monospace; background: #eee; padding: 5px;")
#         self.detail_text.setAlignment(Qt.AlignTop)
#         # layout.addWidget(self.detail_label)
#         # layout.addWidget(self.detail_text)

#         # Input nilai uang yang disetorkan
#         uang_layout = QHBoxLayout()
#         uang_layout.addWidget(QLabel("💵 Jumlah Uang Tunai yang Disetorkan:"))
#         self.uang_input = QLineEdit()
#         self.uang_input.setPlaceholderText("Masukkan jumlah uang")
#         self.uang_input.setFixedWidth(200)
#         uang_layout.addWidget(self.uang_input)
#         layout.addLayout(uang_layout)

#         # GroupBox: verifikasi admin (disembunyikan awalnya)
#         self.admin_group = QGroupBox("Verifikasi Admin")
#         self.admin_group.setVisible(False)
#         admin_layout = QVBoxLayout()

#         self.admin_combo = QComboBox()
#         self.admin_combo.setPlaceholderText("Pilih Admin")
#         self.password_input = QLineEdit()
#         self.password_input.setEchoMode(QLineEdit.Password)
#         self.password_input.setPlaceholderText("Masukkan password admin")

#         admin_layout.addWidget(QLabel("👤 Admin:"))
#         admin_layout.addWidget(self.admin_combo)
#         admin_layout.addWidget(QLabel("🔐 Password:"))
#         admin_layout.addWidget(self.password_input)
#         self.admin_group.setLayout(admin_layout)
#         layout.addWidget(self.admin_group)

#         # Rekap tunai & EDC
#         self.rekap_label = QLabel("Rincian Total Penjualan Tunai/Non-Tunai:")
#         self.rekap_text = QLabel("-")
#         self.rekap_text.setStyleSheet("font-family: monospace; background: #eef; padding: 5px;")
#         self.rekap_text.setAlignment(Qt.AlignTop)
#         layout.addWidget(self.rekap_label)
#         layout.addWidget(self.rekap_text)


#         # Tombol aksi
#         button_layout = QHBoxLayout()
#         self.settle_button = QPushButton("✅ SETTLE")
#         self.settle_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #28a745;  /* hijau terang */
#                 color: white;
#                 font-weight: bold;
#                 padding: 8px 20px;
#                 border-radius: 10px;
#             }
#             QPushButton:hover {
#                 background-color: #218838;  /* hijau gelap saat hover */
#             }
#         """)
#         self.settle_button.setEnabled(False)

#         self.cancel_button = QPushButton("BATAL")
#         self.cancel_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #28a745;  /* hijau terang */
#                 color: white;
#                 font-weight: bold;
#                 padding: 8px 20px;
#                 border-radius: 10px;
#             }
#             QPushButton:hover {
#                 background-color: #218838;  /* hijau gelap saat hover */
#             }
#         """)
#         button_layout.addStretch()
#         button_layout.addWidget(self.settle_button)
#         button_layout.addWidget(self.cancel_button)
#         layout.addLayout(button_layout)

#         self.setLayout(layout)
from PySide6.QtCore import Signal

class SettlementDialogView(QDialog):
    # settlement_selesai = Signal()

# class SettlementDialogView(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("🔒 Settlement Transaksi")
        self.setMinimumSize(900, 600)
        # self.settlement_selesai = Signal()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Label info
        label_info = QLabel("Daftar Transaksi yang Belum Disettle (Sebelum Jam 20:00 Hari Ini):")
        layout.addWidget(label_info)

        # ===============================
        # Tabel transaksi master
        # ===============================
        self.table_transaksi = QTableWidget()
        self.table_transaksi.setColumnCount(4)
        self.table_transaksi.setHorizontalHeaderLabels(["ID", "Tgl", "Customer", "Total"])
        self.table_transaksi.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_transaksi.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_transaksi)

        # ===============================
        # Input uang setor
        # ===============================
        uang_layout = QHBoxLayout()
        uang_layout.addWidget(QLabel("💵 Jumlah Uang TUNAI Disetor:"))
        self.uang_input = QLineEdit()
        self.uang_input.setPlaceholderText("Masukkan jumlah uang TUNAI")
        self.uang_input.setFixedWidth(200)
        uang_layout.addWidget(self.uang_input)
        layout.addLayout(uang_layout)

        # ===============================
        # Verifikasi Admin
        # ===============================
        self.admin_group = QGroupBox("Verifikasi Admin")
        self.admin_group.setVisible(False)
        admin_layout = QVBoxLayout()
        self.admin_combo = QComboBox()
        self.admin_combo.setPlaceholderText("Pilih Admin")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Masukkan password admin")
        admin_layout.addWidget(QLabel("👤 Admin:"))
        admin_layout.addWidget(self.admin_combo)
        admin_layout.addWidget(QLabel("🔐 Password:"))
        admin_layout.addWidget(self.password_input)
        self.admin_group.setLayout(admin_layout)
        layout.addWidget(self.admin_group)

        # ===============================
        # Rekap settlement
        # ===============================
        self.rekap_label = QLabel("Rekap Settlement:")
        self.rekap_text = QLabel("-")
        self.rekap_text.setStyleSheet("font-family: monospace; background: #eef; padding: 5px;")
        self.rekap_text.setAlignment(Qt.AlignTop)
        layout.addWidget(self.rekap_label)
        layout.addWidget(self.rekap_text)

        # ===============================
        # History settlement terakhir
        # ===============================
        self.history_label = QLabel("📜 History Settlement (7 Terakhir):")
        layout.addWidget(self.history_label)

        self.table_history = QTableWidget()
        self.table_history.setColumnCount(6)
        self.table_history.setHorizontalHeaderLabels([
            "Tanggal", "Admin", "Harus", "Disetor", "Selisih", "Status"
        ])
        self.table_history.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_history.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table_history)

        # ===============================
        # Tombol aksi
        # ===============================
        button_layout = QHBoxLayout()
        self.settle_button = QPushButton("✅ SETTLE")
        self.settle_button.setEnabled(False)
        self.cancel_button = QPushButton("BATAL")
        button_layout.addStretch()
        button_layout.addWidget(self.settle_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    # ===============================
    # Tambahan untuk isi tabel history
    # ===============================
    def tampilkan_history(self, history_list):
        self.table_history.setRowCount(len(history_list))
        for row, h in enumerate(history_list):
            self.table_history.setItem(row, 0, QTableWidgetItem(h["tanggal"]))
            self.table_history.setItem(row, 1, QTableWidgetItem(h["admin"]))
            self.table_history.setItem(row, 2, QTableWidgetItem(f"{h['total_harus']:,.0f}"))
            self.table_history.setItem(row, 3, QTableWidgetItem(f"{h['total_disetor']:,.0f}"))
            self.table_history.setItem(row, 4, QTableWidgetItem(f"{h['selisih']:,.0f}"))
            self.table_history.setItem(row, 5, QTableWidgetItem(h["status"]))

    def tampilkan_detail_transaksi(self, text):
        self.detail_text.setText(text)

    def tampilkan_admin_section(self, admin_list):
        self.admin_combo.clear()
        self.admin_combo.addItems(admin_list)
        self.admin_group.setVisible(True)

    def tampilkan_pesan(self, pesan):
        QMessageBox.information(self, "Info", pesan)

    def tampilkan_error(self, pesan):
        QMessageBox.critical(self, "Error", pesan)

    def tampilkan_rekap(self, text):
        self.rekap_text.setText(text)

