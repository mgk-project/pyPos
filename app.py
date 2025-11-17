import sys
from PySide6.QtWidgets import QApplication, QStackedWidget
import requests
from views.login_window import LoginWindow
from views.dashboard_window import DashboardWindow
import os
from PySide6.QtGui import QFontDatabase, QFont
os.environ["QT_QPA_PLATFORM"] = "windows"  # default
# os.environ["QT_QPA_PLATFORM"] = "offscreen"  # jika ingin tanpa tampilan GUI (debug mode)

# Device Manager → Display adapters
from controllers.sinkron_controller import SinkronController
from controllers.login_controller import LoginController
from views.sinkron_view import SinkronView
from PySide6.QtWidgets import QMessageBox,QDialog
from utils.device_utils import get_device_id, cek_device_terdaftar  # Pastikan sudah kamu import
from views.device_registration_dialog import DeviceRegistrationDialog
from PySide6.QtWidgets import QApplication  # ✅ Jangan lupa pastikan import ini
from PySide6.QtCore import QObject, Signal,QEventLoop
from utils.audit_logger import log_audit
from PySide6.QtCore import QTimer
from models.sinkron_model import SinkronModel
from utils.config_utils import load_config


# from controllers.login_controller import LoginController  # import controller loginmu

# class AppController(QStackedWidget):
#     def show_dashboard(self, user_info):
#         # ... kode existing ...
#         self.dashboard_window = DashboardWindow(user_info, self)
#         self.addWidget(self.dashboard_window)
#         self.setCurrentWidget(self.dashboard_window)

#         # Start Auto-Cek Data Update Tiap 5 menit
#         self.sync_check_timer = QTimer()
#         self.sync_check_timer.timeout.connect(self.cek_data_update_ke_server)
#         self.sync_check_timer.start(5 * 60 * 1000)  # 5 menit

#         # Lakukan cek pertama kali saat dashboard muncul
#         self.cek_data_update_ke_server()

class AppController(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.model_sinkron = SinkronModel()  # <== Tambahkan ini
        self.current_user = None
        # self.login_window = LoginWindow(self)
        self.dashboard_window = None

        # self.login_window = LoginWindow(self)
        # self.login_controller = LoginController(
        #     login_view=self.login_window,
        #     app=self
        # )
        self.login_window = LoginWindow(None)  # sementara None dulu
        self.login_controller = LoginController(
            login_view=self.login_window,
            app=self
        )
        self.login_window.controller = self.login_controller  # inject setelah login_controller dibuat
        


        self.addWidget(self.login_window)
        self.setCurrentWidget(self.login_window)
        self.resize(400, 300)
        self.move(800, 100)


    

    def tampilkan_widget(self, widget):
            self.addWidget(widget)
            self.setCurrentWidget(widget)
    def login_success(self, user_info):
        self.current_user = user_info
        # Setelah login sukses:
        from utils.path_utils import get_db_path
        BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.argv[0])))
        DB_PATH = get_db_path() # os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')

        log_audit(DB_PATH, self.current_user["id"], "INSERT", "login", self.current_user["id"], "Login berhasil")
        # Buat tampilan sinkronisasi
        self.sinkron_view = SinkronView()
        self.sinkron_controller = SinkronController(self.sinkron_view, user_info, self)
   
        # ➕ Hubungkan sinyal selesai
        self.sinkron_controller.sinkron_selesai.connect(lambda: self.on_sinkron_selesai(user_info))

        # Tambahkan ke stack dan tampilkan
        self.addWidget(self.sinkron_view)
        self.setCurrentWidget(self.sinkron_view)
        self.sinkron_controller.mulai_sinkron()
        # supaya cepat , proses sinkron nya dimatikan dahulu 
        # self.show_dashboard(user_info)

    def on_sinkron_selesai(self, user_info):
        QMessageBox.information(None, "Sinkronisasi Data", "Sinkronisasi data server-lokal selesai")
        self.show_dashboard(user_info)

    def show_login(self, reset_size=False):
        try:
            device_id = get_device_id()
            device_data = cek_device_terdaftar(device_id)

            if not device_data:
                dialog = DeviceRegistrationDialog(self)
                dialog.exec()
                return

        except Exception as e:
            QMessageBox.critical(self, "Error Deteksi Device", f"Gagal mendeteksi device.\n{str(e)}")
            return

        self.setCurrentWidget(self.login_window)
        self.login_window.input_username.setFocus()

        # ✅ Kembalikan window ke ukuran normal (bukan maximize)
        self.showNormal()

        # ✅ Atur ulang ukuran window utama (AppController)
        self.setFixedSize(400, 300)
        self.move(800, 100)

        # ✅ Opsional: batasi juga ukuran login window supaya tidak melar
        self.login_window.setFixedSize(400, 300)



    # def show_dashboard(self, user_info):
    #     self.current_user = user_info

    #     from views.dashboard_window import DashboardWindow  # pastikan kamu punya file ini
    #     self.dashboard_window = DashboardWindow(user_info)
    #     self.addWidget(self.dashboard_window)
    #     self.setCurrentWidget(self.dashboard_window)
    #     self.showMaximized()

# self.dashboard_window = DashboardWindow(user_info, self)

#     # Cek status koneksi saat masuk dashboard
#     is_online = self.is_online()  # Kamu sudah punya fungsi ini
#     self.dashboard_window.update_koneksi_status(is_online)

#     # Tambahkan widget dashboard ke stack
#     self.addWidget(self.dashboard_window)
#     self.setCurrentWidget(self.dashboard_window)

#     # Set ukuran window dsb
#     self.showNormal()
#     self.setFixedSize(1900, 1000)
#     self.move(5, 5)

    def is_online(self):
        try:
            response = requests.head("https://beta.mayagrahakencana.com", timeout=3)
            # response = requests.head("https://beta.mayagrahakencana.com/ping", timeout=3) # untuk debug offline mode
            return response.status_code < 400  # 2xx or 3xx dianggap sukses
        except requests.RequestException:
            return False
        
        # def show_dashboard(self, user_info):
        # # ... kode existing ...
        # self.dashboard_window = DashboardWindow(user_info, self)
        # self.addWidget(self.dashboard_window)
        # self.setCurrentWidget(self.dashboard_window)

        # # Start Auto-Cek Data Update Tiap 5 menit
        # self.sync_check_timer = QTimer()
        # self.sync_check_timer.timeout.connect(self.cek_data_update_ke_server)
        # self.sync_check_timer.start(5 * 60 * 1000)  # 5 menit

        # # Lakukan cek pertama kali saat dashboard muncul
        # self.cek_data_update_ke_server()
    def show_dashboard(self, user_info):
        # Bersihkan widget dashboard lama jika ada
        if hasattr(self, "dashboard_window") and self.dashboard_window is not None:
            self.removeWidget(self.dashboard_window)

        self.current_user = user_info

        self.dashboard_window = DashboardWindow(user_info, self)
        # self.dashboard_window.showMaximized()
        # Cek status koneksi saat masuk dashboard
        is_online = self.is_online()  # Kamu sudah punya fungsi ini
        self.dashboard_window.update_koneksi_status(is_online)

        self.addWidget(self.dashboard_window)
        

        self.login_window.hide()
        print('✅ show_dashboard ditampilkan dalam mode maximized')

        self.setCurrentWidget(self.dashboard_window)

        # Start Auto-Cek Data Update Tiap 5 menit
        self.sync_check_timer = QTimer()
        self.sync_check_timer.timeout.connect(self.cek_data_update_ke_server)
        self.sync_check_timer.start(0.5 * 60 * 1000)  # 5 menit aslinya , untuk debugging di ganti jadi 30 s / 0.5 menit dulu saja

        # Lakukan cek pertama kali saat dashboard muncul
        self.cek_data_update_ke_server() # aslinya nyala, untuk kep debugging di off kan dulu

        # self.login_window.input_username.setFocus()

        # ✅ Kembalikan window ke ukuran normal (bukan maximize)
        self.showNormal()

        # ✅ Atur ulang ukuran window utama (AppController)
        self.setFixedSize(1900, 1000)
        self.move(5, 5)

        # ✅ Opsional: batasi juga ukuran login window supaya tidak melar
        self.dashboard_window.setFixedSize(1900, 1000)

    def cek_data_update_ke_server(self):
        # Cek update data server
        # Jika ada perubahan:
        if self.server_data_changed():
            print('data server berubah')
            self.dashboard_window.update_sync_status(True)
        else:
            self.dashboard_window.update_sync_status(False)
    def closeEvent(self, event):
        if hasattr(self, 'model_sinkron'):
            self.model_sinkron.close_connections()
        event.accept()

    def server_data_changed(self):
        # tables_to_check = [
        #     'produk', 'price', 'price_per_area', 'diskon',
        #     'diskon_customer', 'per_customers', 'per_employee',
        #     'setting_struk'
        # ]
        tables_to_check = [
            'per_customers'
        ]
        # tables_to_check = [
        #     'transaksi'
        # ]
        for table in tables_to_check:
            print(f"🔍 Cek perubahan table: {table}")
            # if self.model.is_data_updated(table):
            if self.model_sinkron.is_data_updated(table):

                print(f"⚠️ Ada perubahan data di server pada tabel: {table}")
                return True  # Ada perubahan, segera update indikator di dashboard
        print("✅ Data server up-to-date dengan lokal")
        return False  # Semua data lokal up-to-date

    # def cek_data_update_ke_server(self):
    #     if not self.is_online():
    #         self.dashboard_window.update_sync_status(False)
    #         return

    #     print("🕵️ Cek apakah ada data baru di server...")
    #     try:
    #         # Panggil API Cek Last Update (misal: /api/check_update)
    #         response = requests.get("https://beta.mayagrahakencana.com/api/check_update", timeout=5)
    #         data = response.json()

    #         # Misal response JSON:
    #         # { "needs_sync": true } atau { "needs_sync": false }
    #         needs_sync = data.get('needs_sync', False)
    #         self.dashboard_window.update_sync_status(needs_sync)

    #     except Exception as e:
    #         print(f"⚠️ Gagal cek update: {e}")
    #         # Tetap anggap tidak perlu sinkron jika gagal cek (atau atur sesuai kebutuhan)
    #         self.dashboard_window.update_sync_status(True)

    # def mulai_sinkronisasi_background(self):
    #     # Jalankan sinkronisasi background
    #     print("🚀 Proses sinkronisasi background dimulai...")
    #     # Kamu bisa panggil SinkronController di sini.
    #     self.sinkron_controller = SinkronController(self.dashboard_window, self.current_user, self)
    #     self.sinkron_controller.sinkron_selesai.connect(self.on_sinkron_selesai_notifikasi)
    #     self.sinkron_controller.mulai_sinkron()
    def mulai_sinkronisasi_background(self):
        print("🚀 Sinkronisasi Silent Background dimulai...")
        self.sinkron_controller = SinkronController(None, self.current_user, self, silent_mode=True)
        self.sinkron_controller.sinkron_selesai.connect(self.on_sinkron_selesai_notifikasi)
        self.sinkron_controller.mulai_sinkron()
        
    def on_sinkron_selesai_notifikasi(self):
        print("✅ Sinkronisasi selesai (background)")
        QMessageBox.information(None, "Sinkronisasi", "Data berhasil disinkronisasi.")
        self.dashboard_window.update_sync_status(False)



if __name__ == "__main__":
    app = QApplication(sys.argv)

        # ⬇ Tambahkan pemanggilan stylesheet di sini
    # try:
    #     with open("resources/styles/main.qss.css", "r") as f:
    #         app.setStyleSheet(f.read())
    # except Exception as e:
    #     print("Gagal memuat QSS:", e)
    import sys
    import os

    # Temukan path file QSS dengan cara yang aman (baik saat run normal maupun dari .exe)
    if getattr(sys, 'frozen', False):
        # Saat sudah dibundle ke .exe
        base_path = sys._MEIPASS
    else:
        # Saat dijalankan langsung
        base_path = os.path.dirname(os.path.abspath(__file__))

    qss_path = os.path.join(base_path, "resources", "styles", "main.qss.css")
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Gagal memuat QSS:", e)
    # Font (opsional)
    font_path = "resources/fonts/DejaVuSans.ttf"
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)
        app.setFont(QFont("DejaVu Sans", 9))
        
    # the first all , sinkronkan data server ke pos dahulu 
    
    font_path = "resources/fonts/DejaVuSans.ttf"
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)
        app.setFont(QFont("DejaVu Sans", 9))


# pakai cara tim 1
    from utils.device_utils import cek_device_ke_server, get_device_id

    
    from views.device_registration_dialog import DeviceRegistrationDialog

    # Cek device
    device_id = get_device_id() #"145862430726560" # sementara saja karena menunggu proses apporoval get_device_id()
    print(f'cek device id ke server nya = {device_id}')
    result = cek_device_ke_server(device_id)

    if result['status'] == 200:
        print("✅ Device terdaftar, Silakan Login")
       
    elif result['status'] == 202:
        QMessageBox.information(None, "Registrasi", "Registrasi menunggu proses approved. Silakan Cek Lagi Lain Kali.")
        sys.exit(0)
    elif result['status'] == 404:
        dialog = DeviceRegistrationDialog()
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(None, "Registrasi", "Registrasi selesai. Silakan buka ulang aplikasi.")
        else:
            QMessageBox.warning(None, "Registrasi", "Registrasi dibatalkan.")
        sys.exit(0)
    else:
        QMessageBox.critical(None, "Error", f"Device check failed: {result.get('reason', 'Unknown error')}")
        sys.exit(0)
    # if result['status'] == 200:
    #     # print("✅ Device terdaftar, Silakan Login")
    #     dialog = DeviceRegistrationDialog()
    #     if dialog.exec() == QDialog.Accepted:
    #         QMessageBox.information(None, "Registrasi", "Registrasi selesai. Silakan buka ulang aplikasi.")
    #     else:
    #         QMessageBox.warning(None, "Registrasi", "Registrasi dibatalkan.")
    #     sys.exit(0)

    # elif result['status'] == 202:
    #     QMessageBox.information(None, "Registrasi", "Registrasi menunggu proses approved. Silakan Cek Lagi Lain Kali.")
    #     sys.exit(0)
    # elif result['status'] == 404:
    #     dialog = DeviceRegistrationDialog()
    #     if dialog.exec() == QDialog.Accepted:
    #         QMessageBox.information(None, "Registrasi", "Registrasi selesai. Silakan buka ulang aplikasi.")
    #     else:
    #         QMessageBox.warning(None, "Registrasi", "Registrasi dibatalkan.")
    #     sys.exit(0)
    # else:
    #     QMessageBox.critical(None, "Error", f"Device check failed: {result.get('reason', 'Unknown error')}")
    #     sys.exit(0)
    

    # # ✅ Device valid, baru buat dan tampilkan AppController
    # login_controller = LoginController(
    #         login_view=self.login_window,
    #         app=self  # supaya bisa panggil show_dashboard nanti
    #     )
    # controller = login_controller

    controller = AppController()
    controller.show()
    sys.exit(app.exec())

