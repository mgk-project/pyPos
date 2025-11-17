from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
import hashlib

MASTER_PASSWORD_HASH = hashlib.sha256("dev-only-secret".encode()).hexdigest()

class MasterPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Master Password")
        layout = QVBoxLayout(self)

        self.label = QLabel("Masukkan master password:")
        layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input)

        self.button = QPushButton("OK")
        self.button.clicked.connect(self.verify_password)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def verify_password(self):
        entered = self.input.text()
        if hashlib.sha256(entered.encode()).hexdigest() == MASTER_PASSWORD_HASH:
            self.accept()
        else:
            QMessageBox.warning(self, "Gagal", "Master password salah")
            self.input.clear()
            self.input.setFocus()