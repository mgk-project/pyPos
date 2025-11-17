from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
import hashlib
import sqlite3
from views.config_dialog import ConfigDialog
from views.master_password_dialog import MasterPasswordDialog
from utils.config_utils import load_config
# from utils.device_utils import get_device_id, cek_device_terdaftar  # Pastikan sudah kamu import

# Koneksi SQLite
# import sys
# import os

# BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
# DB_PATH = os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
# print("DB Path:", DB_PATH)
import os
import sys
from utils.path_utils import get_db_path
BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.argv[0])))
DB_PATH = get_db_path() # os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')

# DB_PATH = "z:/pos_hipermarket/db/beta_sb_pos_sqlite.db"
class LoginWindow(QWidget):
    def __init__(self, controller):  # Bukan app_controller
        super().__init__()
        self.controller = controller
        # self.init_ui()
# class LoginWindow(QWidget):
#     def __init__(self, app_controller):
#         super().__init__()
#         self.controller = app_controller

        layout = QVBoxLayout()

        cfg = load_config()

        self.label_username = QLabel("Username:")
        self.input_username = QLineEdit()
        self.label_password = QLabel("Password:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.returnPressed.connect(self.check_login)
        print('masuk login')
        self.button_login = QPushButton("Login")
        self.button_login.setStyleSheet("""
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
        self.button_login.clicked.connect(self.check_login)

        layout.addWidget(self.label_username)
        layout.addWidget(self.input_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.button_login)

        # rekomendasi tim 1
        self.button_config = QPushButton("Config")
        self.button_config.clicked.connect(self.open_config)
        layout.addWidget(self.button_config)

        # self.setLayout(layout)
        # self.setWindowTitle("Login")
        self.setLayout(layout)
        client_name = cfg.get("client_name", "")
        title = f"Login - {client_name}" if client_name else "Login"
        self.setWindowTitle(title)

        # ✅ Tambahkan ini agar ukuran login window selalu konsisten
        self.setFixedSize(400, 300)


    def check_login(self):
            # def check_login(self):
        username = self.input_username.text()
        password = self.input_password.text()
        self.controller.proses_login(username, password)
    
    
        # username = self.input_username.text()
        # password = self.input_password.text()
        # print("🧪 Cek Login:", username, password)
        # print("🧪 Path DB:", DB_PATH)
        # # print("🧪 DB exists?", os.path.exists(DB_PATH))

        # if not username or not password:
        #     QMessageBox.warning(self, "Login Gagal", "Username dan password harus diisi.")
        #     return

        # password_hash = hashlib.md5(password.encode()).hexdigest()

        # conn = sqlite3.connect(DB_PATH)
        # conn.row_factory = sqlite3.Row
        # cursor = conn.cursor()
        # cursor.execute("SELECT id, nama, password FROM per_employee WHERE nama = ?", (username,))
        # user = cursor.fetchone()
        # conn.close()

        # if user and user["password"] == password_hash:
        #     user_info = {"id": user["id"], "nama": user["nama"]}
        #     print("🟢 Login berhasil:", user_info)

        #     self.controller.login_success(user_info)
        #     self.clear_fields()
        # else:
        #     QMessageBox.warning(self, "Login Gagal", "Username atau password salah.")
    def clear_fields(self):
        self.input_username.clear()
        self.input_password.clear()
        self.input_username.setFocus()

    def open_config(self):
            pwd_dialog = MasterPasswordDialog(self)
            if pwd_dialog.exec() == QDialog.Accepted:
                dlg = ConfigDialog(self)
                if dlg.exec() == QDialog.Accepted:
                    if self.controller and hasattr(self.controller, 'app'):
                        self.controller.app.config = load_config()
                    client_name = self.controller.app.config.get("client_name", "")
                    title = f"Login - {client_name}" if client_name else "Login"