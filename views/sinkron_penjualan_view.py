from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from controllers.sinkron_penjualan_controller import SinkronPenjualanController

class SinkronPenjualanView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sinkronisasi Data Penjualan (30 Hari Terakhir)")

        self.layout = QVBoxLayout()
        self.info_label = QLabel("Klik untuk mulai sinkronisasi:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.sync_button = QPushButton("Mulai Sinkronisasi")
        self.sync_button.setStyleSheet("""
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

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.sync_button)
        self.layout.addWidget(self.output_text)
        self.setLayout(self.layout)

        self.sync_button.clicked.connect(self.mulai_sinkronisasi)

    def mulai_sinkronisasi(self):
        self.output_text.clear()
        self.sync_button.setEnabled(False)

        self.worker = SinkronPenjualanController()
        self.worker.progress.connect(self.update_log)
        self.worker.selesai.connect(self.sinkron_selesai)
        self.worker.start()

    def update_log(self, text):
        self.output_text.append(text)

    def sinkron_selesai(self, text):
        self.output_text.append("\n" + text)
        self.sync_button.setEnabled(True)
