from PySide6.QtCore import QThread
from sinkron_thread import SinkronWorker
from models.sinkron_model import SinkronModel
from PySide6.QtCore import QObject, Signal,QEventLoop
from PySide6.QtWidgets import QMessageBox,QDialog


# class SinkronController(QObject):
#     sinkron_selesai = Signal(bool)

#     def __init__(self, view, user_info, app_controller, silent_mode=False):
#         super().__init__()
#         self.view = view
#         self.user_info = user_info
#         self.app_controller = app_controller
#         self.model = SinkronModel()
#         self.view.set_controller(self)
#         self.silent_mode = silent_mode
#         self.thread = None
#         self.worker = None
#         self.tables = [
#             'per_cabang_device', 'per_cabang', 'per_customers', 'per_employee',
#             'bank', 'produk', 'price', 'price_per_area', 'diskon',
#             'diskon_customer'
#         ]
# class SinkronController:
class SinkronController(QObject):
    sinkron_selesai = Signal(bool)
    # sinkron_selesai = Signal()  # ⬅️ sinyal sinkron selesai

    def __init__(self, view, user_info, app_controller, silent_mode=False):
        super().__init__()  # ✅ wajib
        self.view = view
        self.user_info = user_info
        self.app_controller = app_controller
        self.model = SinkronModel()

        if self.view:  # ✅ Tambahkan pengecekan
            self.view.set_controller(self)

        # self.view.set_controller(self)
        self.silent_mode = silent_mode
        self.thread = None
        self.worker = None

        self.tables = [
            'per_cabang_device', 'per_cabang', 'per_customers', 'per_employee',
            'bank', 'produk', 'price', 'price_per_area', 'diskon',
            'diskon_customer'
        ]
        # self.tables = [
        #     'per_customers'
        # ]
       

    def sinkronkan_setelah_login(self, user_info):
        print('sinkronkan panggil sinkronkan_setelah_login')
        # fitur ini diperlukan untuk : 
        # kondisi saat POS habis offline dan baru bisa online kembali, data harus dipastikan terupdate otomatis
        # kondisi saat POS selalu online, supaya meskipun kasir lupa mensinkronkan data, POS lokal selalu dalam kondisi terupdate (meski sudah ada notif up-to-date atau perlu sinkron di kanan atas dashboard)
        self.thread = QThread()
        self.worker = SinkronWorker(self.tables)
        self.worker.moveToThread(self.thread)

        

        self.thread.started.connect(self.worker.run)
        # self.worker.progress.connect(self.update_progress_gui)
        self.worker.progress.connect(self.handle_progress_update)

        self.worker.selesai.connect(self.sinkronisasi_selesai)
        # self.worker.gagal.connect(self.sinkronisasi_gagal)
        self.worker.gagal.connect(self.handle_sinkron_gagal)
        self.worker.selesai.connect(self.view.emit_sinyal_selesai)

        # Cleanup: otomatis setelah selesai
        self.worker.selesai.connect(self.cleanup_thread)
        self.worker.gagal.connect(self.cleanup_thread)

        self.thread.start()

    def background_sinkron(self, user_info):
        print('sinkronkan panggil sinkronkan_setelah_login')
        # fitur ini diperlukan untuk : 
        # kondisi saat POS habis offline dan baru bisa online kembali, data harus dipastikan terupdate otomatis
        # kondisi saat POS selalu online, supaya meskipun kasir lupa mensinkronkan data, POS lokal selalu dalam kondisi terupdate (meski sudah ada notif up-to-date atau perlu sinkron di kanan atas dashboard)
        self.thread = QThread()
        self.worker = SinkronWorker(self.tables)
        self.worker.moveToThread(self.thread)

        

        self.thread.started.connect(self.worker.run)
        # self.worker.progress.connect(self.update_progress_gui)
        self.worker.progress.connect(self.handle_progress_update)

        self.worker.selesai.connect(self.sinkronisasi_selesai)
        # self.worker.gagal.connect(self.sinkronisasi_gagal)
        self.worker.gagal.connect(self.handle_sinkron_gagal)
        self.worker.selesai.connect(self.view.emit_sinyal_selesai)

        # Cleanup: otomatis setelah selesai
        self.worker.selesai.connect(self.cleanup_thread)
        self.worker.gagal.connect(self.cleanup_thread)

        self.thread.start()

# pakai mulai sinkron dengan api yang tersedia oleh server
    def mulai_sinkron(self):
        print("Mulai sinkron via API...")
        self.thread = QThread()
        self.worker = SinkronWorker(table_list=self.tables)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.handle_progress_update)
        self.worker.selesai.connect(self.emit_sinyal_selesai)
        self.worker.selesai.connect(self.cleanup_thread)
        self.worker.gagal.connect(self.handle_sinkron_gagal)

        self.thread.start()

    # def mulai_sinkron(self):
    #     print('Sinkronisasi (silent_mode =', self.silent_mode, ') dimulai...')

    #     self.thread = QThread()
    #     self.worker = SinkronWorker(table_list=self.tables)
    #     self.worker.moveToThread(self.thread)

    #     self.thread.started.connect(self.worker.run)
    #     self.worker.progress.connect(self.handle_progress_update)
    #     self.worker.selesai.connect(self.emit_sinyal_selesai)
    #     self.worker.selesai.connect(self.thread.quit)
    #     self.worker.selesai.connect(self.worker.deleteLater)
    #     self.thread.finished.connect(self.thread.deleteLater)
    #     self.worker.gagal.connect(self.handle_sinkron_gagal)

    #     self.thread.start()

    
    # def emit_sinyal_selesai(self, total_updated):
    #     print(f"[DEBUG] Sinkron selesai: {total_updated} baris")
    #     # QMessageBox.information(None, "Sinkronisasi Data", "Sinkronisasi data server-lokal selesai")
    #     self.sinkron_selesai.emit(True)
    #     # QMessageBox.information(None, "Sinkronisasi Data", "Sinkronisasi data server-lokal selesai")
    def emit_sinyal_selesai(self, total_updated):
        print(f"[DEBUG] Sinkron selesai: {total_updated} baris")
        self.sinkron_selesai.emit(True)

        if self.silent_mode and hasattr(self.app_controller, 'dashboard_window'):
            self.app_controller.dashboard_window.set_sinkron_status("✅ Sinkron Selesai")

    def handle_sinkron_gagal(self, pesan):
        print(f"[ERROR] Sinkron gagal: {pesan}")
        self.sinkron_selesai.emit(False)
        self.thread.quit()
    
 

    def on_sinkron_selesai(self, total_rows=None):
            # Menutup view sinkron
            if self.view:
                self.view.close()
                self.view.deleteLater()
                self.view = None

            # Menampilkan dashboard lewat app controller
            if self.app_controller:
                self.app_controller.show_dashboard(self.user_info)


    
    def sinkronisasi_selesai(self, total):
        if self.view:
            self.view.update_progress(100, "✅ Sinkronisasi selesai.", f"{total} data diperbarui")
            self.view.emit_sinyal_selesai()

    def sinkronisasi_gagal(self, pesan):
        if self.view:
            self.view.update_progress(0, "❌ Gagal sinkronisasi", pesan)

    def cleanup_thread(self):
        # QMessageBox.information(None, "Sinkronisasi Data", "Sinkronisasi data server-lokal selesai")
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()
        

    from PySide6.QtCore import Slot

    # @Slot(int, str)
    # def handle_progress_update(self, persen, pesan):
    #     if self.view:
    #         self.view.update_progress(persen, pesan)

    @Slot(int, str)
    def handle_progress_update(self, persen, pesan):
        if self.silent_mode:
            print(f"[Silent Sync] {persen}% - {pesan}")
            # Update indikator kecil di Dashboard (misal: label status)
            if hasattr(self.app_controller, 'dashboard_window'):
                self.app_controller.dashboard_window.set_sinkron_status(f"⏳ Sinkron {persen}%...")
        else:
            if self.view:
                self.view.update_progress(persen, pesan)


