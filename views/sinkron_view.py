from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar,
    QTextEdit, QFrame, QSizePolicy, QApplication
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtCore import QObject, Signal,Slot
from PySide6.QtWidgets import QMessageBox

class SinkronView(QWidget):
    def __init__(self):
        super().__init__()
        self.emit_selesai_sinkron = None  # Akan di-set dari controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Sinkronisasi Data POS")
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Judul utama
        title = QLabel("🚀 Sinkronisasi Data Pusat ke POS Lokal")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        # Status umum
        self.label_status = QLabel("Menyiapkan sinkronisasi...")
        self.label_status.setFont(QFont("Segoe UI", 11))
        self.label_status.setAlignment(Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(25)

        # Log detail
        self.label_detail = QTextEdit()
        self.label_detail.setReadOnly(True)
        self.label_detail.setFont(QFont("Consolas", 9))
        self.label_detail.setStyleSheet("background-color: #f0f0f0;")
        self.label_detail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Rangkai layout
        main_layout.addWidget(title)
        main_layout.addWidget(separator)
        main_layout.addWidget(self.label_status)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.label_detail)

        self.setLayout(main_layout)

    def set_controller(self, controller):
        self.controller = controller

    def update_progress(self, persen, status="", detail_log=""):
        self.progress_bar.setValue(persen)
        self.label_status.setText(status)
        if detail_log:
            self.label_detail.append(detail_log)
        QApplication.processEvents()


    @Slot(int, str, str)
    def tampilkan_progress(self, percent, status, detail):
        self.progress_bar.setValue(percent)
        self.label_status.setText(status)
        if detail:
            self.label_detail.append(detail)



