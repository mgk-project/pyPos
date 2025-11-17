from controllers.load_transaksi_controller import LoadTransaksiController

from controllers.customer_search_controller import CustomerSearchController
from controllers.pembayaran_controller import PembayaranController
from models.pembayaran_model import InfoTransaksi

from models.transaksi_model import TransaksiModel
from views.transaksi_penjualan_view import TransaksiPenjualanView
from datetime import datetime
from PySide6.QtCore import QTimer,Qt
# untuk cetak struk

import os
import tempfile
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
import platform
import subprocess
import win32print
import win32api
import re
from PySide6.QtWidgets import QMessageBox
from utils.mysql_connector import get_mysql_connection  # asumsi modul kamu namanya begitu
import traceback
# untuk cetak struk
from reportlab.lib.pagesizes import A7
from reportlab.lib.utils import ImageReader
import csv
from datetime import datetime

import requests
from controllers.diskon_controller import DiskonController
# from views.diskon_view import DiskonView
# from models.diskon_model import DiskonModel
# untuk settlement proses
from PySide6.QtWidgets import QDialog
from utils.settlement_checker import SettlementHandler
from models.settlement_model import SettlementModel
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QSpinBox, QHeaderView, QDialog,
    QFormLayout, QDialogButtonBox, QCheckBox, QFrame, QAbstractItemView,
    QCompleter ,QPlainTextEdit,QRadioButton,QGroupBox, QMessageBox
)

# untuk cetak printer langsung ke printer 
# fungsi cetak_struk
# untuk cetak pdf preview
# fungsinya ceta_strukpdf
from escpos.printer import Usb
from datetime import datetime
from PySide6.QtWidgets import QMessageBox
# from controllers.printer_settings_controller import PrinterSettingsController
from controllers.printer_settings_controller import PrinterSettingsController
from PySide6.QtPrintSupport import QPrintPreviewDialog
from PySide6.QtCore import QSizeF
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QTextDocument
# from PySide6.QtCore import QSizeF
from PySide6.QtGui import QPageLayout

import os, csv
from datetime import datetime


# class TransaksiPenjualanController:
#     def __init__(self, customer_list, user_info, db_path):
#         self.customer_list = customer_list
#         self.user_info = user_info
#         self.db_path = db_path

#         # Berikan semua argumen ke view
#         self.view = TransaksiPenjualanView(self, user_info, db_path)

class TransaksiPenjualanController:
    def __init__(self, customer_list, user_info, db_path, parent_window=None):
    # self.model = ...
    # self.view = TransaksiPenjualanView(self, user_info, db_path, parent_window=parent_window)

    # def __init__(self, customer_list, user_info, db_path):
        self.model = TransaksiModel(db_path)
        # self.view = TransaksiPenjualanView(self)
        self.db_path = db_path
        # self.view = TransaksiPenjualanView(self, user_info, db_path)
        self.view = TransaksiPenjualanView(self, user_info, db_path, parent_window=parent_window)

        # untuk proses settlement f2
        self.model_settle = SettlementModel(db_path)
        # untuk printer nya 
        self.printer_settings_controller = PrinterSettingsController()
        # self.controller_setting_printer = PrinterSettingsController

        
        # # Dalam init atau fungsi tertentu
        # self.transaksi_modal = QDialog(self.view)
        # self.settlement_handler = SettlementHandler(self.view, self.transaksi_modal)

        # # Saat ingin cek settlement
        # self.settlement_handler.cek_status_settlement()

        # Misal base_url = "http://127.0.0.1:5000" atau sesuai URL Flask kamu
        # diskon_model = DiskonModel(base_url="http://127.0.0.1:5000")
        # diskon_view = DiskonView()
        self.diskon_controller = DiskonController() #diskon_model, diskon_view)

        # self.view = TransaksiPenjualanView(self, user_info)

        self.customer_list = customer_list
        self.user_info = user_info
        self.barang_mapping = {}
        self.data_barang_cache = {}  # ✅ Tambahkan ini

        self.view.populate_customer_combo(customer_list)
        barang_list, mapping = self.model.get_produk_autocomplete()
        self.barang_mapping = mapping
        self.view.set_barang_autocomplete(barang_list)
        # ✅ Fokus ke input barang setelah UI tampil
        QTimer.singleShot(100, self.view.barang_input.setFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F3:
            self.buka_customer_dialog()
        elif event.key() == Qt.Key_F7:
            self.buka_dialog_pembayaran()
        elif event.key() == Qt.Key_F2:
            self.buka_modal_settlement()


        else:
            super().keyPressEvent(event)

    def cek_status_settlement(self):
        data = self.model_settle.cek_transaksi_settlement()
        self.settlement_result(data)

    def settlement_result(self, data):
        print(f'masuk settlement result , jumlah data = {len(data)}')
        if len(data) > 0:
            # self.transaksi_modal.exec()
            # self.view.buka_modal_settlement()
            self.nonaktifkan_form()
            QMessageBox.warning(
                self.view,
                "Perhatian",
                "Ada transaksi penjualan yang belum diselesaikan. Silakan selesaikan terlebih dahulu."
            )
            self.view.buka_modal_settlement()
        else:
            self.aktifkan_form()

    def nonaktifkan_form(self):
        widget_types = [QLineEdit, QComboBox, QPushButton]
        for widget_type in widget_types:
            for widget in self.view.findChildren(widget_type):
                widget.setEnabled(False)

    def aktifkan_form(self):
        widget_types = [QLineEdit, QComboBox, QPushButton]
        for widget_type in widget_types:
            for widget in self.view.findChildren(widget_type):
                widget.setEnabled(True)

    def buka_customer_dialog(self):
        dialog = CustomerSearchController()
        selected_id = dialog.show()
        if selected_id:
            print(f"Customer dipilih: {selected_id}")
            self.view.set_customer_by_id(selected_id)  # opsional kalau kamu punya fungsi itu

    # import re

    def buka_dialog_pembayaran(self):
        # # Ambil teks dari label
        # total_text = self.view.total_label.text().replace(",00", "").replace(".", "")  # contoh: "Total: 150.000"
        # print(f'total text = {total_text}')
        # # Bersihkan: hilangkan semua selain angka
        # total_text_clean = re.sub(r"[^\d]", "", total_text)  # hasil: '150000'
        # total_belanja = int(total_text_clean) if total_text_clean else 0
        # print(f'total text clean = {total_text_clean}')
        # # Ambil info item
        # jenis_item = self.view.table_barang.rowCount()
        # total_qty = sum(int(self.view.table_barang.item(r, 4).text()) for r in range(jenis_item))
        # # #kode voucher
        # # self.voucher_input = QLineEdit()
        # # form_layout.addRow("Kode Voucher Retur:", self.voucher_input)

        # Ambil teks total dari label, misal: "Total: Rp 439.000,00"
        raw_text = self.view.total_label.text()
        print(f"raw total text = {raw_text}")

        # Ambil hanya bagian angka menggunakan regex (mengambil digit, titik, koma)
        import re
        match = re.search(r"([\d\.\,]+)", raw_text)
        if match:
            angka_str = match.group(1)
        else:
            angka_str = "0"

        # Hapus spasi
        angka_str = angka_str.strip()

        # Jika format Indonesia, ubah jadi format numerik internasional
        # (titik = pemisah ribuan → dihapus, koma = desimal → ganti jadi titik)
        angka_str = angka_str.replace(".", "").replace(",", ".")

        # Konversi aman ke float
        try:
            total_belanja = float(angka_str)
        except ValueError:
            total_belanja = 0.0

        print(f"angka_str setelah parsing = {angka_str}")
        print(f"total pembayaran ke pembayaran controller = {total_belanja}")
        # Ambil info item
        jenis_item = self.view.table_barang.rowCount()
        total_qty = sum(int(self.view.table_barang.item(r, 4).text()) for r in range(jenis_item))
        # #kode voucher
        # self.voucher_input = QLineEdit()
        # form_layout.addRow("Kode Voucher Retur:", self.voucher_input)

        # Kirim ke dialog
        info = InfoTransaksi(
            tanggal=datetime.now().strftime("%Y-%m-%d"),
            jenis_item=jenis_item,
            total_qty=total_qty,
            total_belanja=total_belanja
        )

        # dialog = PembayaranController(self.view, info)
        # if dialog.show():
        #     hasil = dialog.get_payment_result()
        #     if hasil:
        #         print("✅ Pembayaran berhasil:", hasil)
        # print(f'total pembayaran ke pembayaran controller = {total_belanja}')
        dialog = PembayaranController(self.view, info)
        if dialog.show():
            hasil = dialog.result
            if hasil and hasil.metode == "tunai":
                self.simpan_transaksi_f7(hasil)  # 🚀 panggil fungsi simpan transaksi
            elif hasil and hasil.metode == "kredit":
                print('masuk ke pembayaran credit')
                self.simpan_transaksi_f7(hasil)  # 🚀 panggil fungsi simpan transaksi
            elif hasil and hasil.metode == "debit":
                print('masuk ke pembayaran debit')
                self.simpan_transaksi_f7(hasil)  # 🚀 panggil fungsi simpan transaksi
            else:
                print("Pembayaran dibatalkan atau metode lain")


    def buka_penyimpanan_dialog(self):
        # Tampilkan konfirmasi
        reply = QMessageBox.question(
            self.view,
            "Simpan Transaksi?",
            "Apakah Anda ingin menyimpan kondisi transaksi sekarang?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            transaksi_data, detail_data,transaksi_data_dict = self.view.kumpulkan_data_transaksi()
            # transaksi_data, detail_data = self.view.kumpulkan_data_transaksi()
            transaksi_data = list(transaksi_data)  # ubah ke list agar bisa dimodifikasi
            # detail_data = list(detail_data)  # ubah ke list agar bisa dimodifikasi

            if not transaksi_data:
                return

            # Ubah label ke 'simpan_transaksi'
            if len(transaksi_data) > 11:
                transaksi_data[11] = 'simpan_transaksi'  # jenis_label
            else:
                while len(transaksi_data) < 14:
                    transaksi_data.append(None)
                transaksi_data[11] = 'simpan_transaksi'

            # Ubah produk_jenis dari semua detail ke 'simpan_transaksi'
            # detail_data_fix = []
            # for d in detail_data:
            #     d = list(d)
            #     d[4] = 'simpan_transaksi'  # kolom produk_jenis
            #     detail_data_fix.append(tuple(d))
            # Ubah produk_jenis jadi 'simpan_transaksi'
            for item in detail_data:
                item.produk_jenis = 'simpan_transaksi'

            try:
                # transaksi_id = self.model.simpan_transaksi_f9(transaksi_data, detail_data_fix)
                transaksi_id = self.model.simpan_transaksi_f9(transaksi_data, detail_data)
                self.view.reset_form()
                QMessageBox.information(self.view, "Berhasil", f"Transaksi disimpan dengan ID: {transaksi_id}")
            except Exception as e:
                QMessageBox.critical(self.view, "Gagal", f"Gagal menyimpan transaksi:\n{e}")
    def load_transaksi_tersimpan(self):
        dialog = LoadTransaksiController(self.view, self, self.model.db_path)
        dialog.show()

 
    def load_transaksi_ke_view(self, detail_rows, cust_id, cust_nama, diskon, ppn, total_harga):
        self.view.reset_form()
        # Load detail ke tabel
        for item in detail_rows:
            produk_id, nama, harga, jumlah, diskon_persen,satuan = item
            self.view.tambah_barang_ke_tabel({
                "id": produk_id,
                "nama": nama,
                "harga": harga,
                "jumlah": jumlah,
                "diskon_persen": diskon_persen,
                "satuan": satuan
            })

        # Set customer_combo
        index = self.view.customer_combo.findText(cust_nama)
        if index != -1:
            self.view.customer_combo.setCurrentIndex(index)

        # Set nilai diskon transaksi
        self.view.diskon_input.setValue(int(diskon))  # pastikan int jika diskon persen
        self.view.ppn.setText(f"{ppn:,.0f}")
        self.view.total_bayar.setText(f"{total_harga:,.0f}")
        self.view.update_ringkasan()

    # cetak nya di preview dulu baru di kirim ke printer
    def generate_struk_preview(self, transaksi_data, detail_data, transaksi_data_dict):
        lines = []
        lines.append("===== STRUK PREVIEW =====")
        lines.append(f"INVOICE: {transaksi_data_dict['nomer']}")
        lines.append(f"Tanggal: {transaksi_data_dict['dtime']}")
        lines.append(f"Kasir  : {transaksi_data_dict['oleh_nama']}")
        lines.append(f"Customer: {transaksi_data_dict.get('customers_nama','')}")
        lines.append("-"*32)

        for item in detail_data:
            nama = item.produk_nama
            harga_satuan = item.produk_ord_hrg
            jumlah = item.produk_ord_jml
            diskon = item.produk_ord_diskon
            harga_diskon = harga_satuan * (1 - diskon/100)
            subtotal = harga_diskon * jumlah
            lines.append(f"{nama}")
            lines.append(f"  {jumlah} x {harga_diskon:,.0f} = {subtotal:,.0f}")

        lines.append("-"*32)
        lines.append(f"Total Harga : {transaksi_data_dict['transaksi_bulat']:,.0f}")
        lines.append(f"Diskon      : {transaksi_data_dict['diskon_persen']}%")
        lines.append(f"Total Bayar : {transaksi_data_dict['transaksi_nilai']:,.0f}")
        lines.append("==========================")
        return "\n".join(lines)
    # from PySide6.QtWidgets import QMessageBox

    def cetak_struk(self, transaksi_data, detail_data, transaksi_data_dict):
        # Buat preview teks
        preview_text = self.generate_struk_preview(transaksi_data, detail_data, transaksi_data_dict)

        # Tampilkan preview ke user
        msg = QMessageBox()
        msg.setWindowTitle("Preview Struk")
        msg.setText(preview_text)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = msg.exec()

        # Jika user pilih OK → coba cetak (kalau printer sudah ada)
        if ret == QMessageBox.Ok:
            try:
                from escpos.printer import Usb
                VENDOR_ID = 0x0416
                PRODUCT_ID = 0x5011
                p = Usb(VENDOR_ID, PRODUCT_ID)

                # contoh kirim teks saja
                p.text(preview_text + "\n")
                p.cut()
            except Exception as e:
                QMessageBox.warning(None, "Gagal Cetak", f"Printer tidak tersedia.\nError: {e}")




    # from escpos.printer import Usb
    # from datetime import datetime

    # def cetak_struk(self, transaksi_data, detail_data, transaksi_data_dict):
    #     """Cetak struk langsung ke thermal printer (ESC/POS)"""
    #     # ✅ ganti dengan vendor & product ID sesuai printer thermalmu
    #     VENDOR_ID = 0x0416
    #     PRODUCT_ID = 0x5011
    #     p = Usb(VENDOR_ID, PRODUCT_ID)

    #     # --- Header toko ---
    #     p.set(align="center", bold=True, width=2, height=2)
    #     p.text("INVOICE\n")
    #     p.set(align="center", bold=False)
    #     p.text(f"{transaksi_data_dict.get('nomer','')}\n")

    #     waktu = datetime.strptime(transaksi_data_dict["dtime"], "%Y-%m-%d %H:%M:%S")
    #     waktu_str = waktu.strftime("%d/%m/%Y %H:%M")
    #     p.text(f"{waktu_str} | {transaksi_data_dict['oleh_nama']}\n")
    #     p.text(f"Customer: {transaksi_data_dict.get('customers_nama','')}\n")
    #     p.text("-" * 32 + "\n")

    #     # --- Item detail ---
    #     for item in detail_data:
    #         nama = item.produk_nama
    #         harga_satuan = item.produk_ord_hrg
    #         jumlah = item.produk_ord_jml
    #         diskon = item.produk_ord_diskon
    #         harga_diskon = harga_satuan * (1 - diskon / 100)
    #         subtotal = harga_diskon * jumlah

    #         p.text(f"{nama}\n")
    #         p.text(f"  {jumlah} x {harga_diskon:,.0f} = {subtotal:,.0f}\n")

    #     p.text("-" * 32 + "\n")

    #     # --- Ringkasan ---
    #     p.text(f"Total Harga : {transaksi_data_dict['transaksi_bulat']:,.0f}\n")
    #     p.text(f"Diskon      : {transaksi_data_dict['diskon_persen']}%\n")
    #     p.text(f"PPN         : {transaksi_data[4]:,.0f}\n")
    #     p.text(f"Total Bayar : {transaksi_data_dict['transaksi_nilai']:,.0f}\n")

    #     metode = int(transaksi_data_dict['settlement_id'])
    #     if metode > 1:  # Kredit/Debit
    #         no_kartu = transaksi_data_dict.get("bank_rekening_nama", "")
    #         approve_code = transaksi_data_dict.get("rekening", "")
    #         nominal = transaksi_data_dict["transaksi_nilai"]
    #         if no_kartu and len(no_kartu) > 4:
    #             no_kartu = "**** **** **** " + no_kartu[-4:]

    #         if metode == 2:
    #             p.text("Metode: KREDIT\n")
    #         else:
    #             p.text("Metode: DEBIT\n")

    #         p.text(f"No Kartu: {no_kartu}\n")
    #         p.text(f"Approval: {approve_code}\n")
    #         p.text(f"Nominal : {nominal:,.0f}\n")
    #     else:  # Tunai
    #         p.text(f"Dibayar : {transaksi_data_dict['transaksi_nilai']:,.0f}\n")
    #         p.text(f"Kembali : {transaksi_data_dict.get('returned',0):,.0f}\n")

    #     p.text("-" * 32 + "\n")

    #     # --- Footer ---
    #     p.set(align="center")
    #     p.text("Terima kasih\n")
    #     p.text("Barang yang sudah dibeli\n")
    #     p.text("tidak dapat dikembalikan\n")

    #     # --- Cut kertas ---
    #     p.cut()
    # from PySide6.QtPrintSupport import QPrintPreviewDialog
    # from PySide6.QtCore import QSizeF

    def preview_struk(self, transaksi_data, detail_data, transaksi_data_dict, index_printer: int = 0, parent=None):
        """Preview struk dengan data nyata (QPrintPreviewDialog)."""
        if not transaksi_data:
            return False

        # ---------- Load setting struk (CSV) ----------
        def load_setting_struk(path_csv):
            import csv , os
            with open(path_csv, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    return row
            return {}

        import os
        setting_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'setting_struk.csv')
        setting = load_setting_struk(setting_path)

        # ---------- Siapkan printer PREVIEW ----------
        printers = self.printer_settings_controller.model.load_printers()
        if not (0 <= index_printer < len(printers)):
            print("⚠️ Tidak ada printer terpilih.")
            return False

        cfg = printers[index_printer]
        paper_label = cfg.get("paper_size", "")
        label = (paper_label or "").lower().strip()
        if label in ("56", "56mm"):
            w_mm = 56.0
        elif label in ("80", "80mm"):
            w_mm = 80.0
        elif label in ("100x150", "100x150mm"):
            w_mm = 100.0
        else:
            w_mm = 58.0

        preview_printer = self.printer_settings_controller._make_preview_printer(w_mm)

        # ---------- Siapkan data item ----------
        items = []
        print(f'isi var detail_data = {detail_data}')

        for d in detail_data:
            try:
                qty = int(d.produk_ord_jml or 0)
                price = int(float(d.produk_ord_hrg or 0))
                disc = int(float(d.produk_ord_diskon or 0))
            except Exception as e:
                print(f"⚠️ Error parsing item {d.produk_nama}: {e}")
                qty, price, disc = 0, 0, 0

            is_free = (d.produk_jenis == 'free_produk')

            items.append({
                "name": d.produk_nama,
                "qty": qty,
                "price": price, #0 if is_free else price,
                "disc": 0 if is_free else disc,
                "free": is_free
            })

        # items = []
        # print(f'isi var detail_data = {detail_data}')
        # for d in detail_data:
        #     if d.produk_jenis=='free_produk':
        #         items.append({
        #         "name": d.produk_nama,
        #         "qty": int(d.produk_ord_jml),
        #         "price": int(d.produk_ord_hrg),
        #         "disc": int(d.produk_ord_diskon or 0),
        #         "free": True
        #     })


        #     else:
        #         items.append({
        #             "name": d.produk_nama,
        #             "qty": int(d.produk_ord_jml),
        #             "price": int(d.produk_ord_hrg),
        #             "disc": int(d.produk_ord_diskon or 0),
        #             "free": False
        #         })

        # ---------- Ringkasan pembayaran ----------
        metode = int(transaksi_data_dict.get("settlement_id", 1))
        if metode > 1:
            payment = {
                "method": "Kredit" if metode == 2 else "Debit",
                "card_brand": transaksi_data_dict.get("bank_nama", ""),
                "last4": (transaksi_data_dict.get("bank_rekening_nama", "")[-4:]
                        if transaksi_data_dict.get("bank_rekening_nama") else "XXXX"),
                "approval_code": transaksi_data_dict.get("rekening", "-"),
            }
        else:
            payment = {"method": "Tunai"}

        wifi_code = setting.get("wifi_code", "-")
        qr_data = "https://toko.local/struk/" + transaksi_data_dict["nomer"]

        # ---------- Hitung kolom ----------
        cols = self.printer_settings_controller._estimate_cols(preview_printer, css_font_pt=10.0,
                                            family="DejaVu Sans Mono",
                                            paper_label=paper_label)

        # ---------- Buat dokumen ----------
        # doc = self.printer_settings_controller._create_doc(items, payment, wifi_code, qr_data, cols)
        doc = self.printer_settings_controller._create_doc(items, payment, wifi_code, qr_data, cols, setting, transaksi_data_dict)

        # pastikan width sesuai lebar kertas
        w_pt = self.printer_settings_controller._mm_to_points(w_mm)
        doc.setTextWidth(w_pt)
        doc.setPageSize(QSizeF(w_pt, 1_000_000.0))

        # ---------- Tampilkan preview ----------
        preview = QPrintPreviewDialog(preview_printer, parent)
        preview.setWindowTitle("Preview Struk")
        try:
            preview.setZoomMode(QPrintPreviewDialog.FitToWidth)
        except Exception:
            pass
        preview.paintRequested.connect(lambda p: self.printer_settings_controller._render_doc_to_printer(p, doc))
        preview.exec()
        return True
    # # review tim 1 nomor 1 tgl 1 oki 2025 :
    # def print_struk(self, transaksi_data, detail_data, transaksi_data_dict, index_printer: int = 0, copy_no: int = 0):
    #     """Langsung cetak struk dengan data nyata (tanpa preview)."""
    #     print(f'MASUK PRINT STRUK DI CONTROLLER TRANSAKSI PENJUALAN, DENGAN NILAI COPY_NO = {copy_no}')
    #     if not transaksi_data:
    #         return False

    #     # ---------- Load setting struk (CSV) ----------
    #     def load_setting_struk(path_csv):
    #         import csv, os
    #         setting = {}
    #         with open(path_csv, newline='', encoding='utf-8') as f:
    #             reader = csv.DictReader(f)
    #             for row in reader:
    #                 setting = row
    #                 break  # ambil baris pertama saja

    #         # cek baris tambahan manual
    #         with open(path_csv, encoding='utf-8') as f:
    #             for line in f:
    #                 if line.strip().startswith("print_mode"):
    #                     key, val = line.strip().split(",", 1)
    #                     setting[key] = val
    #                     break
    #         return setting

    #     # def load_setting_struk(path_csv):
    #     #     import csv, os
    #     #     with open(path_csv, newline='', encoding='utf-8') as f:
    #     #         reader = csv.DictReader(f)
    #     #         for row in reader:
    #     #             return row
    #     #     return {}

    #     import os
    #     setting_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'setting_struk.csv')
    #     setting = load_setting_struk(setting_path)

    #     # ---------- Ambil printer ----------
    #     printers = self.printer_settings_controller.model.load_printers()
    #     if not (0 <= index_printer < len(printers)):
    #         print("⚠️ Tidak ada printer terpilih.")
    #         return False

    #     cfg = printers[index_printer]
    #     printer_name = cfg.get("name", "")
    #     paper_label = cfg.get("paper_size", "")
    #     label = (paper_label or "").lower().strip()

    #     if label in ("56", "56mm"):
    #         w_mm = 56.0
    #     elif label in ("80", "80mm"):
    #         w_mm = 80.0
    #     elif label in ("100x150", "100x150mm"):
    #         w_mm = 100.0
    #     else:
    #         w_mm = 58.0

    #     # ---------- Siapkan QPrinter ----------
    #     from PySide6.QtPrintSupport import QPrinter
    #     printer = QPrinter(QPrinter.HighResolution)
    #     printer.setPrinterName(printer_name)
    #     printer.setResolution(203)
    #     try:
    #         printer.setOutputFormat(QPrinter.NativeFormat)
    #     except Exception:
    #         pass
    #     self.printer_settings_controller._apply_paper_size(printer, paper_label)

    #     # ---------- Siapkan data item ----------
    #     items = []
    #     print(f'isi var detail_data = {detail_data}')

    #     for d in detail_data:
    #         try:
    #             qty = int(d.produk_ord_jml or 0)
    #             price = int(float(d.produk_ord_hrg or 0))
    #             disc = int(float(d.produk_ord_diskon or 0))
    #         except Exception as e:
    #             print(f"⚠️ Error parsing item {d.produk_nama}: {e}")
    #             qty, price, disc = 0, 0, 0

    #         is_free = (d.produk_jenis == 'free_produk')

    #         items.append({
    #             "name": d.produk_nama,
    #             "qty": qty,
    #             "price": price,
    #             "disc": 0 if is_free else disc,
    #             "free": is_free
    #         })

    #     # ---------- Ringkasan pembayaran ----------
    #     metode = int(transaksi_data_dict.get("settlement_id", 1))
    #     if metode > 1:
    #         payment = {
    #             "method": "Kredit" if metode == 2 else "Debit",
    #             "card_brand": transaksi_data_dict.get("bank_nama", ""),
    #             "last4": (transaksi_data_dict.get("bank_rekening_nama", "")[-4:]
    #                     if transaksi_data_dict.get("bank_rekening_nama") else "XXXX"),
    #             "approval_code": transaksi_data_dict.get("rekening", "-"),
    #         }
    #     else:
    #         payment = {"method": "Tunai"}

    #     wifi_code = setting.get("wifi_code", "-")
    #     qr_data = "https://toko.local/struk/" + transaksi_data_dict["nomer"]

    #     # ---------- Hitung kolom ----------
    #     cols = self.printer_settings_controller._estimate_cols(
    #         printer, css_font_pt=10.0,
    #         family="DejaVu Sans Mono",
    #         paper_label=paper_label
    #     )

    #     # ---------- Buat dokumen ----------
    #     doc = self.printer_settings_controller._create_doc(
    #         items, payment, wifi_code, qr_data, cols, setting, transaksi_data_dict
    #     )

    #     # Tambahkan watermark copy jika reprint
    #     if copy_no > 0:
    #         html = doc.toHtml()
    #         html = html.replace("<body>", f"<body><div class='hdr'>*** COPY KE-{copy_no} ***</div>")
    #         doc.setHtml(html)

    #     # pastikan width sesuai lebar kertas
    #     w_pt = self.printer_settings_controller._mm_to_points(w_mm)
    #     doc.setTextWidth(w_pt)
    #     doc.setPageSize(QSizeF(w_pt, 1_000_000.0))

    #     # ---------- Kirim ke printer ----------
    #     try:
    #         return self.printer_settings_controller._render_doc_to_printer(printer, doc)
    #     except Exception as e:
    #         print(f"[PrintStruk] Error cetak: {e}")
    #         return False
    # review tim 1 per 24 oktober 2025 
    # terkait print yang tidak rapi 
    # from PySide6.QtPrintSupport import QPrinter
    # from PySide6.QtGui import QTextDocument
    # from PySide6.QtCore import QSizeF

    def print_struk(self, transaksi_data, detail_data, transaksi_data_dict, index_printer: int = 0, copy_no: int = 0):
        """Cetak struk langsung ke printer dengan engine HTML yang sama seperti preview."""
        printers = self.printer_settings_controller.model.load_printers()
        if not (0 <= index_printer < len(printers)):
            print("⚠️ Tidak ada printer terpilih.")
            return False

        cfg = printers[index_printer]
        printer_name = cfg.get("name", "")
        paper_label = cfg.get("paper_size", "58mm")

        # Siapkan printer
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPrinterName(printer_name)
        printer.setResolution(203)
        printer.setOutputFormat(QPrinter.NativeFormat)
        self.printer_settings_controller._apply_paper_size(printer, paper_label)

        # Gunakan layout HTML yang sama dari preview
        items, payment, wifi_code, qr_data, setting = self._prepare_print_data(transaksi_data, detail_data, transaksi_data_dict)

        cols = self.printer_settings_controller._estimate_cols(
            printer, css_font_pt=10.0,
            family="DejaVu Sans Mono",
            paper_label=paper_label
        )
        doc = self.printer_settings_controller._create_doc(items, payment, wifi_code, qr_data, cols, setting, transaksi_data_dict)

        # ⚙️ KUNCI: atur ukuran halaman & text width sama seperti preview
        w_mm = 58 if "58" in paper_label else 80
        w_pt = self.printer_settings_controller._mm_to_points(w_mm)
        doc.setPageSize(QSizeF(w_pt, 1000000))
        doc.setTextWidth(w_pt)

        # Render langsung ke printer — SAMA SEPERTI PREVIEW
        from PySide6.QtGui import QPainter
        painter = QPainter()
        if not painter.begin(printer):
            print("❌ Tidak bisa memulai printer.")
            return False

        # Gunakan QTextDocument.drawContents() (identik dengan preview)
        doc.drawContents(painter)
        painter.end()
        print("✅ Struk berhasil dicetak dengan layout HTML identik preview.")
        return True

    def _prepare_print_data(self, transaksi_data, detail_data, transaksi_data_dict):
        """Helper untuk menyiapkan data item, payment, dan setting untuk dicetak."""
        import os, csv

        # --- 1️⃣ Kumpulkan data produk (detail_data) ---
        items = []
        for d in detail_data:
            try:
                qty = int(d.produk_ord_jml or 0)
                price = int(float(d.produk_ord_hrg or 0))
                disc = int(float(d.produk_ord_diskon or 0))
                free = (d.produk_jenis == "free_produk")
            except Exception as e:
                print(f"⚠️ Gagal parsing data item {getattr(d, 'produk_nama', '-')}: {e}")
                qty, price, disc, free = 0, 0, 0, False

            items.append({
                "name": getattr(d, "produk_nama", "-"),
                "qty": qty,
                "price": price,
                "disc": 0 if free else disc,
                "free": free,
            })
#
        # --- 2️⃣ Informasi pembayaran ---
        metode = int(transaksi_data_dict.get("settlement_id", 1))
        if metode > 1:
            payment = {
                "method": "Kredit" if metode == 2 else "Debit",
                "card_brand": transaksi_data_dict.get("bank_nama", ""),
                "last4": (transaksi_data_dict.get("bank_rekening_nama", "")[-4:]
                        if transaksi_data_dict.get("bank_rekening_nama") else "XXXX"),
                "approval_code": transaksi_data_dict.get("rekening", "-"),
            }
        else:
            payment = {"method": "Tunai"}

        # --- 3️⃣ Baca setting_struk.csv ---
        setting_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'setting_struk.csv')
        setting = {}
        try:
            with open(setting_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    setting = row
                    break
        except Exception as e:
            print(f"⚠️ Gagal membaca setting_struk.csv: {e}")

        # --- 4️⃣ QR code & Wi-Fi ---
        wifi_code = setting.get("wifi_code", "-")
        qr_data = "https://toko.local/struk/" + transaksi_data_dict.get("nomer", "")

        # --- 5️⃣ Return semua data terstruktur ---
        return items, payment, wifi_code, qr_data, setting


    def cetak_struk(self, transaksi_data, detail_data, transaksi_data_dict, index_printer: int = 0):
        """Cetak struk real, pakai format & layout dari printer_settings_controller."""
        if not transaksi_data:
            return False

        # ---------- Load setting struk (CSV) ----------
        # def load_setting_struk(path_csv):
        #     with open(path_csv, newline='', encoding='utf-8') as f:
        #         reader = csv.DictReader(f)
        #         for row in reader:
        #             return row
        #     return {}
# ---------- Load setting struk (CSV) ----------
        def load_setting_struk(path_csv):
            import csv , os
            with open(path_csv, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    return row
            return {}
        setting_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'setting_struk.csv')
        setting = load_setting_struk(setting_path)

        # ---------- Siapkan printer ----------
        printers = self.printer_settings_controller.model.load_printers()
        if not (0 <= index_printer < len(printers)):
            print("⚠️ Tidak ada printer terpilih.")
            return False

        cfg = printers[index_printer]
        printer_name = cfg.get("name", "")
        paper_label = cfg.get("paper_size", "")

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPrinterName(printer_name)
        printer.setResolution(203)
        try:
            printer.setOutputFormat(QPrinter.NativeFormat)
        except Exception:
            pass
        self.printer_settings_controller._apply_paper_size(printer, paper_label)

        # ---------- Siapkan data item ----------
        items = []
        for d in detail_data:
            items.append({
                "name": d.produk_nama,
                "qty": int(d.produk_ord_jml),
                "price": int(d.produk_ord_hrg),
                "disc": int(d.produk_ord_diskon or 0),
                "free": False
            })

        # ---------- Ringkasan pembayaran ----------
        metode = int(transaksi_data_dict.get("settlement_id", 1))
        if metode > 1:
            payment = {
                "method": "Kredit" if metode == 2 else "Debit",
                "card_brand": transaksi_data_dict.get("bank_nama", ""),
                "last4": (transaksi_data_dict.get("bank_rekening_nama", "")[-4:]
                        if transaksi_data_dict.get("bank_rekening_nama") else "XXXX"),
                "approval_code": transaksi_data_dict.get("rekening", "-"),
            }
        else:
            payment = {"method": "Tunai"}

        # ---------- Header / Footer tambahan ----------
        wifi_code = setting.get("wifi_code", "-")
        qr_data = "https://toko.local/struk/" + transaksi_data_dict["nomer"]

        # ---------- Hitung kolom ----------
        cols = self.printer_settings_controller._estimate_cols(printer, css_font_pt=10.0,
                                            family="DejaVu Sans Mono", 
                                            paper_label=paper_label)

        # ---------- Buat dokumen ----------
        # doc = self.printer_settings_controller._create_doc(items, payment, wifi_code, qr_data, cols)
        doc = self.printer_settings_controller._create_doc(items, payment, wifi_code, qr_data, cols, setting, transaksi_data_dict)

        # (opsional) pastikan width sesuai mm
        w_pt = self.printer_settings_controller._mm_to_points(58.0 if not paper_label else float(paper_label.strip("mmx")))
        doc.setTextWidth(w_pt)
        doc.setPageSize(QSizeF(w_pt, 1_000_000.0))

        # ---------- Render ke printer ----------
        return self.printer_settings_controller._render_doc_to_printer(printer, doc)


    def cetak_struk_pdf(self,transaksi_data, detail_data, transaksi_data_dict):
        def load_setting_struk(path_csv):
            with open(path_csv, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    return row
            return {}

        print('masuk cetak struk')
        # transaksi_data, detail_data, transaksi_data_dict = self.view.kumpulkan_data_transaksi()
        if not transaksi_data:
            return

        # Load setting struk
        setting_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'setting_struk.csv')
        setting = load_setting_struk(setting_path)

        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"struk_{transaksi_data[0]}.pdf")

        c = canvas.Canvas(pdf_path, pagesize=A7)
        c.setFont("Helvetica", 6)
        width, height = A7
        y = height - 10
        center = width / 2

        
        from reportlab.lib.utils import ImageReader

        logo_path = setting.get("logo", "") # os.path.join(os.path.dirname(__file__), '..', 'resources', 'logo', setting.get("logo", ""))
        print(f'path logo = {logo_path}, isi seting log = {setting.get("logo", "")}')
        # if os.path.exists(logo_path):
        try:
            logo_img = ImageReader(logo_path)
            c.drawImage(logo_img, 5, y - 30 , width=25, height=25, preserveAspectRatio=True, mask='auto')
            # y -= 35  # naikkan y setelah logo ditampilkan
        except Exception as e:
            print("‼️ Gagal menampilkan logo:", e)
        # else:
            # print("⚠️ Logo tidak ditemukan di:", logo_path)

        # Header toko
        for key in ("header1", "header2", "header3"):
            if setting.get(key):
                c.drawCentredString(center, y, setting[key])
                y -= 8

        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(center, y, "INVOICE")
        y -= 10
        c.drawCentredString(center, y, transaksi_data_dict["nomer"])
        y -= 10

        waktu = datetime.strptime(transaksi_data_dict["dtime"], "%Y-%m-%d %H:%M:%S")
        waktu_str = waktu.strftime("%d/%m/%Y %H:%M")
        c.setFont("Helvetica", 6)
        c.drawCentredString(center, y, f"{waktu_str} | {transaksi_data_dict['oleh_nama']}")
        y -= 8
        c.drawCentredString(center, y, transaksi_data_dict.get("customers_nama", ""))
        y -= 8

        # Divider
        c.drawCentredString(center, y, "-" * 40)
        y -= 8
        c.drawString(5, y, "ITEM / KODE QTY  H.SATUAN     TOTAL")
        y -= 6
        # c.drawString(5, y, " QTY  H.SATUAN     TOTAL")
        # y -= 6
        c.drawCentredString(center, y, "-" * 40)
        y -= 8

        # Item barang
        for item in detail_data:
            nama = item.produk_nama
            harga_satuan = item.produk_ord_hrg
            jumlah = item.produk_ord_jml
            diskon = item.produk_ord_diskon
            print(f'harga satuan = {item.produk_ord_hrg}')
            harga_diskon = harga_satuan * (1 - diskon / 100)
            subtotal = harga_diskon * jumlah

            line = f"{nama}   {jumlah} x {harga_diskon:,.0f}   = {subtotal:,.0f}"
            c.drawString(5, y, line)
            # c.drawString(5, y, nama)
            # y -= 6
            # line = f"{jumlah} x {harga_diskon:,.0f}   = {subtotal:,.0f}"
            # c.drawString(10, y, line)
            y -= 8

            if y < 40:
                c.showPage()
                y = height - 20

        c.drawCentredString(center, y, "-" * 40)
        y -= 8

        # Ringkasan pembayaran
        # c.drawString(5, y, f"Total Harga : {transaksi_data[5]:,.0f}")
        # y -= 6
        # c.drawString(5, y, f"Diskon      : {transaksi_data[3]}%")
        # y -= 6
        # c.drawString(5, y, f"PPN         : {transaksi_data[4]:,.0f}")
        # y -= 6
        # c.drawString(5, y, f"Total Bayar : {transaksi_data[2]:,.0f}")
        # y -= 10
        # Ringkasan pembayaran
        c.drawString(5, y, f"Total Harga : {transaksi_data_dict['transaksi_bulat']:,.0f}")
        y -= 6
        c.drawString(5, y, f"Diskon      : {transaksi_data_dict['diskon_persen']}%")
        y -= 6
        c.drawString(5, y, f"PPN         : {transaksi_data[4]:,.0f}")
        y -= 6
        c.drawString(5, y, f"Total Bayar : {transaksi_data_dict['transaksi_nilai']:,.0f}")
        y -= 10


        # tambahan untuk menampilkan no kartu debit/ credit atau tunai 
        # --- Tambahan: detail pembayaran sesuai metode ---
        # metode = transaksi_data_dict.get("metode_bayar", "tunai").lower()
        metode = int(transaksi_data_dict['settlement_id'])

# transaksi_data_dict["bank_nama"]=hasil_pembayaran.jenis_edc
#                 transaksi_data_dict["bank_from"]=hasil_pembayaran.jenis_kartu
#                 transaksi_data_dict["bank_rekening_nama"]=hasil_pembayaran.kartu
#                 transaksi_data_dict["rekening"]=hasil_pembayaran.approval_code
        print(f'METODE = {metode}')
        if metode > 1:
            no_kartu = transaksi_data_dict["bank_rekening_nama"]
            approve_code = transaksi_data_dict["rekening"]
            nominal = transaksi_data_dict["transaksi_nilai"]

            # Masking no kartu → tampilkan 4 digit terakhir
            if no_kartu and len(no_kartu) > 4:
                no_kartu_tampil = "**** **** **** " + no_kartu[-4:]
            else:
                no_kartu_tampil = no_kartu

            c.setFont("Helvetica-Bold", 6)
            if metode==2: #METODE = 2 artinya settlement_id = 2 , untuk kredit kalau nilainya 3  = debit
                c.drawString(5, y, f"Metode      : KREDIT")
            else:
                c.drawString(5, y, f"Metode      : DEBIT")

            y -= 6
            c.drawString(5, y, f"No Kartu    : {no_kartu_tampil}")
            y -= 6
            c.drawString(5, y, f"Approve Code: {approve_code}")
            y -= 6
            c.drawString(5, y, f"Nominal     : {nominal:,.0f}")
            y -= 10

        else:
            # Kalau tunai, tampilkan uang dibayar & kembalian
            uang_bayar = transaksi_data_dict["transaksi_nilai"] #transaksi_data_dict.get("transaksi_nilai", transaksi_data[2])
            kembalian = transaksi_data_dict.get("kembali", 0)
            c.setFont("Helvetica-Bold", 6)
            c.drawString(5, y, f"Dibayar     : {uang_bayar:,.0f}")
            y -= 6
            c.drawString(5, y, f"Kembali     : {kembalian:,.0f}")
            y -= 10


        c.drawCentredString(center, y, "-" * 40)
        y -= 8

        # Footer (catatan)
        c.setFont("Helvetica", 5)
        for key in ("footer1", "footer2", "footer3"):
            if setting.get(key):
                c.drawCentredString(center, y, setting[key])
                y -= 6

        c.save()
        self._buka_preview_pdf(pdf_path)
        self._cetak_ke_printer(pdf_path)

    def parse_rupiah(self, text: str) -> float:
        """Mengubah string rupiah lokal ke float Python"""
        if not text:
            return 0.0
        try:
            cleaned = text.replace(".", "").replace(",", ".")
            return float(cleaned)
        except Exception as e:
            print(f"❌ Error parse_rupiah: {e} | raw: {text}")
            return 0.0

    def _buka_preview_pdf(self, pdf_path):
        if platform.system() == "Windows":
            os.startfile(pdf_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", pdf_path])
        else:
            subprocess.run(["xdg-open", pdf_path])

    def _cetak_ke_printer(self, pdf_path):
        try:
            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(
                0,
                "print",
                pdf_path,
                None,
                ".",
                0
            )
            print(f"Struk dikirim ke printer: {printer_name}")
        except ImportError:
            print("❌ Gagal cetak langsung (pywin32 belum terinstal)")
        except Exception as e:
            print(f"❌ Error saat cetak: {e}")

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_F3:
    #         self.buka_customer_dialog()

    # def buka_customer_dialog(self):
    #     customer_list = self.model.load_all_customers()  # atau cache lokal
    #     dialog = CustomerSearchController(customer_list)
    #     selected_id = dialog.show()
    #     if selected_id:
    #         print("Customer dipilih:", selected_id)

    def proses_pilih_barang(self, display_text):
        if getattr(self, '_proses_barang_aktif', False):
            return  # prevent double trigger

        self._proses_barang_aktif = True

        try:
            # buka dialog jumlah, proses barang
            barang_data = self.barang_mapping.get(display_text)
            if not barang_data:
                return
            jumlah, ok = self.view.input_jumlah_dialog()
            if not ok:
                return
            
            existing_row, jumlah_lama = self.view.find_barang_row_by_id(str(barang_data['id']))
            jumlah_total = jumlah + jumlah_lama
            print(f'jalankan fungis cari barang by id dengan id barang = {barang_data["id"]}, dan jumlah total = {jumlah_total}')
            barang_detail = self.model.cari_barang_by_id(str(barang_data['id']), jumlah_total)
            # self.data_barang_cache[barang_data['id']] = barang_detail

            # ✅ Simpan detail ke cache
            self.data_barang_cache[str(barang_data['id'])] = barang_detail
            print(f"id barang = {barang_data['id']}, barcode = {barang_detail['barcode']}  ada di baris = {existing_row} , jumlah lama = {jumlah_lama}, diskon grosir = {barang_detail['diskon_persen']}")
            if existing_row is not None:
                self.view.update_row_barang(existing_row, barang_detail)
            else:
                self.view.tambah_barang_ke_tabel(barang_detail)

            # ✅ Tampilkan info diskon interaktif
            self.view.update_info_diskon(barang_detail)

            # self.view.tampilkan_info_diskon(barang_detail)
            self.view.update_ringkasan()

        finally:
            self._proses_barang_aktif = False


    # import requests
    # import datetime

    def cek_kuota_free_produk(self,barang):
        """
        Mengecek kuota free produk ke server, dipanggil saat user input barang.
        """
        url = "https://beta.mayagrahakencana.com/main_sb/eusvc/proDiskon/checkFreeProdukQuota"  # Misal endpoint check quota (pastikan sesuai)
        
        # Jika tidak ada endpoint khusus check, kamu bisa pakai saveFreeProduk, tapi nanti tidak update quota (hanya check)
        data = {
            # 'diskon_id': barang["diskon_id"],
            'produk_id': barang["id"],
            'produk_nama': barang["nama"],
            'free_produk_id': barang["free_produk_id"],
            'free_produk_nama': barang["free_produk_nama"],
            'free_qty': barang["jumlah_free"],
            'kelipatan': barang.get("kelipatan", 1),
            'quota_global': barang.get("quota_global", 0),
            'quota_used': barang.get("quota_used", 0),
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'settlement': 1,  # <--- flag hanya check
            'transaksi_id': "",
            'transaksi_no': "",
            'toko_id': 1001,
            'oleh_id': 999,  # contoh, ganti dengan user login
            'oleh_nama': "kasir",
            'customer_id': 1,
            'customer_nama': "Tunai"
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            print("❌ Error cek kuota free produk:", e)
            return {"status": 0, "reason": str(e)}

    def find_barang_row_by_id(self, id_barang: str):
        for row in range(self.view.table_barang.rowCount()):
            item = self.view.table_barang.item(row, 0)  # kolom 0 = ID
            if item and item.text() == id_barang:
                jumlah_item = self.view.table_barang.item(row, 4)
                jumlah = int(jumlah_item.text().replace(".","").replace(",",".")) if jumlah_item else 0
                return row, jumlah
        return None, 0

    def handle_input_barcode(self):
        print('masuk ke handle input barcode')
        barcode_input = self.view.barang_input.text().strip()
        if not barcode_input:
            return

        self.view.barang_input.clear()  # Kosongkan setelah input

        # 🔍 Cari barang berdasarkan barcode
        barang_detail = self.model.cari_barang_by_barcode(barcode_input)
        # print(f'nilai barang bdari barcode = {barang_detail}')
        if not barang_detail:
            # from PySide6.QtWidgets import QMessageBox
            # QMessageBox.warning(self.view, "Barcode Tidak Ditemukan", f"Barang dengan barcode '{barcode_input}' tidak ditemukan.")
            return

        id_barang = str(barang_detail["id"])
        existing_row, jumlah_lama = self.find_barang_row_by_id(id_barang)

        # 🚀 Tentukan jumlah
        if self.view.popup_checkbox.isChecked():
            jumlah, ok = self.view.input_jumlah_dialog()
            if not ok:
                return
        else:
            jumlah = 1

        jumlah_total = jumlah + (jumlah_lama if jumlah_lama else 0)
        barang_detail = self.model.cari_barang_by_id(id_barang, jumlah_total)

        # 🔁 Update cache
        self.data_barang_cache[id_barang] = barang_detail

        if existing_row is not None:
            self.view.update_row_barang(existing_row, barang_detail)
        else:
            self.view.tambah_barang_ke_tabel(barang_detail)

        self.view.update_info_diskon(barang_detail)
        self.view.update_ringkasan()

    def handle_barang_input(self):
        print('masuk ke handle barang input ')
        text = self.view.barang_input.text().strip()
        self.view.barang_input.clear()

        if not text:
            return

        # 🔍 Jika input adalah BARCODE (angka 5 digit atau lebih)
        if re.fullmatch(r"\d{5,}", text):
            barang_detail = self.model.cari_barang_by_barcode(text)


            # print(f'nilai barang = {barang_detail}')
            if not barang_detail:
                # QMessageBox.warning(self.view, "Barcode Tidak Ditemukan", f"Barcode '{text}' tidak ditemukan.")
                return
        
        else:
            # Autocomplete: gunakan hasil text untuk cari barang berdasarkan nama
            barang_detail = self.model.cari_barang_by_nama(text)
            if not barang_detail:
                QMessageBox.warning(self.view, "Barang Tidak Ditemukan", f"Barang '{text}' tidak ditemukan.")
                return

        id_barang = str(barang_detail["id"])
        existing_row, jumlah_lama = self.find_barang_row_by_id(id_barang)

        # def handle_pilih_barang(self, produk_id):
        # print(f'id barang nya untuk di cek diskon nya adalah {id_barang}')
        # self.diskon_controller.tampilkan_keterangan_produk_grosir(id_barang)


        # 🚀 Tentukan jumlah
        if self.view.popup_checkbox.isChecked():
            jumlah, ok = self.view.input_jumlah_dialog()
            if not ok:
                return
        else:
            jumlah = 1

        jumlah_total = jumlah + (jumlah_lama if jumlah_lama else 0)
        barang_detail = self.model.cari_barang_by_id(id_barang, jumlah_total)

        # Simpan ke cache dan update tabel
        self.data_barang_cache[id_barang] = barang_detail
        print('masuk ke handle_barang_input')
        if existing_row is not None:
            self.view.update_row_barang(existing_row, barang_detail)
        else:
            self.view.tambah_barang_ke_tabel(barang_detail)

        self.view.update_info_diskon(barang_detail)
        self.view.update_ringkasan()

    def handle_jumlah_berubah(self, row, column):
        if column != 4:  # kolom "Jumlah"
            return
        print('masuk ke handle jumlah berubah controler')

        try:
            id_item = self.view.table_barang.item(row, 0)
            if not id_item:
                return

            id_barang = str(id_item.text())
            # print(f'id barang nya untuk di cek diskon nya adalah {id_barang}')
            # self.diskon_controller.tampilkan_keterangan_produk_grosir(id_barang)

            jumlah_item_widget = self.view.table_barang.item(row, 4)
            if not jumlah_item_widget:
                return

            jumlah = int(jumlah_item_widget.text())
            if jumlah <= 0:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self.view, "Input Tidak Valid", "Jumlah tidak boleh nol atau negatif.")
                self.view.set_jumlah_row(row, 1)
                jumlah = 1

            barang_detail = self.model.cari_barang_by_id(id_barang, jumlah)
            self.data_barang_cache[id_barang] = barang_detail

            # ✅ Cegah cellChanged saat update item
            self.view.table_barang.blockSignals(True)

            self.view.update_row_barang(row, barang_detail)

            self.view.table_barang.blockSignals(False)

            self.view.update_info_diskon(barang_detail)
            self.view.update_ringkasan()

        except Exception as e:
            print(f"❌ Gagal update jumlah: {e}")
            self.view.table_barang.blockSignals(False)  # Safety net jika terjadi error

# try:
#     # langkah simpan transaksi...
#     ...
#     return transaksi_id

# except Exception as e:
#     conn.rollback()
#     print("‼️ Error simpan_transaksi:", e)
#     traceback.print_exc()  # 🧠 Ini akan tunjukkan file & baris error yang sebenarnya
#     raise e

    def simpan_transaksi(self):
        print('masuk simpan transaksi')
        data_ui = self.view.kumpulkan_data_transaksi()
        if not data_ui:
            return False

        transaksi_data, detail_data , transaksi_data_dict = data_ui
        try:
            print('mau simpan transaksi ctrl+s')
            transaksi_id = self.model.simpan_transaksi(transaksi_data, detail_data ,transaksi_data_dict)
            from utils.audit_logger import log_audit
            log_audit(self.db_path, transaksi_data_dict["oleh_id"], "INSERT", "transaksi", transaksi_id, f"Transaksi simpan oleh {transaksi_data_dict['oleh_nama']}")
            print('sukses simpan transaksi ctrl + s ')
            self.view.notifikasi_sukses(transaksi_id)
            # # catat kuota global di server

            # # Siapkan list free_produk yang sudah dihitung sebelumnya
            # # Contoh:
            # arr_free_produk = []
            # print('mau proses api free produk')
            # for detail in detail_data:
            #     print(f'jenis diskon produk ={detail.produk_jenis}')
            #     if detail.produk_jenis == "free_produk" and detail.produk_ord_jml > 0:
            #         print(f'free produk ={detail.produk_jenis}')

            #         free_item = {
            #             "diskon_id": 10011 ,  #detail.diskon_id,            # pastikan di detail disiapkan diskon_id
            #             "produk_id": '11702', # detail.produk_id,
            #             "produk_nama": detail.produk_nama,
            #             "free_produk_id": detail.produk_id,
            #             "free_produk_nama": detail.produk_nama,
            #             "free_qty": detail.produk_ord_jml,
            #             "kelipatan": 1 , # detail.kelipatan,            # pastikan di detail disiapkan kelipatan
            #             "quota_global": 1 , #detail.quota_global,
            #             "quota_used": 1, # detail.quota_used,
            #             "transaksi_id": transaksi_id,            # transaksi_id SQLite
            #             "transaksi_no": transaksi_data_dict["nomer"],
            #             "oleh_id": transaksi_data_dict["oleh_id"],
            #             "oleh_nama": transaksi_data_dict["oleh_nama"],
            #             "customer_id": transaksi_data_dict.get("customers_id", 1),
            #             "customer_nama": transaksi_data_dict.get("customers_nama", "Tunai"),
            #         }
            #         arr_free_produk.append(free_item)
            #         print(f'data arr produk = {free_item}')

            # if arr_free_produk:
            #     from models.transaksi_model import update_quota_free_produk_ke_server
            #     result = update_quota_free_produk_ke_server(arr_free_produk)

            #     if result.get("status") == 1:
            #         print("✅ Kuota free produk berhasil diupdate ke server")
            #     else:
            #         print("❌ Gagal update free produk:", result.get("reason"))

            self.view.reset_form()
            return True
        except Exception as e:
            print("‼️ Error simpan_transaksi:", e)
            traceback.print_exc()  # 🧠 Ini akan tunjukkan file & baris error yang sebenarnya
            # self.view.notifikasi_error(str(e))
            return False
    
    def simpan_transaksi_f7(self, hasil_pembayaran):
        print(f"MASUK FUNGSI SIMPAN TRANSAKSI f7")
        # ---------- Load setting struk (CSV) ----------
        # def load_setting_struk(path_csv):
        #     import csv , os
        #     with open(path_csv, newline='', encoding='utf-8') as f:
        #         reader = csv.DictReader(f)
        #         for row in reader:
        #             return row
        #     return {}
        # review tim 1 nomor 1 tanggal 1 oki 2025
        def load_setting_struk(path_csv):
            import csv, os
            setting = {}
            with open(path_csv, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    setting = row
                    break  # ambil baris pertama saja

            # cek baris tambahan manual
            with open(path_csv, encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith("print_mode"):
                        key, val = line.strip().split(",", 1)
                        setting[key] = val
                        break
            return setting


        if not hasil_pembayaran:
            self.view.notifikasi_error("Data pembayaran tidak valid.")
            return False

        data_ui = self.view.kumpulkan_data_transaksi()
        if not data_ui:
            return False

        transaksi_data, detail_data, transaksi_data_dict = data_ui

        try:
            # Simpan metode pembayaran (tunai, kredit, debit)
            # transaksi_data_dict["metode_pembayaran"] = hasil_pembayaran.metode

            # Update nilai transaksi sesuai hasil pembayaran (sudah kena diskon)
            print(f"💡 Total awal transaksi: {transaksi_data_dict['transaksi_nilai']}")
            transaksi_data_dict["transaksi_bulat"] = transaksi_data_dict['transaksi_nilai']

            transaksi_data_dict["transaksi_nilai"] = hasil_pembayaran.total_dibayar
            # transaksi_data_dict["transaksi_bulat"] = hasil_pembayaran.jumlah_dibayar
            transaksi_data_dict["diskon_persen"] = hasil_pembayaran.diskon_member_persen
            print(f"💡 Total setelah diskon (final): {transaksi_data_dict['transaksi_nilai']}")

            print(f'METODE PEMBAYARANG di simpan transaksi f7 = {hasil_pembayaran.metode} ')
            if hasil_pembayaran.metode == "tunai":
                transaksi_data_dict["settlement_id"] = "1"
                transaksi_data_dict["transaksi_dibayar_return"]=hasil_pembayaran.kembali
                # transaksi_data["settlement_id"]="1"
            elif hasil_pembayaran.metode == "kredit":
                
                transaksi_data_dict["settlement_id"] = "2"
                print(f'edc kredit = {hasil_pembayaran.jenis_edc}')
                transaksi_data_dict["bank_nama"]=hasil_pembayaran.jenis_edc
                transaksi_data_dict["bank_from"]=hasil_pembayaran.jenis_kartu
                transaksi_data_dict["bank_rekening_nama"]=hasil_pembayaran.kartu
                transaksi_data_dict["rekening"]=hasil_pembayaran.approval_code
                

                # transaksi_data["settlement_id"]="2"
            elif hasil_pembayaran.metode == "debit":
                print(f'edc debit = {hasil_pembayaran.jenis_edc}')
                transaksi_data_dict["settlement_id"] = "3"
                transaksi_data_dict["bank_nama"]=hasil_pembayaran.jenis_edc
                transaksi_data_dict["bank_from"]=hasil_pembayaran.jenis_kartu
                transaksi_data_dict["bank_rekening_nama"]=hasil_pembayaran.kartu
                transaksi_data_dict["rekening"]=hasil_pembayaran.approval_code

                # transaksi_data["settlement_id"]="3"


            # Simpan transaksi ke database
            transaksi_id = self.model.simpan_transaksi(transaksi_data, detail_data, transaksi_data_dict)

            # Catat audit log
            from utils.audit_logger import log_audit
            log_audit(
                self.db_path,
                transaksi_data_dict["oleh_id"],
                "INSERT",
                "transaksi",
                transaksi_id,
                f"Transaksi simpan(F7) [{hasil_pembayaran.metode}] oleh {transaksi_data_dict['oleh_nama']}"
            )

            # Cetak struk & notifikasi

            print(f'NILAI SETTLEMENT_ID terdeteksi saat masuk cetak _ struk = {transaksi_data_dict["settlement_id"]}')
            # review nomor 1 dari tim 1 tanggal 1 oki 2025 
            setting_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'setting_struk.csv')
            setting = load_setting_struk(setting_path)
            print(f'nilai setting printer nya = {setting}')

            mode = setting.get("print_mode", "preview").lower()
            print(f'mode print sekarang = {mode}')
            if mode == "auto":
                #                 # ---------- Siapkan data item ----------
                # items = []
                # print(f'isi var detail_data = {detail_data}')

                # for d in detail_data:
                #     try:
                #         qty = int(d.produk_ord_jml or 0)
                #         price = int(float(d.produk_ord_hrg or 0))
                #         disc = int(float(d.produk_ord_diskon or 0))
                #     except Exception as e:
                #         print(f"⚠️ Error parsing item {d.produk_nama}: {e}")
                #         qty, price, disc = 0, 0, 0

                #     is_free = (d.produk_jenis == 'free_produk')

                #     items.append({
                #         "name": d.produk_nama,
                #         "qty": qty,
                #         "price": price, #0 if is_free else price,
                #         "disc": 0 if is_free else disc,
                #         "free": is_free
                #     })

                #     self.printer_settings_controller.print_struk(
                #         items, payment, wifi_code, qr_data,
                #         setting, transaksi_data_dict,
                #         copy_no=0   # kalau reprint isi >0
                #     )
                self.print_struk(transaksi_data, detail_data, transaksi_data_dict)
            else:
                self.preview_struk(transaksi_data, detail_data, transaksi_data_dict)

            # if setting.get("print_mode", "preview") == "auto":
            #     self.print_struk(transaksi_data, detail_data, transaksi_data_dict, setting)
            # else:
            #     self.preview_struk(transaksi_data, detail_data, transaksi_data_dict, setting)

            # self.view.controller.cetak_struk(transaksi_data, detail_data, transaksi_data_dict)
            # self.view.controller.preview_struk(transaksi_data, detail_data, transaksi_data_dict)
            # self.view.controller.cetak_struk_pdf(transaksi_data, detail_data, transaksi_data_dict)

            self.view.notifikasi_sukses(transaksi_id)
            print("Catat log audit f7 simpan transaksi")

            # Reset form
            self.view.reset_form()
            return True

        except Exception as e:
            self.view.notifikasi_error(str(e))
            return False


            
    def cetak_struk_terakhir(self):
    # def cetak_struk(self):
        from reportlab.lib.utils import ImageReader
        import tempfile, csv, os
        from datetime import datetime
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A7
        from models.transaksi_model import DetailTransaksi

        def load_setting_struk(path_csv):
            with open(path_csv, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    return row
            return {}

        print('🧾 Cetak struk berdasarkan transaksi terakhir')

        # Ambil transaksi terakhir
        transaksi = self.model.get_transaksi_terakhir()
        if not transaksi:
            QMessageBox.warning(self.view, "Cetak Struk", "Transaksi terakhir tidak ditemukan.")
            return

        detail_rows = self.model.get_detail_transaksi(transaksi["id"])
        detail_data = [
            DetailTransaksi(
                produk_id=row["produk_id"],
                produk_nama=row["produk_nama"],
                produk_ord_hrg=row["produk_ord_hrg"],
                produk_ord_jml=row["produk_ord_jml"],
                produk_jenis=row["produk_jenis"],
                produk_ord_diskon=row["produk_ord_diskon"],
            )
            for row in detail_rows
        ]

        setting_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'setting_struk.csv')
        setting = load_setting_struk(setting_path)

        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"struk_{transaksi['id']}.pdf")

        c = canvas.Canvas(pdf_path, pagesize=A7)
        c.setFont("Helvetica", 6)
        width, height = A7
        y = height - 10
        center = width / 2
        from reportlab.lib.utils import ImageReader

        logo_path = setting.get("logo", "") # os.path.join(os.path.dirname(__file__), '..', 'resources', 'logo', setting.get("logo", ""))
        print(f'path logo = {logo_path}, isi seting log = {setting.get("logo", "")}')
        # if os.path.exists(logo_path):
        try:
            logo_img = ImageReader(logo_path)
            c.drawImage(logo_img, 5, y - 30 , width=25, height=25, preserveAspectRatio=True, mask='auto')
            # y -= 35  # naikkan y setelah logo ditampilkan
        except Exception as e:
            print("‼️ Gagal menampilkan logo:", e)
        # else:
            # print("⚠️ Logo tidak ditemukan di:", logo_path)
        # # Logo
        # logo_path = setting.get("logo", "")
        # if os.path.exists(logo_path):
        #     try:
        #         c.drawImage(ImageReader(logo_path), 5, y - 30 , width=25, height=25, preserveAspectRatio=True, mask='auto')
        #     except Exception as e:
        #         print("‼️ Gagal menampilkan logo:", e)

        # Header
        for key in ("header1", "header2", "header3"):
            if setting.get(key):
                c.drawCentredString(center, y, setting[key])
                y -= 8

        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(center, y, "INVOICE")
        y -= 10
        c.drawCentredString(center, y, transaksi["nomer"])
        y -= 10

        waktu = datetime.strptime(transaksi["dtime"], "%Y-%m-%d %H:%M:%S")
        waktu_str = waktu.strftime("%d/%m/%Y %H:%M")
        c.setFont("Helvetica", 6)
        c.drawCentredString(center, y, f"{waktu_str} | {transaksi['oleh_nama']}")
        y -= 8
        c.drawCentredString(center, y, transaksi.get("customers_nama", ""))
        y -= 8

        c.drawCentredString(center, y, "-" * 40)
        y -= 8
        c.drawString(5, y, "ITEM / KODE")
        y -= 6
        c.drawString(5, y, " QTY  H.SATUAN     TOTAL")
        y -= 6
        c.drawCentredString(center, y, "-" * 40)
        y -= 8

        for item in detail_data:
            nama = item.produk_nama
            harga_satuan = item.produk_ord_hrg
            jumlah = item.produk_ord_jml
            diskon = item.produk_ord_diskon
            harga_diskon = harga_satuan * (1 - diskon / 100)
            subtotal = harga_diskon * jumlah

            c.drawString(5, y, nama)
            y -= 6
            line = f"{jumlah} x {harga_diskon:,.0f}   = {subtotal:,.0f}"
            c.drawString(10, y, line)
            y -= 8

            if y < 40:
                c.showPage()
                y = height - 20

        c.drawCentredString(center, y, "-" * 40)
        y -= 8
        c.drawString(5, y, f"Total Harga : {transaksi['transaksi_bulat']:,.0f}")
        y -= 6
        c.drawString(5, y, f"Diskon      : {transaksi['diskon_persen']}%")
        y -= 6
        c.drawString(5, y, f"PPN         : {transaksi['ppn_persen']:,}")
        y -= 6
        c.drawString(5, y, f"Total Bayar : {transaksi['transaksi_nilai']:,.0f}")
        y -= 10
        c.drawCentredString(center, y, "-" * 40)
        y -= 8

        c.setFont("Helvetica", 5)
        for key in ("footer1", "footer2", "footer3"):
            if setting.get(key):
                c.drawCentredString(center, y, setting[key])
                y -= 6

        c.save()
        self._buka_preview_pdf(pdf_path)
        self._cetak_ke_printer(pdf_path)
