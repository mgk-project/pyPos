from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox
)

class LoadTransaksiView(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Load Transaksi Tersimpan")
        self.resize(700, 400)

        self.layout = QVBoxLayout()

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Nomer", "Tanggal","Customer", "Total Harga"])
        self.table.cellClicked.connect(self.controller.transaksi_diklik)
        self.layout.addWidget(self.table)

        self.preview_label = QLabel("📝 Preview Detail Transaksi:")
        self.layout.addWidget(self.preview_label)

        self.detail_table = QTableWidget(0, 5)
        self.detail_table.setHorizontalHeaderLabels(["Id Produk", "Nama", "Harga", "Jumlah" , "Diskon"])
        self.layout.addWidget(self.detail_table)

        self.button_layout = QHBoxLayout()
        self.btn_load = QPushButton("🔄 Load")
        self.btn_load.setStyleSheet("""
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
        self.btn_cancel = QPushButton("❌ Batal")
        self.btn_cancel.setStyleSheet("""
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
        self.btn_load.clicked.connect(self.controller.load_dipilih)
        self.btn_cancel.clicked.connect(self.reject)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_cancel)
        self.button_layout.addWidget(self.btn_load)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)
