import os
import sys
import requests
import sqlite3
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox
from utils.path_utils import get_db_path
from utils.audit_logger import log_audit
import hashlib

class LoginController:
    # def __init__(self, view, stacked_widget):
    def __init__(self, login_view, app):
        print('masuk login controller')
        # self.view = view
        # self.stacked_widget = stacked_widget
        # self.current_user = None

        # self.login_view = login_view
        # self.app = app
        self.login_view = login_view
        self.app = app
        self.stacked_widget = app  # ✅ Ini penting agar bisa akses .addWidget()

        # ⬇️ Hubungkan tombol login (misal tombol OK ditekan)
        self.login_view.button_login.clicked.connect(self.login_success)
    def proses_login(self, username, password):
        # validasi kosong
        
        if not username or not password:
            QMessageBox.warning(self.login_view, "Login Gagal", "Username dan password harus diisi.")
            return

        password_hash = hashlib.md5(password.encode()).hexdigest()

        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama, password FROM per_employee WHERE nama = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user["password"] == password_hash:
            user_info = {"id": user["id"], "nama": user["nama"]}
            print("🟢 LoginController: login sukses", user_info)
            # self.app.login_success(user_info)
            self.login_success(user_info)
            self.login_view.clear_fields()
        else:
            QMessageBox.warning(self.login_view, "Login Gagal", "Username atau password salah.")

    def login_success(self, user_info):
        print('masuk login controller.py')
        self.current_user = user_info

        # if not self.is_online():
        #     jawab = QMessageBox.question(
        #         None,
        #         "Mode Offline",
        #         "Koneksi internet tidak tersedia.\n"
        #         "POS ini membutuhkan koneksi internet saat login.\n\n"
        #         "Apakah Anda ingin login dalam mode darurat offline dengan persetujuan Admin?",
        #         QMessageBox.Yes | QMessageBox.No
        #     )
        if  not self.is_online():
            print('cek offline nda')
            jawab = QMessageBox.question(
                None,
                "Mode Offline",
                "Koneksi internet tidak tersedia.\n"
                "POS ini membutuhkan koneksi internet saat login.\n\n"
                "Apakah Anda ingin login dalam mode darurat offline dengan persetujuan Admin?",
                QMessageBox.Yes | QMessageBox.No
            )

            if jawab == QMessageBox.Yes:
                if self.otentikasi_admin():
                    QMessageBox.warning(
                        None,
                        "PERHATIAN!",
                        "Anda sedang login dalam kondisi offline.\n"
                        "Beberapa fitur mungkin tidak tersedia:\n"
                        "- Data produk tidak update\n"
                        "- Harga atau diskon bisa saja tidak akurat\n"
                        "- Data penjualan tidak akan terkirim ke server\n\n"
                        "Gunakan data terakhir yang tersedia di sistem lokal."
                    )
                    self.current_user["mode"] = "offline"
                    # log_audit(get_db_path, self.current_user["id"], "LOGIN_OFFLINE", "Login offline dengan admin")
                    log_audit(get_db_path(), self.current_user["id"], "INSERT", "login offline", self.current_user["id"], "Login offline dengan admin berhasil")
                    self.lanjutkan_login_offline()
                    return
                else:
                    QMessageBox.critical(None, "Gagal", "Otorisasi admin gagal.")
                    return
            else:
                return  # Tidak lanjut login

        # Jika online lanjutkan normal
        self.app.login_success(user_info)
        # BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.argv[0])))
        # DB_PATH = get_db_path()
        # log_audit(DB_PATH, self.current_user["id"], "INSERT", "login", self.current_user["id"], "Login berhasil")

        # # Tampilkan sinkronisasi
        # from views.sinkron_data_view import SinkronView
        # from controllers.sinkron_data_controller import SinkronController

        # self.sinkron_view = SinkronView()
        # self.sinkron_controller = SinkronController(self.sinkron_view, self.current_user, self)

        # self.stacked_widget.addWidget(self.sinkron_view)
        # self.stacked_widget.setCurrentWidget(self.sinkron_view)

        # # Jalankan sinkron lalu lanjut ke dashboard saat selesai
        # def selesai_sinkron():
        #     QMessageBox.information(None, "Sinkronisasi Data", "Sinkronisasi data server-lokal selesai")
        #     self.show_dashboard(self.current_user)

        # self.sinkron_controller.sinkron_selesai.connect(selesai_sinkron)
        # self.sinkron_controller.mulai_sinkron()

    # def is_online(self):
    #     try:
    #         response = requests.get("https://beta.mayagrahakencana.com/ping", timeout=3)
    #         return response.status_code == 200
    #     except requests.RequestException:
    #         return False
    # import requests

    def is_online(self):
        try:
            response = requests.head("https://beta.mayagrahakencana.com", timeout=3)
            return response.status_code < 400  # 2xx or 3xx dianggap sukses
        except requests.RequestException:
            return False


    def otentikasi_admin(self):
        dialog = QDialog()
        dialog.setWindowTitle("Otorisasi Admin Toko")
        layout = QFormLayout(dialog)

        username_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)

        layout.addRow("Username Admin:", username_input)
        layout.addRow("Password:", password_input)

        btn_login = QPushButton("Verifikasi")
        layout.addRow(btn_login)

        success = False

        def verifikasi():
            nonlocal success
            username = username_input.text()
            password = password_input.text()
            if self.cek_admin_lokal(username, password):
                success = True
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Gagal", "Username/password admin salah")

        btn_login.clicked.connect(verifikasi)
        dialog.exec()
        return success

    def cek_admin_lokal(self, username, password):
        try:
            password_hash = hashlib.md5(password.encode()).hexdigest()

            conn = sqlite3.connect(get_db_path())
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT id, nama, password FROM per_employee WHERE nama = ? AND nama_login like 'admin%' ", (username,))
            row = cur.fetchone()
            conn.close()

            if row and row["password"] == password_hash:
                user_info = {"id": row["id"], "nama": row["nama"]}
                print("🟢 LoginController: login offline sukses", user_info)
                
            # conn = sqlite3.connect(get_db_path())
            # cur = conn.cursor()
            # print(f"SELECT * FROM per_employee WHERE nama_login like '{username}%' AND nama like 'admin%'")
            # cur.execute("SELECT * FROM per_employee WHERE nama_login like '?%' AND nama like 'admin%'", (username,))
            # row = cur.fetchone()
            # if row and row[0] == password:
                return True
        except:
            pass
        return False

    def lanjutkan_login_offline(self):
        # Lanjutkan login offline jika otorisasi berhasil
        self.app.show_dashboard(self.current_user)
        # self.show_dashboard(self.current_user)

    def show_dashboard(self, user_info):
        from views.dashboard_window import DashboardWindow
        dashboard = DashboardWindow(user_info)
        self.stacked_widget.addWidget(dashboard)
        self.stacked_widget.setCurrentWidget(dashboard)
