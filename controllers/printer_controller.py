# controllers/printer_controller.py
from PySide6.QtWidgets import QMessageBox

class PrinterController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # isi list printer saat pertama kali buka
        self.load_printers()

        # sambungkan tombol
        self.view.btn_tambah.clicked.connect(self.tambah_printer)
        self.view.btn_simpan.clicked.connect(self.simpan_printer)
        self.view.btn_hapus.clicked.connect(self.hapus_printer)
        self.view.btn_set_default.clicked.connect(self.set_default_printer)
        self.view.btn_test.clicked.connect(self.test_printer)

        # kalau klik item list, isi form detail
        self.view.list_printer.itemClicked.connect(self.fill_form_from_list)

    def load_printers(self):
        self.view.list_printer.clear()
        printers = self.model.get_all()
        for p in printers:
            self.view.list_printer.addItem(f"{p['id']} - {p['nama']}")

    def fill_form_from_list(self, item):
        """Ketika user klik list, isi form detail"""
        text = item.text()
        printer_id = int(text.split(" - ")[0])
        printers = self.model.get_all()
        printer = next((p for p in printers if p["id"] == printer_id), None)
        if printer:
            self.view.input_nama.setText(printer["nama"])
            self.view.combo_koneksi.setCurrentText(printer["koneksi"])
            self.view.input_address.setText(printer.get("address") or "")
            self.view.combo_kertas.setCurrentText(str(printer["lebar_kertas"]))
            self.view.spin_margin.setValue(int(printer.get("margin", 0)))
            self.view.current_printer_id = printer_id
        else:
            self.view.current_printer_id = None

    def tambah_printer(self):
        data = {
            "nama": self.view.input_nama.text(),
            "koneksi": self.view.combo_koneksi.currentText(),
            "address": self.view.input_address.text(),
            "lebar_kertas": self.view.combo_kertas.currentText(),
            "margin": self.view.spin_margin.value(),
        }
        self.model.add_printer(data)
        QMessageBox.information(self.view, "Tambah", "✅ Printer berhasil ditambahkan")
        self.load_printers()

    def simpan_printer(self):
        if not hasattr(self.view, "current_printer_id") or not self.view.current_printer_id:
            QMessageBox.warning(self.view, "Simpan", "Pilih printer dulu dari list!")
            return

        data = {
            "nama": self.view.input_nama.text(),
            "koneksi": self.view.combo_koneksi.currentText(),
            "address": self.view.input_address.text(),
            "lebar_kertas": self.view.combo_kertas.currentText(),
            "margin": self.view.spin_margin.value(),
        }
        self.model.update_printer(self.view.current_printer_id, data)
        QMessageBox.information(self.view, "Simpan", "✅ Printer berhasil diperbarui")
        self.load_printers()

    def hapus_printer(self):
        if not hasattr(self.view, "current_printer_id") or not self.view.current_printer_id:
            QMessageBox.warning(self.view, "Hapus", "Pilih printer dulu dari list!")
            return

        self.model.delete_printer(self.view.current_printer_id)
        QMessageBox.information(self.view, "Hapus", "✅ Printer berhasil dihapus")
        self.load_printers()
        self.view.current_printer_id = None

    def set_default_printer(self):
        if not hasattr(self.view, "current_printer_id") or not self.view.current_printer_id:
            QMessageBox.warning(self.view, "Set Default", "Pilih printer dulu dari list!")
            return

        self.model.set_default(self.view.current_printer_id)
        QMessageBox.information(self.view, "Default", "✅ Printer berhasil dijadikan default")

    def test_printer(self):
        koneksi = self.view.combo_koneksi.currentText()
        address = self.view.input_address.text()

        success, msg = self.model.test_connection(koneksi, address)
        if success:
            QMessageBox.information(self.view, "Test Print", msg)
        else:
            QMessageBox.warning(self.view, "Test Print", msg)

# from escpos.printer import Usb, Network
# from PySide6.QtWidgets import QMessageBox,QDialog

# # controllers/printer_controller.py
# class PrinterController:
#     def __init__(self, model, view):
#         self.model = model
#         self.view = view
#         self.view.btn_test.clicked.connect(self.test_print)
#         self.load_printers()
#         self.setup_events()

#     def test_print(self):
#         config = self.view.get_selected_printer_config()
#         success, message = self.model.test_printer_connection(config)

#         if success:
#             self.view.show_info(message)
#         else:
#             self.view.show_error(message)

# # class PrinterController:
# #     def __init__(self, model, view):
# #         self.model = model
# #         self.view = view
#         # self.load_printers()
#         # self.setup_events()

#     def load_printers(self):
#         print('masuk ke load printer')
#         self.view.list_printer.clear()
#         for p in self.model.get_all():
#             self.view.list_printer.addItem(f"{p['nama']} ({p['koneksi']})")

#     def setup_events(self):
#         self.view.btn_test.clicked.connect(self.test_print)

#     def test_print(self):
#         try:
#             nama = self.view.input_nama.text()
#             koneksi = self.view.combo_koneksi.currentText()
#             if koneksi == "usb":
#                 # contoh VID:PID dummy
#                 p = Usb(0x04b8, 0x0202)  
#             elif koneksi == "lan":
#                 ip, port = self.view.input_address.text().split(":")
#                 p = Network(ip, int(port))
#             else:
#                 raise Exception("Koneksi belum didukung")

#             p.text(f"=== TEST PRINT ===\nPrinter: {nama}\n\n")
#             p.cut()
#             QMessageBox.information(self.view, "Sukses", "Test print berhasil.")
#         except Exception as e:
#             QMessageBox.critical(self.view, "Error", f"Gagal print: {e}")
