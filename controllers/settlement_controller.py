from PySide6.QtCore import QDateTime
from views.settlement_dialog_view import SettlementDialogView
from models.settlement_model import SettlementModel
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTableWidgetItem
class SettlementController:
    def __init__(self, db_path, user_info, parent_window=None):
        self.model = SettlementModel(db_path)
        self.view = SettlementDialogView(self)
        self.user_info = user_info
        self.db_path = db_path

        self.setup_events()

        self.transaksi_data = []
        print('masuk controller settel')
        self.parent_window = parent_window

        # load data awal
        self.load_transaksi()

        # ✅ langsung tampilkan history settlement terakhir
        history = self.model.get_last_settlements()
        self.view.tampilkan_history(history)


# class SettlementController:
#     def __init__(self, db_path, user_info, parent_window=None):
#         self.model = SettlementModel(db_path)
#         self.view = SettlementDialogView(self)
#         self.user_info = user_info
#         self.db_path = db_path
#         self.setup_events()

#         self.transaksi_data = []  # simpan transaksi master untuk referensi id
#         print('masuk controller settel')
#         self.load_transaksi()
    
    def on_settlement_selesai(self):
        print("Settlement selesai — refresh POS atau reset form di sini")

    def show(self):
        self.view.exec()

    def setup_events(self):
        # dinon aktifkan dulu untuk tampilkan detailnya 
        # self.view.table_transaksi.cellClicked.connect(self.tampilkan_detail)
        self.view.uang_input.textChanged.connect(self.aktifkan_admin_section)
        self.view.cancel_button.clicked.connect(self.view.close)
        self.view.settle_button.clicked.connect(self.proses_settlement)
        # self.view.settlement_selesai.connect(self.on_settlement_selesai)


    def load_transaksi(self):
        self.transaksi_data = self.model.get_transaksi_belum_settle()
        print(f'isi transaksi data = {self.transaksi_data}')
        self.tampilkan_rekap()


        print(f'[DEBUG] Jumlah transaksi: {len(self.transaksi_data)}')
        
        table = self.view.table_transaksi
        table.setRowCount(len(self.transaksi_data))
        # table.setColumnCount(5)
        # table.setHorizontalHeaderLabels(["ID", "Tanggal", "Customer", "Total", "Detail"])

        for row, data in enumerate(self.transaksi_data):
            print(f"[DEBUG] Isi data baris {row}: {data}")
            table.setItem(row, 0, QTableWidgetItem(str(data['id'])))
            table.setItem(row, 1, QTableWidgetItem(str(data['tanggal'])))
            table.setItem(row, 2, QTableWidgetItem(str(data['customer'])))
            table.setItem(row, 3, QTableWidgetItem(f"{data['total']:,.0f}"))

    def make_item(self, text):
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def tampilkan_detail(self, row, col):
        transaksi_id = self.transaksi_data[row]['id']
        detail_list = self.model.get_detail_transaksi(transaksi_id)

        detail_text = "\n".join(
            f"{d['nama']} x{d['jumlah']} = {d['total']:,}" for d in detail_list
        )
        self.view.tampilkan_detail_transaksi(detail_text)

    def aktifkan_admin_section(self):
        try:
            nilai = int(self.view.uang_input.text())
            if nilai > 0:
                admin_list = self.model.get_list_admin()
                self.view.tampilkan_admin_section(admin_list)
                self.view.settle_button.setEnabled(True)
        except ValueError:
            self.view.settle_button.setEnabled(False)
            self.view.admin_group.setVisible(False)

    # # review #3 tim 1 tgl 1 oki 2025
    def proses_settlement(self):
        """Menangani proses klik tombol SETTLE"""
        uang_str = self.view.uang_input.text().strip()
        if not uang_str:
            self.view.tampilkan_error("Jumlah uang setor belum diisi.")
            return

        try:
            total_disetor = float(uang_str.replace(",", ""))
        except ValueError:
            self.view.tampilkan_error("Format uang tidak valid.")
            return

        # --- Cegah double settlement hari ini ---
        # if self.model.sudah_disettle_hari_ini(self.user_info["id"]):
        #     self.view.tampilkan_error("Kasir ini sudah melakukan settlement hari ini.")
        #     return

        # --- Ambil transaksi tunai yang belum disettle ---
        transaksi_list = self.model.cek_transaksi_settlement()
        print(f'isi var transaksi_list dari fungsi proses_settlement = {transaksi_list}')
        if not transaksi_list:
            self.view.tampilkan_error("Tidak ada transaksi yang perlu disettle.")
            return

        # --- Simpan settlement ---
    #     kasir_id = self.user.id
    # kasir_nama = self.user.nama
    # cabang_id = self.user.cabang_id
    # cabang_nama = self.user.cabang_nama
        shift = "2 (15:00 - 22:00)"  # bisa dinamis
        counter = self.model.simpan_settlement(
            kasir_id=self.user_info["id"],
            kasir_nama=self.user_info["nama"],
            cabang_id=1 ,#self.user_info["cabang_id"],
            cabang_nama='kasir2', #self.user_info["cabang_nama"],
            transaksi_list=transaksi_list
        )

        if not counter:
            self.view.tampilkan_error("Gagal menyimpan settlement.")
            return

        # --- Hitung total per metode dan cetak laporan ---
        total_dict = self.model.hitung_total_per_metode()
        print(f'isi var total_dict dari fungsi proses_settlement {total_dict}')
        print(f'isi var counter dari fungsi proses_settlement {counter}')
        print(f'isi var self_user_info_nama {self.user_info["nama"]}')
        print(f'isi var shift dari fungsi proses_settlement {shift}')

        # shift = self.user_info.get("shift", "Pagi")
        self.model.print_settlement_report(counter, self.user_info["nama"], shift, total_dict, transaksi_list)

        # --- Ubah status transaksi menjadi sudah disettle ---
        self.model.set_settlement([t["id"] for t in transaksi_list], self.user_info["nama"], total_disetor)

        # --- Matikan tombol SETTLE agar tidak double ---
        self.view.settle_button.setEnabled(False)
        # self.view.tampilkan_pesan(f"Settlement {counter} berhasil disimpan dan dicetak.")

        # ✅ Tampilkan pesan sukses
        self.view.tampilkan_pesan(f"Settlement berhasil disimpan dengan ID: {counter}")

        # ✅ Tutup dialog otomatis setelah pesan sukses
        self.view.close()

        # ✅ Coba akses dashboard window dari parent view
        try:
            print("🔄 Refreshing Transaksi Penjualan View di Dashboard...")

            # parent_window di sini = TransaksiPenjualanView
            
            # transaksi_view = getattr(self, "parent_window", None)
            # if transaksi_view is not None:
            #     dashboard = getattr(transaksi_view, "parent_window", None)
            # else:
            #     dashboard = None

            # if dashboard is None:
            #     print("⚠️ Tidak menemukan DashboardWindow, tidak bisa refresh otomatis.")
            #     return

            print('SELF.PARENT_WINDOW.BUKA_PENJUALAN')
            # self.parent_window.buka_penjualan
            self.parent_window.parent_window.buka_penjualan()


            # # ✅ Import modul yang diperlukan
            # from views.transaksi_penjualan_view import TransaksiPenjualanView
            # from controllers.transaksi_penjualan_controller import TransaksiPenjualanController
            # from controllers.customer_controller import CustomerController
            # import sys, os
            # from utils.path_utils import get_db_path

            # BASE_DIR = os.path.abspath(os.path.join(sys.path[0]))
            # DB_PATH = get_db_path()
            # print("DB Path setelah settlement:", DB_PATH)

            # customer_list = CustomerController().load_all_customers()

            # # ✅ Buat ulang transaksi penjualan controller dan view
            # transaksi_controller = TransaksiPenjualanController(
            #     customer_list,
            #     self.user_info,
            #     DB_PATH
            # )
            # transaksi_view_baru = transaksi_controller.view

            # # ✅ Set widget baru di dashboard.content_area
            # dashboard.content_area.setCurrentWidget(transaksi_view_baru)

            # # ✅ Jalankan cek settlement lagi jika perlu
            # transaksi_controller.cek_status_settlement()

            # # ✅ Fokus ke barang_input setelah sedikit delay agar UI stabil
            # QTimer.singleShot(150, lambda: transaksi_view_baru.barang_input.setFocus())

            print("✅ Refresh POS selesai.")
        except Exception as e:
            print(f"⚠️ Gagal refresh POS otomatis: {e}")

        
    # def proses_settlement(self):
    #     """Menangani proses klik tombol SETTLE"""
    #     uang_str = self.view.uang_input.text().strip()
    #     if not uang_str:
    #         self.view.tampilkan_error("Jumlah uang setor belum diisi.")
    #         return

    #     try:
    #         total_disetor = float(uang_str.replace(",", ""))
    #     except ValueError:
    #         self.view.tampilkan_error("Format uang tidak valid.")
    #         return

    #     transaksi_list = self.model.cek_transaksi_settlement()
    #     if not transaksi_list:
    #         self.view.tampilkan_error("Tidak ada transaksi yang perlu disettle.")
    #         return

    #     shift = "2 (15:00 - 22:00)"
    #     counter = self.model.simpan_settlement(
    #         kasir_id=self.user_info["id"],
    #         kasir_nama=self.user_info["nama"],
    #         shift=shift,
    #         total_disetor=total_disetor
    #     )

    #     # ✅ Tampilkan pesan sukses
    #     self.view.tampilkan_pesan(f"Settlement berhasil disimpan dengan ID: {counter}")

    #     # ✅ Tutup dialog otomatis setelah pesan sukses
    #     self.view.close()

    #     # ✅ (Opsional) Panggil refresh transaksi di halaman utama jika parent window disediakan
    #     if hasattr(self, "parent_window") and self.parent_window:
    #         try:
    #             self.parent_window.controller.model_settle.get_transaksi_belum_settle()
    #             print("✅ Data transaksi utama di-refresh setelah settlement.")
    #         except Exception as e:
    #             print(f"⚠️ Gagal refresh transaksi utama: {e}")


    


    def tampilkan_rekap(self):
        rekap = self.model.get_rekap_settlement()

        tunai_total = rekap["tunai"]
        edc_list = rekap["edc"]

        # text = f"💵 Total Penjualan Tunai: {tunai_total:,.0f}\n"
        # text += f"💵 Total Penjualan Non-Tunai: \n"
        text = f"💵 Total Penjualan Non-Tunai: \n"
        for edc, total in edc_list.items():
            text += f"🏧 {edc}: {total:,.0f}\n"

        self.view.tampilkan_rekap(text)

