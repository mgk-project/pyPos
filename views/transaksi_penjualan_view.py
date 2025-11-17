# from PySide6.QtWidgets import QGroupBox,QHBoxLayout,QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QMessageBox, QDialog, QSpinBox, QFormLayout, QDialogButtonBox
# from PySide6.QtWidgets import (
#     QGroupBox,QHBoxLayout,QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget,
#     QTableWidgetItem, QLineEdit, QPushButton, QMessageBox, QDialog, QSpinBox, QFormLayout,
#     QDialogButtonBox,QRadioButton, QButtonGroup,QCheckBox,QAbstractItemView ,QHeaderView # ✅ Tambahkan di sini
# )

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QSpinBox, QHeaderView, QDialog,
    QFormLayout, QDialogButtonBox, QCheckBox, QFrame, QAbstractItemView,
    QCompleter ,QPlainTextEdit,QRadioButton,QGroupBox, QMessageBox
)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QCompleter
from PySide6.QtCore import QEvent, Qt
from models.transaksi_model import DetailTransaksi


from datetime import datetime

from models.detail_transaksi_model import DetailTransaksi
from views.settlement_dialog_view import SettlementDialogView
from controllers.settlement_controller import SettlementController

from utils.db_helper import get_ppn_from_profile
from utils.path_utils import get_db_path
from utils.myhelper import set_editable_only_column
from PySide6.QtGui import QColor

# from PySide6.QtWidgets import QRadioButton, QButtonGroup 
# class TransaksiPenjualanView(QWidget):
#     def __init__(self, controller, user_info, db_path):
#         super().__init__()
#         self.controller = controller
#         self.user_info = user_info
#         self.db_path = db_path
#         self.produk_jenis = 'invoice'

class TransaksiPenjualanView(QWidget):
    def __init__(self, controller, user_info, db_path, parent_window=None):
        super().__init__(parent_window)
        self.controller = controller
        self.user_info = user_info
        self.db_path = db_path
        self.parent_window = parent_window  # 🧩 Tambahan penting
        self.produk_jenis = 'invoice'

#         self.init_ui()
#         self.installEventFilter(self)  # Untuk bisa tangkap event keyboard

# class TransaksiPenjualanView(QWidget):
#     def __init__(self, controller, user_info):
#         super().__init__()
#         self.controller = controller
#         self.user_info = user_info

# class TransaksiPenjualanView(QWidget):
#     def __init__(self, controller):
#         super().__init__()
#         self.controller = controller
        self.init_ui()
        self.installEventFilter(self)
        # set_editable_only_column(self.table, editable_column_index=5)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            self.controller.simpan_transaksi()
        else:
            super().keyPressEvent(event)
    
# def eventFilter(self, obj, event):
#     if event.type() == QEvent.KeyPress:
#         if event.key() == Qt.Key_F2:
#             self.buka_modal_settlement()
#             return True

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()

            if event.modifiers() == Qt.ControlModifier:
                # key = event.key()

                if key == Qt.Key_S:
                    # self.controller.simpan_transaksi()
                    self.controller.buka_penyimpanan_dialog()
                    return True

                elif key == Qt.Key_D:
                    self.reset_form()
                    return True

                elif key == Qt.Key_P:
                    self.controller.cetak_struk_terakhir()
                    return True
            elif key == Qt.Key_F2:
                self.buka_modal_settlement()

            elif key == Qt.Key_F3:
                    self.controller.buka_customer_dialog()
                    return True  # cegah lanjut ke widget lain
            elif key == Qt.Key_F7:
                    self.controller.buka_dialog_pembayaran()
                    return True  # cegah lanjut ke widget lain
            elif key == Qt.Key_F9:
                    self.controller.buka_penyimpanan_dialog()
                    return True
            elif key == Qt.Key_F10:
                    self.controller.load_transaksi_tersimpan()
                    return True
        return super().eventFilter(obj, event)

            
#                     shortcut_load = QShortcut(QKeySequence("F10"), self)
# shortcut_load.activated.connect(self.controller.load_transaksi_tersimpan)
        # return super().eventFilter(obj, event)
    
    def reset_form(self):
        self.table_barang.setRowCount(0)
        self.diskon_input.setValue(0)
        self.total_label.setText("Total: 0")
        self.ppn.setText("")
        self.total_bayar.setText("")
        self.customer_combo.setCurrentIndex(0)
        self.barang_input.clear()

        # Bersihkan info diskon jika ada
        if hasattr(self, 'diskon_groupbox_map'):
            for g, _ in self.diskon_groupbox_map.values():
                g.setParent(None)
            self.diskon_groupbox_map.clear()
            while self.info_diskon_layout.count():
                w = self.info_diskon_layout.takeAt(0).widget()
                if w:
                    w.deleteLater()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Shortcut Info
        shortcut_table = self.create_shortcut_table()
        main_layout.addWidget(shortcut_table)

        # Customer Combo (dengan label)
        customer_layout = QHBoxLayout()
        customer_layout.setSpacing(4)
        label_customer = QLabel("Customer:")
        label_customer.setFixedWidth(80)  # opsional untuk rata
        self.customer_combo = QComboBox()
        self.customer_combo.setStyleSheet("margin: 0px; padding: 0px;")
        customer_layout.addWidget(label_customer)
        customer_layout.addWidget(self.customer_combo)
        main_layout.addLayout(customer_layout)

        # Input barang (dengan label)
        barang_layout = QHBoxLayout()
        barang_layout.setSpacing(4)
        label_barang = QLabel("Cari Barang:")
        label_barang.setFixedWidth(80)
        self.barang_input = QLineEdit()
        self.barang_input.setPlaceholderText("Ketik nama barang...")
        # self.barang_input.returnPressed.connect(self.on_enter_pressed)
        # self.barang_input.returnPressed.connect(self.controller.handle_barang_input)
        self.barang_input.returnPressed.connect(self.controller.handle_input_barcode)

        self.barang_input.setStyleSheet("margin: 0px; padding: 0px;")
        barang_layout.addWidget(label_barang)
        barang_layout.addWidget(self.barang_input)
        main_layout.addLayout(barang_layout)

        # Checkbox input mode
        self.popup_checkbox = QCheckBox("PopUp untuk Barcode ( Dengan PopUp / Langsung menambahkan barang +1 ) ")
        self.popup_checkbox.setStyleSheet("margin: 0px; padding: 0px;")
        main_layout.addWidget(self.popup_checkbox)

        # Gabungkan ke layout utama
        # main_layout.addLayout(form_layout)

        
        # # --- Tabel Barang ---
        # self.table = QTableWidget(0, 6)
        # self.table.setHorizontalHeaderLabels(["ID", "Nama", "Harga", "Jumlah", "Subtotal", "Diskon %"])
        # self.table.horizontalHeader().setStretchLastSection(True)
        # self.table.setMinimumHeight(200)

        # self.table_barang = QTableWidget(0, 7)
        # self.table_barang.setHorizontalHeaderLabels([
        #     "ID", "Barcode", "Nama",  "Harga", "Jumlah", "Subtotal", "Diskon %"
        # ])

        # self.table_barang = QTableWidget(0, 9)
        # self.table_barang.setHorizontalHeaderLabels(["ID","Barcode", "Nama", "Harga", "Jumlah","UOM", "Subtotal", "Diskon %", "Aksi"])
        self.table_barang = QTableWidget(0, 10)
        self.table_barang.setHorizontalHeaderLabels(["ID","Barcode", "Nama", "Harga", "Jumlah","UOM", "Subtotal", "Diskon %", "Aksi","produk_jenis"])
        self.table_barang.setColumnHidden(9, True)  # sembunyikan kolom Produk Jenis



        self.table_barang.horizontalHeader().setStretchLastSection(True)
        self.table_barang.setMinimumHeight(200)

        # 🔒 Sembunyikan kolom ID dari tampilan
        self.table_barang.setColumnHidden(0, True)

        # Hubungkan event perubahan jumlah
        # self.table.cellChanged.connect(self.handle_jumlah_berubah)
        self.table_barang.cellChanged.connect(self.on_table_cell_changed)



        # --- Info Diskon ---
        self.info_diskon_group = QGroupBox("Info Diskon")
        # self.info_diskon_group .setMaximumWidth(280)
        
        self.info_diskon_layout = QVBoxLayout()
        self.info_diskon_layout.setSpacing(4)       # Jarak antar item lebih rapat
        self.info_diskon_layout.setContentsMargins(6, 6, 6, 6)  # Margin kiri-kanan minimal
        self.info_diskon_group.setLayout(self.info_diskon_layout)
        self.info_diskon_group.setMaximumWidth(500)
        self.info_diskon_group.setStyleSheet("QGroupBox { font-weight: bold; } QLabel { margin-bottom: 4px; }")
      
        # Gabungkan Tabel + Info Diskon
        tabel_dan_diskon_layout = QHBoxLayout()
        
        tabel_dan_diskon_layout.addWidget(self.table_barang, stretch=3)
        tabel_dan_diskon_layout.addWidget(self.info_diskon_group, stretch=1)
        # self.info_diskon_layout.addWidget(groupbox, 0, Qt.AlignTop)

        # tabel_dan_diskon_layout.addWidget(self.info_diskon_group)

        main_layout.addLayout(tabel_dan_diskon_layout)

        # --- Ringkasan Transaksi ---
        ringkasan_widget = QWidget()
        ringkasan_layout = QFormLayout(ringkasan_widget)
        ringkasan_widget.setMaximumWidth(250)

        self.total_label = QLabel("0")
        ringkasan_layout.addRow("Total:", self.total_label)

        self.diskon_input = QSpinBox()
        self.diskon_input.setSuffix(" %")
        self.diskon_input.setMaximum(100)
        self.diskon_input.valueChanged.connect(self.update_ringkasan)
        #ringkasan_layout.addRow("Diskon:", self.diskon_input)

        self.ppn = QLineEdit()
        self.ppn.setReadOnly(True)
        # ringkasan_layout.addRow("PPN 10%:", self.ppn)

        self.total_bayar = QLineEdit()
        self.total_bayar.setReadOnly(True)
        # ringkasan_layout.addRow("Total Bayar:", self.total_bayar)

        # Tombol simpan + ringkasan
        bawah_layout = QHBoxLayout()
        self.button_simpan = QPushButton("Simpan Transaksi")
        self.button_simpan.setStyleSheet("""
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
        self.button_simpan.clicked.connect(self.controller.buka_penyimpanan_dialog)
        bawah_layout.addWidget(self.button_simpan)
        bawah_layout.addStretch()
        bawah_layout.addWidget(ringkasan_widget)

        main_layout.addLayout(bawah_layout)
        self.setLayout(main_layout)

    def on_table_cell_changed(self, row, column):
        self.controller.handle_jumlah_berubah(row, column)



    def set_customer_by_id(self, customer_id):
        for index in range(self.customer_combo.count()):
            if self.customer_combo.itemData(index) == customer_id:
                self.customer_combo.setCurrentIndex(index)
                break

    def buka_modal_settlement(self):
        self.settlement_controller = SettlementController(
            db_path=self.db_path,
            user_info=self.user_info,
            parent_window=self

        )
        self.settlement_controller.view.exec()  # pastikan dialog dibuka


    # def buka_modal_settlement(self):
    #     self.settlement_controller = SettlementController(
    #         view=self,
    #         db_path=self.db_path,
    #         user_info=self.user_info,
    #         parent_window=None
    #     )
    #     self.settlement_dialog = SettlementDialogView(self,self.user_info, self.controller)
    #     self.settlement_dialog.exec()

    # def buka_modal_settlement(self):
    #     from controllers.settlement_controller import SettlementController
    #     from views.settlement_dialog_view import SettlementDialogView

    #     # Pastikan controller settlement dibuat
    #     self.settlement_controller = SettlementController(
    #         self, self.db_path, self.user_info, parent_window=self
    #     )

    #     # Buat dan tampilkan dialog
    #     self.settlement_dialog = SettlementDialogView(
    #         self.user_info, self.settlement_controller
    #     )
    #     self.settlement_dialog.exec()
    # def buka_modal_settlement(self):
    #     self.settlement_controller = SettlementController(self, db_path, user_info, parent_window=None) 
    #     self.settlement_dialog = SettlementDialogView(self.user_info, self.controller)
    #     self.settlement_dialog.exec()

    def create_shortcut_table(self):
        shortcut_table = QTableWidget(2, 4)

        # Hilangkan header
        shortcut_table.verticalHeader().setVisible(False)
        shortcut_table.horizontalHeader().setVisible(False)

        # Atur isi shortcut
        shortcut_table.setItem(0, 0, QTableWidgetItem("F2 - Settlement"))
        shortcut_table.setItem(0, 1, QTableWidgetItem("F3 - Customer"))
        shortcut_table.setItem(0, 2, QTableWidgetItem("Ctrl + D - Reset Form"))
        shortcut_table.setItem(0, 3, QTableWidgetItem("Ctrl + P - Cetak Struk"))
        
        # shortcut_table.setItem(0, 2, QTableWidgetItem("F1 - Customer Modal"))
        # shortcut_table.setItem(0, 3, QTableWidgetItem("F10 - Buka Preorder"))
        shortcut_table.setItem(1, 0, QTableWidgetItem("F7 - Pembayaran Transaksi"))
        shortcut_table.setItem(1, 1, QTableWidgetItem("F8 - MultiPayment"))
        shortcut_table.setItem(1, 2, QTableWidgetItem("F9 - Simpan Transaksi"))
        shortcut_table.setItem(1, 3, QTableWidgetItem("F10 - Buka Preorder"))

        # Stretch kolom agar rata
        shortcut_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Nonaktifkan interaksi
        shortcut_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        shortcut_table.setFocusPolicy(Qt.NoFocus)
        shortcut_table.setSelectionMode(QAbstractItemView.NoSelection)
        shortcut_table.setShowGrid(True)

        # ✅ Atur tinggi pas, agar tidak ada baris kosong
        total_rows = 2
        row_height = shortcut_table.verticalHeader().defaultSectionSize()
        shortcut_table.setFixedHeight(row_height * total_rows + shortcut_table.frameWidth() * 2)

        return shortcut_table


  
    def update_info_diskon(self, barang_detail: dict):
        id_barang = str(barang_detail.get("id", ""))

        # Inisialisasi dict penyimpan per barang jika belum ada
        if not hasattr(self, 'diskon_groupbox_map'):
            self.diskon_groupbox_map = {}

        # Cek apakah GroupBox untuk barang ini sudah ada
        if id_barang in self.diskon_groupbox_map:
            groupbox, inner_layout = self.diskon_groupbox_map[id_barang]
            while inner_layout.count():
                item = inner_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        else:
            # Belum ada, buat QGroupBox baru dan simpan ke info_diskon_layout
            groupbox = QGroupBox(f"Diskon untuk ID {id_barang} - {barang_detail.get('nama', '')}")
            groupbox.setMaximumWidth(480)  # Batasi lebar agar tidak terlalu luas
            inner_layout = QVBoxLayout(groupbox)
            # inner_layout = QVBoxLayout()
            inner_layout.setSpacing(4)
            inner_layout.setContentsMargins(6, 6, 6, 6)  # left, top, right, bottom

            groupbox.setLayout(inner_layout)
                        # Style tampilannya
            groupbox.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    margin-top: 6px;
                    padding: 4px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 4px;
                }
                QLabel, QRadioButton {
                    padding-left: 2px;
                }
            """)
            groupbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

            self.diskon_groupbox_map[id_barang] = (groupbox, inner_layout)
            # self.info_diskon_layout.addWidget(groupbox)
            self.info_diskon_layout.addWidget(groupbox, 0, Qt.AlignTop)


        # Tambahkan radio button sesuai diskon yang tersedia
        if barang_detail.get("flag_diskon_grosir"):

            print(f'CEK DISKON GROSIR ,id barang nya untuk di cek diskon nya adalah {id_barang}')
            keterangan_diskon = self.controller.diskon_controller.tampilkan_keterangan_produk_grosir(id_barang)

            radio_grosir = QRadioButton(keterangan_diskon)

            # radio_grosir = QRadioButton("Diskon Grosir : " +barang_detail.get("keterangan_diskon", ""))

            radio_grosir.setToolTip(barang_detail.get("keterangan_diskon", ""))
            radio_grosir.toggled.connect(
                lambda checked, idb=id_barang: self.on_diskon_selected(idb, "grosir") if checked else None
            )
            inner_layout.addWidget(radio_grosir)

        if barang_detail.get("flag_diskon_free"):
            print(f'CEK DISKON FREE PORDUK ,id barang nya untuk di cek diskon nya adalah {id_barang}')
            # keterangan_diskon = self.controller.diskon_controller.tampilkan_keterangan_produk_free(id_barang)
            # keterangan_diskon = "\n".join(f"Free Produk: {jumlah_free} x {nama_free}")
            # cek ke server apakah ada kuota global tersedia, jika tidak maka out saja
            # result = self.controller.cek_kuota_free_produk(barang_detail)

            # if result.get("status") == 1:
            #     print("✅ Masih ada kuota free produk, lanjut tampilkan di POS.")
            #     # tampilkan diskon free produk
            # else:
            #     print("❌ Kuota free produk habis.")
                # tampilkan info di POS (misal QMessageBox)

            nama_free = barang_detail.get("free_produk_nama", "-")
            jumlah_free = barang_detail.get("jumlah_free", 0)
            array_ket = []
            array_ket.append(self.controller.diskon_controller.tampilkan_keterangan_produk_free(id_barang))
            array_ket.append(f"Free Produk: {jumlah_free} x {nama_free}")
            keterangan_diskon = "\n".join(array_ket)
            radio_free = QRadioButton(keterangan_diskon)
            # radio_free = QRadioButton(f"Free Produk: {jumlah_free} x {nama_free}")
            radio_free.setToolTip("Diskon Free Produk")
            radio_free.toggled.connect(
                lambda checked, idb=id_barang: self.on_diskon_selected(idb, "free") if checked else None
            )
            inner_layout.addWidget(radio_free)

        # Jika tidak ada diskon sama sekali
        if not barang_detail.get("flag_diskon_grosir") and not barang_detail.get("flag_diskon_free"):
            inner_layout.addWidget(QLabel("Tidak ada diskon untuk produk ini."))
        else:
            # Otomatis pilih salah satu radio (prioritaskan grosir)
            if barang_detail.get("flag_diskon_grosir"):
                radio_grosir.setChecked(True)
            elif barang_detail.get("flag_diskon_free"):
                radio_free.setChecked(True)
    # def on_diskon_selected(self, id_barang, jenis_diskon):
    #     print(f"Diskon untuk barang ID {id_barang} dipilih: {jenis_diskon}")
    #     # Kalau handler ini milik controller, lempar ke controller:
    #     if hasattr(self.controller, 'on_diskon_selected'):
    #         self.controller.on_diskon_selected(id_barang, jenis_diskon)
            

    # def tampilkan_info_diskon(self, barang):
    #     # Bersihkan isi lama
    #     while self.info_diskon_layout.count():
    #         item = self.info_diskon_layout.takeAt(0)
    #         widget = item.widget()
    #         if widget:
    #             widget.deleteLater()

    #     # Header: ID & Nama Barang
    #     label_id_nama = QLabel(f"Barang: [{barang['id']}] {barang['nama']}")
    #     label_id_nama.setStyleSheet("font-weight: bold;")
    #     self.info_diskon_layout.addWidget(label_id_nama)

    #     # Jenis Barang
    #     self.info_diskon_layout.addWidget(QLabel("Jenis: invoice"))  # Atau ambil dari barang['jenis']

    #     self.diskon_button_group = QButtonGroup(self)

    #     if barang.get("flag_diskon_grosir"):
    #         radio_grosir = QRadioButton(f"Grosir: {barang['diskon_persen']}% + {barang['keterangan_diskon']}")
    #         self.diskon_button_group.addButton(radio_grosir)
    #         self.info_diskon_layout.addWidget(radio_grosir)

    #     if barang.get("flag_diskon_free"):
    #         jumlah_free = barang.get("jumlah_free", 0)
    #         nama_free = barang.get("free_produk_nama", "-")
    #         radio_free = QRadioButton(f"Free Produk: {nama_free} x{jumlah_free}")
    #         self.diskon_button_group.addButton(radio_free)
    #         self.info_diskon_layout.addWidget(radio_free)

    #     # Pilih otomatis radio pertama jika ada
    #     buttons = self.diskon_button_group.buttons()
    #     if buttons:
    #         buttons[0].setChecked(True)

    #     self.info_diskon_group.setVisible(True)
        
    def populate_customer_combo(self, customers):
        for c in customers:
            self.customer_combo.addItem(c["nama"], c["id"])

    # def set_barang_autocomplete(self, barang_list):
    #     from PySide6.QtWidgets import QCompleter
    #     completer = QCompleter(barang_list)
    #     completer.setCaseSensitivity(Qt.CaseInsensitive)
    #     completer.setFilterMode(Qt.MatchContains)
    #     self.barang_input.setCompleter(completer)
    #     completer.activated.connect(self.pilih_barang)
    # def set_barang_autocomplete(self, barang_list):
    #     from PySide6.QtWidgets import QCompleter
    #     completer = QCompleter(barang_list)
    #     completer.setCaseSensitivity(Qt.CaseInsensitive)
    #     completer.setFilterMode(Qt.MatchContains)
    #     self.barang_input.setCompleter(completer)

    #     # ✅ Gunakan sinyal dengan parameter string
    #     completer.activated[str].connect(self.pilih_barang)
    def pilih_barang(self, text=None):
        # Jika dipanggil via enter (returnPressed), ambil dari input
        if text is None:
            text = self.barang_input.text()

        # ✅ Kosongkan input setelah memilih
        self.barang_input.clear()

        # Proses barang terpilih
        self.controller.proses_pilih_barang(text)
    def set_barang_autocomplete(self, barang_list):
    # from PySide6.QtWidgets import QCompleter
        self.completer = QCompleter(barang_list)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.barang_input.setCompleter(self.completer)

        # Hanya aktif jika user memilih item dari suggestion
        self.completer.activated[str].connect(self.on_barang_selected)

        # Tekan Enter biasa
        self.barang_input.returnPressed.connect(self.on_enter_pressed)
    def on_enter_pressed(self):
        popup = self.completer.popup()
        if popup and popup.isVisible():
            return  # Jangan proses jika sedang pilih dari daftar

        text = self.barang_input.text()
        if text.strip():  # hanya proses jika ada isi
            self.barang_input.clear()
            self.controller.proses_pilih_barang(text)

    def on_barang_selected(self, text):
        if text.strip():
            self.barang_input.clear()
            # ✅ Panggil hanya sekali, tanpa triggering returnPressed
            self.controller.proses_pilih_barang(text)
    
    
    def find_barang_row_by_id(self, id_barang):
        for row in range(self.table_barang.rowCount()):
            item = self.table_barang.item(row, 0)  # kolom 0 = id
            print(f"id tabel = {item.text()}")
            if item and item.text() == id_barang:
                jumlah = int(self.table_barang.item(row, 4).text())  # kolom 4 = jumlah
                print(f"jumlah = {jumlah}")
                return row, jumlah
        return None, 0

    def set_jumlah_row(self, row, jumlah):
        print('masuk ke update jumlah')
        self.table_barang.blockSignals(True)
        self.table_barang.setItem(row, 4, QTableWidgetItem(str(jumlah)))
        self.table_barang.blockSignals(False)

    # def update_row_barang(self, row, barang_detail):
    #     harga = barang_detail["harga"]
    #     jumlah = barang_detail["jumlah"]
    #     diskon = barang_detail.get("diskon_persen", 0)
    #     subtotal = jumlah * (harga - (harga * diskon / 100))

    #     self.table_barang.blockSignals(True)
    #     self.table_barang.setItem(row, 3, QTableWidgetItem(str(harga)))  # harga
    #     self.table_barang.setItem(row, 4, QTableWidgetItem(str(jumlah)))  # jumlah
    #     self.table_barang.setItem(row, 5, QTableWidgetItem(str(self.format_rupiah(subtotal))))  # subtotal
    #     self.table_barang.setItem(row, 6, QTableWidgetItem(f"{diskon:.2f}"))  # diskon
    #     self.table_barang.blockSignals(False)
    def update_row_barang(self, row, barang):
        self.table_barang.blockSignals(True)

        kolom_data = [
            (3, self.format_rupiah(barang["harga"])),
            (4, str(barang["jumlah"])),
            (5, barang["satuan"]),
            (6, self.format_rupiah(barang["harga"] * barang["jumlah"])),
            (7, f"{barang['diskon_persen']:.2f}")
        ]

        for col, value in kolom_data:
            item = self.table_barang.item(row, col)
            if item:
                item.setText(str(value))

        for col in range(self.table_barang.columnCount()):
            item = self.table_barang.item(row, col)
            if not item:
                continue
            if col == 4:
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                item.setBackground(QColor("#FFFFFF"))
            else:
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setBackground(QColor("#F5F500"))

        self.table_barang.blockSignals(False)

    def tambah_barang_ke_tabel(self, barang):
        # id_barang = str(barang['id'])
        jumlah_baru = int(barang['jumlah'])
        print(f'nilai kolom harga = {barang["harga"]}')
        harga = float(barang['harga'])
        diskon_persen = float(barang['diskon_persen'])
        # barcode = str(barang['barcode'])
        # print(f'harga barang = {harga}, diskon_persen = {diskon_persen}')
        # Hitung harga setelah diskon
        harga_diskon = harga - (harga * diskon_persen / 100)
        subtotal_baru = harga_diskon * jumlah_baru


        row = self.table_barang.rowCount()
        self.table_barang.insertRow(row)

        # def create_item(text, editable=False):
        #     item = QTableWidgetItem(str(text))
        #     if not editable:
        #         item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        #     return item

        # self.table.setItem(row, 0, create_item(barang['id']))               # ID
        # self.table.setItem(row, 2, create_item(barang['nama']))             # Nama
        # self.table.setItem(row, 1, create_item(barang.get('barcode', '')))  # Barcode
        # self.table.setItem(row, 3, create_item(str(self.format_rupiah(harga)), editable=False))            # Harga
        # self.table.setItem(row, 4, create_item(str(jumlah_baru), editable=True))  # ✅ Jumlah (editable)
        
        # # harga_diskon = barang['harga'] - (barang['harga'] * barang['diskon_persen'] / 100)
        # # subtotal = barang['jumlah'] * harga_diskon
        # self.table.setItem(row, 5, create_item(str(self.format_rupiah(subtotal_baru))))         # Subtotal
        # self.table.setItem(row, 6, create_item(f"{diskon_persen:.2f}"))    # Diskon %

        # item = self.table.item(row, 0)
        # item.setBackground(QColor("#F5F500"))  # abu-abu muda
        # item = self.table.item(row, 1)
        # item.setBackground(QColor("#F5F500"))  # abu-abu muda
        # item = self.table.item(row, 2)
        # item.setBackground(QColor("#F5F500"))  # abu-abu muda
        # item = self.table.item(row,3)
        # item.setBackground(QColor("#F5F500"))  # abu-abu muda
        # item = self.table.item(row, 4)
        # item.setBackground(QColor("#0000FF"))  # abu-abu muda
        # item = self.table.item(row, 5)
        # item.setBackground(QColor("#F5F500"))  # abu-abu muda
        # item = self.table.item(row, 6)
        # item.setBackground(QColor("#F5F500"))  # abu-abu muda
        kolom_data = [
            (0, barang['id'], False),
            (1, barang.get('barcode', ''), False),
            (2, barang['nama'], False),
            (3, self.format_rupiah(harga), False),
            (4, jumlah_baru, True),  # ✅ hanya kolom 4 editable
            (5, barang['satuan'], False),
            (6, self.format_rupiah(subtotal_baru), False),
            (7, f"{diskon_persen:.2f}", False),
        ]

        for col, value, editable in kolom_data:
            item = QTableWidgetItem(str(value))
            if not editable:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            if col==4:
                bg_color = "#FFFFFF" 
            else:
                bg_color =  "#F5F500"
            
            item.setBackground(QColor(bg_color))
            self.table_barang.setItem(row, col, item)

        # Tombol hapus
        btn_hapus = QPushButton("Hapus")
        btn_hapus.setFixedSize(70, 24)  # Lebar: 70px, Tinggi: 24px
        btn_hapus.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 2px 4px;  /* lebih ramping */
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        # btn_hapus.setStyleSheet("""
        #     QPushButton {
        #         background-color: #28a745;  /* hijau terang */
        #         color: white;
        #         font-weight: bold;
        #         padding: 3px 8px;
        #         border-radius: 8px;
        #     }
        #     QPushButton:hover {
        #         background-color: #218838;  /* hijau gelap saat hover */
        #     }
        # """)
        btn_hapus.clicked.connect(lambda _, r=row: self.hapus_baris(r))
        self.table_barang.setCellWidget(row, 8, btn_hapus)

        # self.label_info_diskon.setText(
            # f"Diskon: {barang['diskon_persen']}%<br>{barang['keterangan_diskon']}"
        # )

    # def hapus_baris(self, row):
    #     self.table.removeRow(row)
    #     self.refresh_tombol_hapus()
    #     self.update_total()

    def refresh_tombol_hapus(self):
        for r in range(self.table_barang.rowCount()):
            btn_hapus = QPushButton("Hapus")
            btn_hapus.setStyleSheet("""
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
            btn_hapus.clicked.connect(lambda _, row_index=r: self.hapus_baris(row_index))
            self.table_barang.setCellWidget(r, 8, btn_hapus)

    # def hapus_baris(self, row):
    #         produk_id_item = self.table_barang.item(row, 0)
    #         produk_id = produk_id_item.text() if produk_id_item else ""

    #         barang_detail = self.controller.data_barang_cache[produk_id]

    #         # produk_id_item = self.table_barang.item(row, 0)  # kolom 0: id produk
    #         self.table_barang.removeRow(row)
    #         self.refresh_tombol_hapus()
    #         # self.update_total()
    #         self.update_ringkasan()  # Perbarui total bayar, PPN, dst.
    #         # barang_detail = self.controller.data_barang_cache[produk_id_item]
    #         self.hapus_info_diskon(barang_detail)

    def hapus_baris(self, row):
        produk_id_item = self.table_barang.item(row, 0)
        if not produk_id_item:
            return

        produk_id = produk_id_item.text()
        barang_detail = self.controller.data_barang_cache.get(produk_id, {})

        # Hapus info diskon
        self.hapus_info_diskon(barang_detail)

        # Hapus row
        self.table_barang.removeRow(row)
        self.refresh_tombol_hapus()
        self.update_ringkasan()
    # self.refresh_keterangan_diskon()


    def hapus_info_diskon(self, barang_detail: dict):
        id_barang = str(barang_detail.get("id", ""))

        # Pastikan diskon_groupbox_map sudah diinisialisasi
        if not hasattr(self, 'diskon_groupbox_map'):
            self.diskon_groupbox_map = {}

        # Cek apakah ada GroupBox untuk id_barang ini
        if id_barang in self.diskon_groupbox_map:
            groupbox, _ = self.diskon_groupbox_map[id_barang]

            # Hapus widget groupbox dari layout
            self.info_diskon_layout.removeWidget(groupbox)
            groupbox.deleteLater()

            # Hapus dari dictionary map
            del self.diskon_groupbox_map[id_barang]

            print(f"✅ Info diskon untuk barang ID {id_barang} berhasil dihapus.")
        else:
            print(f"ℹ️ Tidak ditemukan info diskon untuk barang ID {id_barang}.")


            # self.refresh_keterangan_diskon()  # ← tambahkan ini

    # def refresh_keterangan_diskon(self):
    #     if self.table_barang.rowCount() == 0:
    #         # self.diskon_view.tampilkan_keterangan_diskon("Tidak ada diskon grosir.")
    #         return

    #     # Misalnya ambil produk_id dari baris pertama sebagai acuan
    #     produk_id_item = self.table_barang.item(0, 0)  # kolom 0: id produk
    #     if not produk_id_item:
    #         # self.diskon_view.tampilkan_keterangan_diskon("Tidak ada diskon grosir.")
    #         return

    #     produk_id = produk_id_item.text()

    #     # Panggil controller diskon untuk update info
    #     self.controller.diskon_controller.tampilkan_keterangan_produk_grosir(produk_id)

    # def update_total(self):
    #     total = 0
    #     for r in range(self.table_barang.rowCount()):
    #         subtotal_item = self.table_barang.item(r, 5)
    #         if subtotal_item:
    #             try:
    #                 total += float(subtotal_item.text())
    #             except ValueError:
    #                 pass
    #     print("Total baru:", total)


        # for col, value, editable in kolom_data:
        #     item = QTableWidgetItem(str(value))
        #     if not editable:
        #         item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        #     bg_color = "#FFFFFF" if editable else "#F5F500"
        #     item.setBackground(QColor(bg_color))
        #     self.table_barang.setItem(row, col, item)

    def on_diskon_selected(self, id_barang, jenis_diskon):
        """Dipanggil saat user memilih radio diskon (grosir / free)"""
        print(f"Diskon untuk barang ID {id_barang} dipilih: {jenis_diskon}")
        self.recalculate_diskon_barang(id_barang, jenis_diskon)

    def recalculate_diskon_barang(self, id_barang, jenis_diskon_terpilih):
        """Hitung ulang subtotal berdasarkan diskon yang dipilih"""
        for row in range(self.table_barang.rowCount()):
            id_item = self.table_barang.item(row, 0)  # Kolom 0 = ID
            if not id_item or id_item.text() != str(id_barang):
                continue

            harga_item = self.table_barang.item(row, 3)    # Kolom 3 = Harga
            jumlah_item = self.table_barang.item(row, 4)   # Kolom 4 = Jumlah

            subtotal_item = self.table_barang.item(row, 6) # Kolom 6 = Subtotal
            diskon_item = self.table_barang.item(row, 7)   # Kolom 7 = Diskon Persen

            if not harga_item or not jumlah_item:
                continue

            try:
                harga = float(harga_item.text().replace(".", "").replace(",", "."))
                jumlah = int(float(jumlah_item.text().replace(".", "").replace(",", ".")))
            except ValueError:
                continue

            # barang_detail = self.controller.data_barang_cache.get(str(id_barang), {})
            barang_data = self.controller.data_barang_cache[str(id_barang)]
            # tambahkan update info apakah diskon biasa ataukan diskon free produk
            # kalau diskon free produk , maka akan dilaporkan ke data server untuk pemakaian global quota
            # print(f'self.produk jenis nya = {self.produk_jenis}')


            # if jenis_diskon_terpilih == "grosir":
            #     diskon_persen = barang_data.get("diskon_persen", 0)
            #     # print(f'diskon groisr : {diskon_persen}')
            #     harga = barang_data.get("harga", harga)
            #     subtotal = harga * jumlah * (1 - diskon_persen / 100)
            #     self.produk_jenis = 'invoice'  # default
            # elif jenis_diskon_terpilih == "free":
            #     diskon_persen = 0
            #     harga = barang_data.get("harga", harga)
            #     subtotal = harga * jumlah
            #     self.produk_jenis = 'free_produk'  # default
            # else:
            #     diskon_persen = 0
            #     subtotal = harga * jumlah
            #     self.produk_jenis = 'invoice'  # default
            if jenis_diskon_terpilih == "grosir":
                diskon_persen = barang_data.get("diskon_persen", 0)
                harga = barang_data.get("harga", harga)
                subtotal = harga * jumlah * (1 - diskon_persen / 100)
                self.table_barang.setItem(row, 9, QTableWidgetItem("diskon_grosir"))

            elif jenis_diskon_terpilih == "free":
                diskon_persen = 0
                harga = barang_data.get("harga", harga)
                subtotal = harga * jumlah
                self.table_barang.setItem(row, 9, QTableWidgetItem("free_produk"))

            else:
                diskon_persen = 0
                subtotal = harga * jumlah
                self.table_barang.setItem(row, 9, QTableWidgetItem("invoice"))


            # print(f"subtotal = {subtotal}")
            # Tulis ulang ke tabel (format rupiah . -> ,)
            # harga_item.setText(f"{harga:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            # subtotal_item.setText(f"{subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            # diskon_item.setText(f"{diskon_persen:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            harga_item.setText(self.format_rupiah(harga))
            if subtotal_item is None:
                subtotal_item = QTableWidgetItem()
                self.table_barang.setItem(row, 6, subtotal_item)
            if diskon_item is None:
                diskon_item = QTableWidgetItem()
                self.table_barang.setItem(row, 7, diskon_item)

            subtotal_item.setText(self.format_rupiah(subtotal))
            diskon_item.setText(f'{diskon_persen:,.2f}')
            break  # hanya satu baris per id

        self.update_ringkasan()  # Perbarui total bayar, PPN, dst.


    def update_ringkasan(self):
        # total = 0
        # for row in range(self.table.rowCount()):
        #     subtotal_item = self.table.item(row, 4)  # kolom 4 = subtotal
        #     if subtotal_item:
        #         try:
        #             total += float(subtotal_item.text())
        #         except ValueError:
        #             pass
        total_harga = 0.0

        for row in range(self.table_barang.rowCount()):
            subtotal_item = self.table_barang.item(row, 6)  # Kolom 6 = Subtotal
            if not subtotal_item:
                continue

            text = subtotal_item.text().replace(",", "").replace(".", "")
            if len(text) > 2:
                text = text[:-2] + "." + text[-2:]  # Konversi ke format float
            try:
                subtotal = float(text)

                total_harga += subtotal
            except ValueError:
                continue

        # print(f'total harga = {total_harga}')
        diskon_persen = self.diskon_input.value()
        diskon_nilai = total_harga * diskon_persen / 100
        total_setelah_diskon = total_harga - diskon_nilai
        #    Ambil nilai PPN dari DB
        ppn_value = int(get_ppn_from_profile(get_db_path())) # state.get("ppn") or get_ppn_from_profile(self.db_path)
        # ppn_nilai = (total-diskon_nilai) * (ppn_value / 100 ) # 0.1
            
        # ppn = (total_harga - diskon_nilai) * (ppn_value / 100 )#0.10

        ppn = total_setelah_diskon * (ppn_value / 100 ) # 0.10
        total_bayar = total_setelah_diskon #+ ppn

        # Label ringkasan
        # self.total_label.setText(
        #     f"Total: {total:,.0f} | Diskon: {diskon_persen}% ({diskon_nilai:,.0f}) | "
        #     f"PPN 10%: {ppn:,.0f} | Bayar: {total_bayar:,.0f}"
        # )
        self.total_label.setText(self.format_rupiah(total_harga))
        # ✅ Tampilkan nilai PPN dan total bayar ke komponen terpisah
        if hasattr(self, 'ppn'):
            self.ppn.setText(self.format_rupiah(ppn))
            # self.ppn.setText(f"{ppn:,.0f}")

        if hasattr(self, 'total_bayar'):
            self.total_bayar.setText(self.format_rupiah(total_bayar))
            # self.total_bayar.setText(f"{total_bayar:,.0f}")
    def format_rupiah(self, angka: float) -> str:
            return f"{angka:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def input_jumlah_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Jumlah Barang")

        layout = QFormLayout(dialog)
        spin = QSpinBox()
        spin.setMinimum(1)

        # ✅ Set fokus dan blok semua teks
        spin.setFocus()
        spin.lineEdit().selectAll()

        layout.addRow("Jumlah:", spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        result = dialog.exec()
        return spin.value(), result == QDialog.Accepted
    # def input_jumlah_dialog(self, default=1):
    #     dialog = QDialog(self)
    #     dialog.setWindowTitle("Jumlah Barang")

    #     layout = QVBoxLayout(dialog)
    #     label = QLabel("Masukkan jumlah:")
    #     jumlah_input = QLineEdit(str(default))
    #     jumlah_input.setFocus()       # ✅ Fokus ke input
    #     jumlah_input.selectAll()      # ✅ Blok semua teks

    #     tombol_ok = QPushButton("OK")
    #     tombol_ok.clicked.connect(dialog.accept)

    #     layout.addWidget(label)
    #     layout.addWidget(jumlah_input)
    #     layout.addWidget(tombol_ok)

    #     dialog.setLayout(layout)

    #     if dialog.exec() == QDialog.Accepted:
    #         try:
    #             return int(jumlah_input.text())
    #         except:
    #             return default
    #     return None
    def kumpulkan_data_transaksi(self):
        import re

        def normalisasi_harga(harga_text):
                if not harga_text:
                    return 0.0

                # Jika harga sudah dalam format numerik (misalnya "2000.0"), langsung konversi
                if "," not in harga_text and "." not in harga_text:
                    try:
                        return float(harga_text)
                    except ValueError:
                        return 0.0

                # Jika ada koma → asumsikan format Indonesia
                if "," in harga_text:
                    harga_text = harga_text.replace(".", "")  # hapus titik ribuan
                    harga_text = harga_text.replace(",", ".")  # ubah koma jadi titik desimal

                try:
                    return float(harga_text)
                except ValueError:
                    return 0.0


        if self.table_barang.rowCount() == 0:
            QMessageBox.warning(self, "Validasi", "Belum ada barang ditambahkan.")
            return None

        diskon_input = self.diskon_input.value()
        total_harga = 0
        detail_data = []
        for row in range(self.table_barang.rowCount()):
            try:
                produk_id = int(self.table_barang.item(row, 0).text())
                produk_nama = self.table_barang.item(row, 2).text()
                # harga = float(self.table.item(row, 2).text().replace(",", "").replace(".", ""))
                # harga_text = self.table.item(row, 3).text().replace(".", "").replace(",", ".")
                # harga_text = self.table.item(row, 3).text().replace(".", "").replace(",00", "")
                harga_text = self.table_barang.item(row, 3).text()
                # print(f'fungsi kumpulkan_data_transaksi, harga teks awal = {harga_text}')
                harga = normalisasi_harga(harga_text)
                # harga = int(float(harga_text))  # bulatkan ke int
                # print(f'fungsi kumpulkan_data_transaksi, harga teks normalisasi = {harga}')
                # jumlah = int(self.table.item(row, 3).text())
                jumlah = int(self.table_barang.item(row, 4).text())
                # print(f'fungsi kumpulkan_data_transaksi, jumlah = {jumlah}')
                # Ambil diskon, boleh desimal
                diskon_text = self.table_barang.item(row, 7).text().replace(",", ".")
                # print(f'fungsi kumpulkan_data_transaksi, diskon teks = {diskon_text}')
                diskon = float(diskon_text)
                # Hitung subtotal dan bulatkan
                harga_diskon = harga * (1 - diskon / 100)
                subtotal = int(round(harga_diskon * jumlah))
                total_harga += subtotal
                satuan = self.table_barang.item(row, 5).text()
                # diskon = float(self.table.item(row, 5).text())
                # print(f'harganya = {harga}')
                
                # item = DetailTransaksi(
                #     produk_id=produk_id,
                #     produk_nama=produk_nama,
                #     produk_ord_hrg=harga,
                #     produk_ord_jml=jumlah,
                #     produk_jenis= self.produk_jenis , # 'invoice',  # default; bisa diubah nanti
                #     produk_ord_diskon=diskon,
                #     satuan = satuan
                # )
                item = DetailTransaksi(
                    produk_id=produk_id,
                    produk_nama=produk_nama,
                    produk_ord_hrg=harga,
                    produk_ord_jml=jumlah,
                    produk_jenis=self.table_barang.item(row, 9).text() if self.table_barang.item(row, 9) else "invoice",
                    produk_ord_diskon=diskon,
                    satuan=satuan
                )

                detail_data.append(item)

                

                

            except:
                continue
        # print(f'diskon input = {diskon_input} , total harga = {total_harga}')

        diskon_nilai = total_harga * diskon_input / 100
        #    Ambil nilai PPN dari DB
        ppn_value = int(get_ppn_from_profile(get_db_path())) # state.get("ppn") or get_ppn_from_profile(self.db_path)
        # ppn_nilai = (total-diskon_nilai) * (ppn_value / 100 ) # 0.1
            
        ppn = (total_harga - diskon_nilai) * (ppn_value / 100 )#0.10
        total_bayar = total_harga - diskon_nilai #+ ppn
        print('masuk kumpulkan data transaksi master ')
        now = datetime.now()
        transaksi_data = (
            now.strftime('%Y%m%d%H%M%S') + '-' + self.controller.user_info['nama'],
            now.strftime('%Y-%m-%d %H:%M:%S'),
            int(round(total_bayar)),     # Total Bayar (bulatkan)
            diskon_input,
            int(round(ppn)),             # PPN (bulatkan)
            total_harga,                # Total Harga Sebelum Diskon
            self.customer_combo.currentData(),
            self.customer_combo.currentText(),
            now.strftime('%Y-%m-%d'),
            self.controller.user_info['id'],
            self.controller.user_info['nama'],
            'invoice',
            '758',
            '1' 
        )
        print('masuk kumpulkan data transaksi dict ')
        # transaksi data dict tanpa info bank id dan bank nama
        # transaksi_data_dict = {
        #     'nomer': now.strftime('%Y%m%d%H%M%S') + '-' + self.controller.user_info['nama']  ,
        #     'nomer2': now.strftime('%Y%m%d%H%M%S') + '-' + self.controller.user_info['nama']  ,
        #     'dtime': now.strftime('%Y-%m-%d %H:%M:%S'),
        #     'transaksi_nilai': int(round(total_bayar)),
        #     'diskon_persen': diskon_input,
        #     'ppn_persen': int(round(ppn)),
        #     'transaksi_bulat': total_harga,
        #     'customers_id': self.customer_combo.currentData(),
        #     'customers_nama': self.customer_combo.currentText(),
        #     'fulldate': now.strftime('%Y-%m-%d'),
        #     'oleh_id': self.controller.user_info['id'],
        #     'oleh_nama': self.controller.user_info['nama'],
        #     'jenis_label': 'invoice',
        #     'transaksi_jenis': '758',
        #     'settlement_id': '1'
        # }
        # transaksi data dict ada bank id dan bank nama untuk hitung tunai dan penjualan per edc nya (proses settlement )
        transaksi_data_dict = {
            'nomer': now.strftime('%Y%m%d%H%M%S') + '-' + self.controller.user_info['nama']  ,
            'nomer2': now.strftime('%Y%m%d%H%M%S') + '-' + self.controller.user_info['nama']  ,
            'dtime': now.strftime('%Y-%m-%d %H:%M:%S'),
            'transaksi_nilai': int(round(total_bayar)),
            'diskon_persen': diskon_input,
            'ppn_persen': int(round(ppn)),
            'transaksi_bulat': total_harga,
            'customers_id': self.customer_combo.currentData(),
            'customers_nama': self.customer_combo.currentText(),
            'fulldate': now.strftime('%Y-%m-%d'),
            'oleh_id': self.controller.user_info['id'],
            'oleh_nama': self.controller.user_info['nama'],
            'jenis_label': 'invoice',
            'transaksi_jenis': '758',
            'settlement_id': '1',
            'bank_id':'0',
            'bank_nama':'0'
        }


#nomer, dtime, transaksi_nilai, diskon_persen, ppn_persen, transaksi_bulat, 
                    # customers_id, customers_nama, fulldate, oleh_id, oleh_nama, 
                    # jenis_label, transaksi_jenis, settlement_id
        return transaksi_data, detail_data,transaksi_data_dict

    def notifikasi_sukses(self, transaksi_id):
        QMessageBox.information(self, "Sukses", f"Transaksi #{transaksi_id} berhasil disimpan")

    def notifikasi_error(self, pesan):
        QMessageBox.critical(self, "Error simpan", f"Gagal: {pesan}")

    # def reset_form(self):
    #     self.table.setRowCount(0)
    #     self.diskon_input.setValue(0)
    #     self.total_label.setText("Total: 0")
    def reset_form(self):
        # Reset tabel transaksi
        self.table_barang.setRowCount(0)

        # Reset ringkasan transaksi
        self.diskon_input.setValue(0)
        self.total_label.setText("Total: 0")
        self.ppn.setText("")
        self.total_bayar.setText("")

        # ✅ Bersihkan layout info diskon
        if hasattr(self, 'diskon_groupbox_map'):
            for groupbox, _ in self.diskon_groupbox_map.values():
                groupbox.setParent(None)  # Lepas dari layout dan view
            self.diskon_groupbox_map.clear()

        # Bersihkan widget dari layout
        while self.info_diskon_layout.count():
            item = self.info_diskon_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
