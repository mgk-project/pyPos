from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QMessageBox
from PySide6.QtCore import Signal

class SinkronDataView(QWidget):
    sinkronkan_ditekan = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sinkronisasi Data")
        self.layout = QVBoxLayout(self)

        self.label_info = QLabel("Tekan tombol untuk mulai sinkronisasi data dari server pusat.")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        self.btn_sinkron = QPushButton("Sinkronkan")
        self.btn_sinkron.setStyleSheet("""
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
        self.btn_sinkron.clicked.connect(self.konfirmasi_sinkron)

        self.layout.addWidget(self.label_info)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.btn_sinkron)

    def konfirmasi_sinkron(self):
        msg = QMessageBox.question(
            self,
            "Konfirmasi Sinkron",
            "Anda yakin ingin sinkron data 5 hari terakhir?",
            QMessageBox.Yes | QMessageBox.No
        )
        if msg == QMessageBox.Yes:
            self.sinkronkan_ditekan.emit()

    def mulai_progress(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Mode tak tentu

    def selesai_progress(self):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)

    def tampilkan_info(self, sukses: bool, pesan: str):
        QMessageBox.information(self, "Hasil Sinkron", pesan if sukses else f"Gagal: {pesan}")
