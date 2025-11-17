from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout

class DiskonView(QWidget):
    def __init__(self):
        super().__init__()
        self.te_keterangan_diskon = QTextEdit()
        self.te_keterangan_diskon.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.te_keterangan_diskon)
        self.setLayout(layout)

    def tampilkan_keterangan_diskon(self, teks):
        self.te_keterangan_diskon.setText(teks)
