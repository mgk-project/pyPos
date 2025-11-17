# from PySide6.QtWidgets import (
#     QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTextEdit,
#     QPushButton, QMessageBox, QComboBox
# )
# from PySide6.QtCore import QDateTime
# from utils.device_utils import (
#     get_device_id, get_ip_address, get_os_info, get_gps_location, simpan_device_baru
# )

# class DeviceRegistrationDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Registrasi Device Baru")
#         self.setFixedSize(500, 700)

#         self.device_id = get_device_id()
#         self.os_info = get_os_info()
#         self.ip_address = get_ip_address()
#         self.location = get_gps_location()
#         self.dtime_in = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

#         main_layout = QVBoxLayout()
#         form_layout = QFormLayout()

#         # 🔒 Info otomatis (readonly)
#         self.le_device_id = QLineEdit(self.device_id)
#         self.le_device_id.setReadOnly(True)
#         form_layout.addRow("Device ID:", self.le_device_id)

#         self.le_com_info = QLineEdit(f"{self.os_info} / IP: {self.ip_address}")
#         self.le_com_info.setReadOnly(True)
#         form_layout.addRow("Com Info:", self.le_com_info)

#         self.le_cpu_info = QLineEdit("CPU info not captured")
#         self.le_cpu_info.setReadOnly(True)
#         form_layout.addRow("CPU Info:", self.le_cpu_info)

#         self.le_browser = QLineEdit("desktop")
#         self.le_browser.setReadOnly(True)
#         form_layout.addRow("Jenis Aplikasi:", self.le_browser)

#         self.le_status = QLineEdit("0 (Pending)")
#         self.le_status.setReadOnly(True)
#         form_layout.addRow("Status:", self.le_status)

#         self.le_jenis = QLineEdit("pos")
#         self.le_jenis.setReadOnly(True)
#         form_layout.addRow("Jenis:", self.le_jenis)

#         self.le_dtime = QLineEdit(self.dtime_in)
#         self.le_dtime.setReadOnly(True)
#         form_layout.addRow("Tanggal Registrasi:", self.le_dtime)

#         # ✅ Input dari user
#         self.le_nama = QLineEdit()
#         form_layout.addRow("Nama Pengguna:", self.le_nama)

#         self.le_alias = QLineEdit()
#         form_layout.addRow("Alias Device:", self.le_alias)

#         self.cb_cabang = QComboBox()
#         self.cb_cabang.addItem("Cabang01", 1)
#         self.cb_cabang.addItem("Cabang02", 2)
#         form_layout.addRow("Cabang:", self.cb_cabang)

#         self.le_keterangan = QTextEdit()
#         form_layout.addRow("Keterangan:", self.le_keterangan)

#         self.le_kelurahan = QLineEdit()
#         self.le_kecamatan = QLineEdit()
#         self.le_kabupaten = QLineEdit()
#         self.le_propinsi = QLineEdit()
#         self.le_alamat = QTextEdit()
#         self.le_toko_id = QLineEdit()

#         form_layout.addRow("Kelurahan:", self.le_kelurahan)
#         form_layout.addRow("Kecamatan:", self.le_kecamatan)
#         form_layout.addRow("Kabupaten:", self.le_kabupaten)
#         form_layout.addRow("Propinsi:", self.le_propinsi)
#         form_layout.addRow("Alamat:", self.le_alamat)
#         form_layout.addRow("Toko ID:", self.le_toko_id)

#         main_layout.addLayout(form_layout)

#         self.btn_submit = QPushButton("Daftarkan Device")
#         self.btn_submit.clicked.connect(self.submit)
#         main_layout.addWidget(self.btn_submit)

#         self.setLayout(main_layout)

#     def submit(self):
#         # Validasi dasar
#         if not self.le_nama.text().strip() or not self.le_alias.text().strip():
#             QMessageBox.warning(self, "Validasi Gagal", "Nama dan Alias wajib diisi.")
#             return

#         try:
#             simpan_device_baru(
#                 device_id=self.device_id,
#                 nama=self.le_nama.text(),
#                 alias=self.le_alias.text(),
#                 cabang_id=self.cb_cabang.currentData(),
#                 cabang_nama=self.cb_cabang.currentText(),
#                 keterangan=self.le_keterangan.toPlainText(),
#                 kelurahan=self.le_kelurahan.text(),
#                 kecamatan=self.le_kecamatan.text(),
#                 kabupaten=self.le_kabupaten.text(),
#                 propinsi=self.le_propinsi.text(),
#                 alamat=self.le_alamat.toPlainText(),
#                 toko_id=self.le_toko_id.text()
#             )
#     #          device_id,
#     # alias,
#     # cabang_id,
#     # cabang_nama,
#     # nama,
#     # keterangan='',
#     # kelurahan='',
#     # kecamatan='',
#     # kabupaten='',
#     # propinsi='',
#     # alamat='',
#     # toko_id=1
#             QMessageBox.information(self, "Registrasi Berhasil", "Device berhasil diregistrasikan.\nMenunggu persetujuan pusat.")
#             self.accept()
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Gagal menyimpan device.\n{str(e)}")

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
import platform, socket
from utils.device_utils import post_device_registration,get_device_id
import datetime


class DeviceRegistrationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registrasi Device")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        self.label_alias = QLabel("Alias (ex: KASIR 1):")
        self.input_alias = QLineEdit()

        self.label_ket = QLabel("Keterangan:")
        self.input_ket = QLineEdit()

        self.label_cabang = QLabel("Cabang:")
        self.combo_cabang = QComboBox()
        # ✅ Ganti ini dengan data cabang sebenarnya dari server
        self.combo_cabang.addItem("Cabang Utama", "101")
        self.combo_cabang.addItem("Cabang Surabaya", "102")

        # cek machine id nya 
        print(f'machine id ini : {self.get_device_id()}')
        # self.button_submit = ("Kirim Registrasi")
        self.button_submit = QPushButton("Kirim Registrasi")
        self.button_submit.clicked.connect(self.kirim_registrasi)

        layout.addWidget(self.label_alias)
        layout.addWidget(self.input_alias)
        layout.addWidget(self.label_ket)
        layout.addWidget(self.input_ket)
        layout.addWidget(self.label_cabang)
        layout.addWidget(self.combo_cabang)
        layout.addWidget(self.button_submit)

        self.setLayout(layout)

    def kirim_registrasi(self):
        alias = self.input_alias.text()
        keterangan = self.input_ket.text()
        cabang_nama = self.combo_cabang.currentText()
        cabang_id = self.combo_cabang.currentData()

        if not alias or not keterangan:
            QMessageBox.warning(self, "Input Kurang", "Harap lengkapi semua field!")
            return

        # Auto info
        data = {
            "machine_id": self.get_device_id(),
            "browser_verif": str(int(datetime.datetime.now().timestamp())),
            "keterangan": keterangan,
            "cabang_nama": cabang_nama,
            "cabang_id": cabang_id,
            "cpu_info": platform.processor(),
            "com_info": socket.gethostname(),
            "alias": alias
        }

        result = post_device_registration(data)

        if result.get("status"):
            QMessageBox.information(self, "Sukses", "Registrasi berhasil dikirim, tunggu approval!")
            self.accept()
        else:
            QMessageBox.critical(self, "Gagal", f"Registrasi gagal: {result.get('reason', 'Unknown error')}")

    def get_device_id(self):
        # Misalnya ambil MAC address, atau ID unik yang sudah kamu gunakan
        print(f'device id ini = {get_device_id()}')
        return get_device_id() #"145862430726560" # sementara saja karena menunggu prosse approval get_device_id()  #self.get_device_id() #"6SJF9V2"  # Ganti sesuai get_device_id() kamu
