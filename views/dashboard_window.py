from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget
)
from PySide6.QtGui import QKeySequence, QShortcut

from views.customer_setup_view import CustomerSetupView
from controllers.customer_controller import CustomerController

from controllers.barang_controller import BarangController

from controllers.transaksi_penjualan_controller import TransaksiPenjualanController

from controllers.sinkron_data_controller import SinkronDataController
from views.sinkron_data_view import SinkronDataView

from controllers.sinkron_controller import SinkronController
from views.sinkron_view import SinkronView

from views.sinkron_penjualan_view import SinkronPenjualanView
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
import sys
from views.return_view import ReturnView
from models.return_model import ReturnModel

# untuk main bar
from PySide6.QtWidgets import QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import QDateTime, QTimer
from controllers.dashboard_info_controller import DashboardInfoController
from PySide6.QtCore import Qt  # ✅ Ini yang penting untuk alignment
from PySide6.QtWidgets import QDialog
from utils.settlement_checker import SettlementHandler
from controllers.printer_settings_controller import PrinterSettingsController
from views.printer_settings_view import PrinterSettingsView

# # untuk setting printer
# from views.printer_setting_view import PrinterSettingView
# from models.printer_model import PrinterModel

# class DashboardWindow(QWidget):
#     def __init__(self, user_info, app_controller):
#         super().__init__()
#         self.user_info = user_info
#         self.app_controller = app_controller

#         # Status Koneksi + Sinkron
#         self.status_label = QLabel()  # Online/Offline
#         self.sync_status_label = QLabel("✅ Data Up-to-date")  # Status Sinkron
#         self.silent_sync_label = QLabel("")  # Indikator Sinkron Silent (kecil)


class DashboardWindow(QMainWindow):
    def __init__(self, user_info, app_controller):
        super().__init__()
        self.user_info = user_info
        self.controller = app_controller
        self.printer_settings_controller = PrinterSettingsController()

        self.status_label = QLabel()  # <-- Status Mode Label
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.sync_status_label = QLabel()  # Status Sinkron
        self.sync_button = QPushButton("Sinkron Sekarang")
        self.sync_button.hide()  # Sembunyikan awalnya
        self.sync_button.clicked.connect(self.lakukan_sinkronisasi)
        self.silent_sync_label = QLabel("")  # Indikator Sinkron Silent (kecil)


        # Cek Status Awal
        self.update_koneksi_status(is_online=False)  # default offline dulu



        self.setWindowTitle("Dashboard - Aplikasi POS")
        self.init_ui()

    # Timer auto-refresh koneksi
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cek_koneksi_realtime)
        self.timer.start(30000)  # cek tiap 30 detik (30000 ms)

    def cek_koneksi_realtime(self):
        is_online = self.controller.is_online()
        self.update_koneksi_status(is_online)

    def update_koneksi_status(self, is_online):
        if is_online:
            self.status_label.setText("🟢 ONLINE MODE")
            self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        else:
            self.status_label.setText("🔴 OFFLINE MODE")
            self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")

    # def update_koneksi_status(self, is_online):
    #     if is_online:
    #         self.status_label.setText("🟢 ONLINE MODE")
    #         self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
    #     else:
    #         self.status_label.setText("🔴 OFFLINE MODE")
    #         self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")

    def update_sync_status(self, needs_sync):
        if needs_sync:
            self.sync_status_label.setText("⚠️ Data Perlu Sinkronisasi")
            self.sync_status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 14px;")
            self.sync_button.show()
        else:
            self.sync_status_label.setText("✅ Data Up-to-date")
            self.sync_status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
            self.sync_button.hide()

    def lakukan_sinkronisasi(self):
        print("🔄 Sinkronisasi dimulai...")
        self.controller.mulai_sinkronisasi_background()


# # Layout header kanan atas
#         header_right_layout = QHBoxLayout()
#         header_right_layout.addWidget(self.status_label)
#         header_right_layout.addSpacing(10)
#         header_right_layout.addWidget(self.sync_status_label)
#         header_right_layout.addWidget(self.sync_button)

#         # Layout Utama Dashboard
#         main_layout = QVBoxLayout()
#         main_layout.addLayout(header_right_layout)
#         # Tambahkan komponen dashboard lainnya...

#         self.setLayout(main_layout)

    def set_sinkron_status(self, text):
        self.silent_sync_label.setText(text)
        
    def init_ui(self):
        # ---------- MAIN BAR ATAS ----------
        self.status_label = QLabel()  # <-- Status Mode Label
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Layout Header (contoh)
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"Selamat datang, {self.user_info['nama']}"))
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)  # Tambahkan Status di Header
        header_layout.addSpacing(10)
        header_layout.addWidget(self.sync_status_label)
        header_layout.addWidget(self.sync_button)
        header_layout.addWidget(self.silent_sync_label)


    #     header_layout = QHBoxLayout()
    #     header_layout.addWidget(self.status_label)
    #     header_layout.addWidget(self.sync_status_label)
    #     header_layout.addWidget(self.silent_sync_label)

    #     main_layout = QVBoxLayout()
    #     main_layout.addLayout(header_layout)
    #     # ...layout lain...

    #     self.setLayout(main_layout)

    # def set_sinkron_status(self, text):
    #     self.silent_sync_label.setText(text)
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)


        main_bar = QWidget()
        main_bar.setStyleSheet("background-color: #2C3E50; color: white; padding: 6px;")
        main_bar_layout = QHBoxLayout(main_bar)

        self.label_title = QLabel("🧾 POS System Review #1, Review #2, Review #3 (try 1)  per 24 oki 2025") #QLabel("🧾 POS System V2.1")
        self.label_title.setStyleSheet("font-weight: bold; font-size: 18px;")

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.label_user = QLabel(f"👤 {self.user_info['nama']}")
        self.label_waktu = QLabel("")
        self.btn_logout_top = QPushButton("Logout")
        self.btn_logout_top.setStyleSheet("background-color: orange; color: white; padding: 5px 12px;")
        self.btn_logout_top.clicked.connect(self.logout)

        main_bar_layout.addWidget(self.label_title)
        main_bar_layout.addItem(spacer)
        main_bar_layout.addWidget(self.label_user)
        main_bar_layout.addSpacing(10)
        main_bar_layout.addWidget(self.label_waktu)
        main_bar_layout.addSpacing(10)
        main_bar_layout.addWidget(self.btn_logout_top)


        # Waktu real-time
        timer = QTimer(self)
        timer.timeout.connect(self.update_waktu)
        timer.start(1000)
        self.update_waktu()

        # ---------- LAYOUT UTAMA ----------
        # main_widget = QWidget()
        # layout_utama = QHBoxLayout(main_widget)
        main_widget = QWidget()
        layout_utama = QHBoxLayout(main_widget)

        # Sidebar
        sidebar_layout = QVBoxLayout()
        
        self.menu_buttons = {
            "Beranda": QPushButton("🏠 Beranda"),
            "Penjualan": QPushButton("💰 Penjualan"),
            "Sinkronkan Data": QPushButton("🔄 Sinkronisasi Data"),
            "Return Penjualan": QPushButton("🔄 Return Penjualan"),
            "Setting Printer": QPushButton("🔄 Setting Printer"),
            # "Sinkronkan Penjualan":QPushButton("Sinkonisasi Data Penjualan - Sinkron hanya jika outdated datanya"),
            "Logout": QPushButton("🚪 Logout")
        }

        for btn in self.menu_buttons.values():
            sidebar_layout.addWidget(btn)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("SidebarWidget")
        for btn in self.menu_buttons.values():
            btn.setFixedHeight(36)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1D8348;  /* Hijau tua */
                    color: white;
                    font-weight: bold;
                    border: none;
                    text-align: left;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #239B56;
                }
            """)
            sidebar_layout.addWidget(btn)
        sidebar_layout.setSpacing(2)
        sidebar_layout.setContentsMargins(4, 4, 4, 4)

        # for btn in self.menu_buttons.values():
        #     btn.setProperty("menuButton", True)
        #     btn.setProperty("active", True)
        #     btn.setStyle(btn.style())  # paksa refresh style

        # sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("background-color: #145A32;")
        # sidebar_widget.setLayout(sidebar_layout)
        # sidebar_widget.setFixedWidth(400)

        # Content Area
        self.content_area = QStackedWidget()
        # self.welcome_label = QLabel(f"Selamat datang, {self.user_info['nama']}")
        self.welcome_label = QLabel("")
        self.content_area.addWidget(self.welcome_label)

        # Tambahkan di __init__ DashboardWindow
        # self.dashboard_layout.addWidget(self.dashboard_info_view, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Koneksi SQLite
        # conn_sqlite = sqlite3.connect(db_path)
        import sys
        import os
        from utils.path_utils import get_db_path
        BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
        DB_PATH = get_db_path() #os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
        print("DB Path dashboard windows:", DB_PATH)


        # self.dashboard_info = DashboardInfoController("z:/beta_desktop/db/beta_sb_pos_sqlite.db")
        self.dashboard_info = DashboardInfoController(DB_PATH)
        self.content_area.addWidget(self.dashboard_info.get_view() )  # sesuaikan layout Anda


        # Setup Customer View
        self.customer_setup_widget = CustomerSetupView()
        # self.content_area.addWidget(self.customer_setup_widget)

        # Setup Barang View
        self.barang_setup_widget = BarangController()  # Sudah return view di dalamnya
        # self.content_area.addWidget(self.barang_setup_widget)

        # Setup Transaksi View
        # Koneksi SQLite
        import sys
        import os
        from utils.path_utils import get_db_path
        BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))  # Ini akan menunjuk ke lokasi app.py saat app dijalankan
        DB_PATH = get_db_path() # os.path.join(BASE_DIR, 'db', 'beta_sb_pos_sqlite.db')
        print("DB Path dashboard windows:", DB_PATH)

        # conn_sqlite = sqlite3.connect(db_path)
        customer_list = CustomerController().load_all_customers()
        # self.transaksi_controller = TransaksiPenjualanController(
        #     customer_list,
        #     self.user_info,
        #     DB_PATH
        # )
        self.transaksi_controller = TransaksiPenjualanController(customer_list, self.user_info, DB_PATH, parent_window=self)
        # self.transaksi_view = transaksi_controller.view
        # self.content_area.setCurrentWidget(transaksi_view)

        # self.transaksi_controller = TransaksiPenjualanController(
        #     customer_list,
        #     self.user_info,
        #     "z:/beta_desktop/db/beta_sb_pos_sqlite.db"
        # )
        
        self.transaksi_view = self.transaksi_controller.view
        self.content_area.addWidget(self.transaksi_view)

        # Layout penggabung
        layout_utama.addWidget(sidebar_widget)
        layout_utama.addWidget(self.content_area)
        # self.setCentralWidget(main_widget)
        # tambahkan main bar 
        main_layout.addWidget(main_bar)
        main_layout.addWidget(main_widget)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Event handler menu
        self.menu_buttons["Beranda"].clicked.connect(
            # lambda: self.content_area.setCurrentWidget(self.welcome_label)
            lambda: self.content_area.setCurrentWidget(self.dashboard_info.get_view())
        )
        # self.menu_buttons["Penjualan"].clicked.connect(
        #     lambda: self.content_area.setCurrentWidget(self.transaksi_view)
        # )
        self.menu_buttons["Penjualan"].clicked.connect(self.buka_penjualan)

        self.menu_buttons["Sinkronkan Data"].clicked.connect(
            self.buka_menu_sinkron_data
        )
        self.menu_buttons["Return Penjualan"].clicked.connect(
            self.buka_menu_return_penjualan
        )

        self.menu_buttons["Setting Printer"].clicked.connect(
            # self.buka_menu_setting_printer
            self.buka_pengaturan_printer
        )
        
        # self.menu_buttons["Sinkronkan Penjualan"].clicked.connect(
        #     self.buka_menu_sinkron_penjualan
        # )
        self.menu_buttons["Logout"].clicked.connect(self.logout)

        # Shortcut
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(
            # lambda: self.content_area.setCurrentWidget(self.transaksi_view)
            self.buka_penjualan
        )
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.buka_menu_return_penjualan)
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(lambda: self.content_area.setCurrentWidget(self.dashboard_info.get_view()))

        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.logout)

    def update_waktu(self):
        now = QDateTime.currentDateTime()
        self.label_waktu.setText(now.toString("dddd, dd MMMM yyyy hh:mm:ss"))

    def buka_penjualan(self):
        self.content_area.setCurrentWidget(self.transaksi_view)
        self.transaksi_controller.cek_status_settlement()
        # # Dalam init atau fungsi tertentu
        # self.transaksi_modal = QDialog(self.transaksi_view)
        # self.settlement_handler = SettlementHandler(self.transaksi_view, self.transaksi_modal)

        # # Saat ingin cek settlement
        # self.settlement_handler.cek_status_settlement()
        # Fokus ke barang_input setelah sedikit delay agar UI stabil
        QTimer.singleShot(100, lambda: self.transaksi_view.barang_input.setFocus())

    # def buka_menu_sinkron_penjualan(self):
    #     if not hasattr(self, 'sinkron_penjualan_view'):
    #         self.sinkron_penjualan_view = SinkronPenjualanView()
    #         self.content_area.addWidget(self.sinkron_penjualan_view)
    #     self.content_area.setCurrentWidget(self.sinkron_penjualan_view)

    def buka_menu_sinkron_data(self):
        print('sinkronkan panggil buka_menu_sinkron_data_di_dashboard_window')
        # Inisialisasi view dan controller sinkron
        self.sinkron_view = SinkronView()
        self.sinkron_controller = SinkronController(
            view=self.sinkron_view,
            user_info=self.user_info,
            app_controller=self.controller  # <- penting: ini AppController
        )

        # Tambahkan tampilan ke content area
        self.content_area.addWidget(self.sinkron_view)
        self.content_area.setCurrentWidget(self.sinkron_view)

        # Jalankan proses sinkron
        self.sinkron_controller.mulai_sinkron()

    def buka_menu_return_penjualan(self):
        print('return penjualan panggil buka_menu_return_penjualan_di_dashboard_window')
        # Inisialisasi view dan controller sinkron
        # model = ReturnModel()
        # dlg = ReturnView(transaksi_id="TX123", model=model)
        # dlg.exec()
        mdl = ReturnModel()
        dlg = ReturnView(mdl)
        dlg.exec()
        mdl.close()        
        # self.sinkron_view = SinkronView()
        # self.sinkron_controller = SinkronController(
        #     view=self.sinkron_view,
        #     user_info=self.user_info,
        #     app_controller=self.controller  # <- penting: ini AppController
        # )

        # # Tambahkan tampilan ke content area
        # self.content_area.addWidget(self.sinkron_view)
        # self.content_area.setCurrentWidget(self.sinkron_view)

        # # Jalankan proses sinkron
        # self.sinkron_controller.mulai_sinkron()


# from models.printer_model import PrinterModel

# def buka_menu_setting_printer(self):
#     mdl = PrinterModel()
#     view = PrinterSettingView(mdl)   # ← model wajib dikirim
#     ctrl = PrinterController(mdl, view)
#     view.exec()
#     mdl.close()

    

    def buka_menu_setting_printer(self):
        from models.printer_model import PrinterModel
        from views.printer_setting_view import PrinterSettingView
        from controllers.printer_controller import PrinterController
        mdl = PrinterModel()
        view = PrinterSettingView(mdl)
        ctrl = PrinterController(mdl, view)
        view.exec()
    # def buka_menu_setting_printer(self):
    #     from models.printer_model import PrinterModel
    #     from views.printer_setting_view import PrinterSettingView
    #     from controllers.printer_controller import PrinterController
    #     from utils.path_utils import get_db_path
    #     print('masuk menu buka menu setting printer')
    #     mdl = PrinterModel(get_db_path())
    #     view = PrinterSettingView(mdl)
    #     ctrl = PrinterController(mdl, view)
    #     view.exec()
    #     mdl.close()
        # view.show()

    def buka_pengaturan_printer(self):
        dlg = PrinterSettingsView(self.printer_settings_controller, self)
        dlg.exec()

    def logout(self):
        print('masuk logout')
        self.controller.show_login(reset_size=True)

        # self.controller.show_login()
