from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton
from utils.config_utils import load_config, save_config

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfigurasi Aplikasi")
        layout = QFormLayout(self)

        cfg = load_config()

        self.api_url_input = QLineEdit()
        self.api_url_input.setText(cfg.get("api_base_url", ""))
        layout.addRow("API Base URL", self.api_url_input)

        self.client_name_input = QLineEdit()
        self.client_name_input.setText(cfg.get("client_name", ""))
        layout.addRow("Client Name", self.client_name_input)

        self.timeout_input = QLineEdit()
        self.timeout_input.setText(str(cfg.get("request_timeout", 3)))
        layout.addRow("Request Timeout", self.timeout_input)

        btn_save = QPushButton("Simpan")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)

    def save(self):
        try:
            timeout = int(self.timeout_input.text())
        except ValueError:
            timeout = 3
        cfg = {
            "api_base_url": self.api_url_input.text().strip(),
            "client_name": self.client_name_input.text().strip(),
            "request_timeout": timeout,
        }
        save_config(cfg)
        self.accept()