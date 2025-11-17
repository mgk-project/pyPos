
# ---------- VIEW & CONTROLLER (gabung sederhana) ---------- #
from models.return_model import ReturnModel,ReturnItem
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QSpinBox, QHeaderView, QDialog,
    QFormLayout, QDialogButtonBox, QCheckBox, QFrame, QAbstractItemView,
    QCompleter ,QPlainTextEdit,QRadioButton,QGroupBox, QMessageBox
)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QCompleter
from PySide6.QtCore import QEvent, Qt,Signal


from datetime import datetime
from utils.print_return_voucher import ReturnVoucherPrinter  # sesuaikan path kamu


class ReturnView(QDialog):
    """Dialog Return Penjualan dengan support checkbox header "Pilih Semua"""  # <== header
    voucher_terbit = Signal(str)

    def __init__(self, model: ReturnModel, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Return Penjualan")
        self.resize(900, 600)
        self.model = model
        self.transaksi_id_selected = None

        vbox = QVBoxLayout(self)

        # --- Top bar : jenis return & search
        top_bar = QHBoxLayout()
        self.cb_jenis = QComboBox(); self.cb_jenis.addItems(["Per Item", "All Item"])
        self.cb_jenis.currentTextChanged.connect(self.on_jenis_return_changed)

        self.search_edit = QLineEdit(); self.search_edit.setPlaceholderText("Cari nomor / tanggal / customer…")
        self.search_edit.textChanged.connect(self.refresh_master)
        top_bar.addWidget(QLabel("Jenis Return:")); top_bar.addWidget(self.cb_jenis)
        top_bar.addWidget(self.search_edit)
        vbox.addLayout(top_bar)

        # --- Table master transaksi ---
        self.tbl_master = QTableWidget(0, 4)
        self.tbl_master.setHorizontalHeaderLabels(["Nomer", "Tanggal", "Customer", "Total"])
        self.tbl_master.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_master.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_master.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_master.cellClicked.connect(self.master_clicked)
        vbox.addWidget(self.tbl_master)

        # --- Table detail barang ---
        self.tbl_detail = QTableWidget(0, 8)
        self.tbl_detail.setHorizontalHeaderLabels(["✔","Id Produk", "Produk", "Harga", "Qty Jual", "Qty Return", "Subtotal", "Jenis"])
        self.tbl_detail.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_detail.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_detail.itemChanged.connect(self.handle_checkbox_changed)
        vbox.addWidget(self.tbl_detail)

        # Tambahkan checkbox header untuk pilih semua (kolom 0)
        self._add_header_checkbox()

        # --- Tombol proses
        self.btn_return = QPushButton("Terbitkan Voucher Return")
        self.btn_return.setStyleSheet("""
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
        self.btn_return.setEnabled(False)
        self.btn_return.clicked.connect(self.proses_return)
        vbox.addWidget(self.btn_return)

        self.refresh_master()
    def on_jenis_return_changed(self, value):
        print('lakukan perubahan pemilihan cb_jenis')
        is_full = value.lower() == 'full'

        self.header_cb.setChecked(is_full)
        self.header_cb.setEnabled(not is_full)

        for r in range(self.tbl_detail.rowCount()):
            cb_item = self.tbl_detail.item(r, 0)
            if cb_item is not None:
                cb_item.setCheckState(Qt.Checked if is_full else Qt.Unchecked)
                cb_item.setFlags(cb_item.flags() & ~Qt.ItemIsEnabled if is_full else cb_item.flags() | Qt.ItemIsEnabled)

    # def handle_checkbox_changed(self, item):
    def handle_checkbox_changed(self, item=None):

        from PySide6.QtCore import Qt

        # Jika dipanggil manual (item=None), lanjutkan langsung ke logika cek checkbox
        if item is not None and item.column() != 0:
            return
        # elif item==None:
        #     print('masuk item - none')
        #     self.btn_return.setEnabled(True)
        #     return

            

        ada_yang_dicentang = False
        for row in range(self.tbl_detail.rowCount()):
            checkbox_item = self.tbl_detail.item(row, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                ada_yang_dicentang = True
                break

        self.btn_return.setEnabled(ada_yang_dicentang)


    # ---------- Helper header checkbox ----------
    def _add_header_checkbox(self):
        header = self.tbl_detail.horizontalHeader()
        if not hasattr(self, "header_cb"):
            self.header_cb = QCheckBox("Pilih Semua")
            self.header_cb.setTristate(False)
            self.header_cb.stateChanged.connect(self.toggle_select_all)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_pos = self.tbl_detail.viewport().mapToParent(self.tbl_detail.geometry().topLeft())
        self.header_cb.setParent(self.tbl_detail)
        self.header_cb.move(10, 4)  # posisi kira‑kira di header kolom
        self.header_cb.show()

    # ---------- Master ----------
    def refresh_master(self):
        rows = self.model.search_transaksi_master(self.search_edit.text())
        self.tbl_master.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.tbl_master.setItem(r,0, QTableWidgetItem(str(row['id'])))
            self.tbl_master.setItem(r,1, QTableWidgetItem(row['tanggal']))
            self.tbl_master.setItem(r,2, QTableWidgetItem(row['customers_nama']))
            self.tbl_master.setItem(r,3, QTableWidgetItem(f"{row['transaksi_nilai']:,.0f}"))
        self.tbl_detail.setRowCount(0)
        self.btn_return.setEnabled(False)
        self.header_cb.setCheckState(Qt.Unchecked)

    def master_clicked(self, row, _col):
        print('masuk master klik')
        nomer = self.tbl_master.item(row,0).text()
        self.transaksi_id_selected = nomer
        data = self.model.load_transaksi_detail(nomer)
        self.populate_detail(data)
        

    # ---------- Detail ----------
    def populate_detail(self, data):
        self.tbl_detail.setRowCount(len(data))
        self.header_cb.setCheckState(Qt.Unchecked)
        for r, d in enumerate(data):
            chk = QTableWidgetItem(); chk.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
            default_state = Qt.Checked if self.cb_jenis.currentIndex()==1 else Qt.Unchecked
            chk.setCheckState(default_state)
            self.tbl_detail.setItem(r,0, chk)
            self.tbl_detail.setItem(r,1, QTableWidgetItem(str(d['produk_id'])))
            print(f'nilia id = {d["produk_id"]}')
            self.tbl_detail.setItem(r,2, QTableWidgetItem(d['produk_nama']))
            self.tbl_detail.setItem(r,3, QTableWidgetItem(f"{d['produk_ord_hrg']:,.0f}"))
            self.tbl_detail.setItem(r,4, QTableWidgetItem(str(d['produk_ord_jml'])))
            qty_return = d['produk_ord_jml']  #if default_state==Qt.Checked else d['produk_ord_jml']
            print(f'jumlah jual = {str(d["produk_ord_jml"])}, yang diretur = {qty_return}')
            self.tbl_detail.setItem(r,5, QTableWidgetItem(str(qty_return)))
            self.tbl_detail.setItem(r,6, QTableWidgetItem("0"))
            self.tbl_detail.setItem(r,7, QTableWidgetItem("full" if default_state==Qt.Checked else "partial"))
        self.calculate_subtotal()

    def toggle_select_all(self, state):
        print('masuk ke togle select all')
        from PySide6.QtCore import Qt

        # Untuk menghindari pemanggilan handle_checkbox_changed saat item di-set programmatically
        self.tbl_detail.blockSignals(True)  # << penting agar itemChanged tidak ter-trigger berulang

        for r in range(self.tbl_detail.rowCount()):
            item = self.tbl_detail.item(r, 0)
            if item is not None:
                item.setCheckState(Qt.CheckState(state))

            #     qty_jual = int(self.tbl_detail.item(r, 4).text())
            #     self.tbl_detail.setItem(r, 5, QTableWidgetItem(str(qty_jual if state == Qt.Checked else 0)))
                self.tbl_detail.setItem(r, 7, QTableWidgetItem("full" if state == Qt.Checked else "partial"))

        self.tbl_detail.blockSignals(False)  # aktifkan kembali sinyal perubahan
        # self.handle_checkbox_changed(None)   # panggil manual untuk update tombol return
        # tidak perlu cek handle checkbox change  (karena pasti tercentang semua)
        print (f'masuk togel select all dengan state = {state}, qt cek state = {Qt.CheckState(state)}')
        if state==0: 
            self.btn_return.setEnabled(False)
            print('set buton return disabled')
        elif state ==2:
            self.btn_return.setEnabled(True)
            print('set button retrun enable')
        self.calculate_subtotal()


    # def toggle_select_all(self, state):
    #     for r in range(self.tbl_detail.rowCount()):
    #         if self.tbl_detail.item(r,0):
    #             self.tbl_detail.item(r,0).setCheckState(state)
    #             # perbarui qty return juga
    #             qty_jual = int(self.tbl_detail.item(r,3).text())
    #             self.tbl_detail.setItem(r,4, QTableWidgetItem(str(qty_jual if state==Qt.Checked else 0)))
    #             self.tbl_detail.setItem(r,6, QTableWidgetItem("full" if state==Qt.Checked else "items"))
    #     self.calculate_subtotal()

    def calculate_subtotal(self):
        total = 0
        for r in range(self.tbl_detail.rowCount()):
                qty = int(self.tbl_detail.item(r,5).text())
                harga = float(self.tbl_detail.item(r,3).text().replace(',',''))
                subtotal = qty*harga
                self.tbl_detail.setItem(r,6, QTableWidgetItem(f"{subtotal:,.0f}"))
                total += subtotal

            # if self.tbl_detail.item(r,0).checkState()==Qt.Checked:
            #     qty = int(self.tbl_detail.item(r,5).text())
            #     harga = float(self.tbl_detail.item(r,3).text().replace(',',''))
            #     subtotal = qty*harga
            #     self.tbl_detail.setItem(r,6, QTableWidgetItem(f"{subtotal:,.0f}"))
            #     total += subtotal
            # else:
            #     self.tbl_detail.setItem(r,6, QTableWidgetItem("0"))
                print(f'nilai kolom subtotal = {self.tbl_detail.item(r,6).text()}')
        # self.btn_return.setEnabled(total>0)
    # ---------- Proses Return ----------
    def proses_return(self):
        items: List[ReturnItem] = []
        for r in range(self.tbl_detail.rowCount()):
            if self.tbl_detail.item(r,0).checkState()==Qt.Checked:
                produk_nama = self.tbl_detail.item(r,2).text()
                harga = float(self.tbl_detail.item(r,3).text().replace(',',''))
                qty_return = int(self.tbl_detail.item(r,5).text())
                produk_id = self.tbl_detail.item(r,2).text()# "-"  # isi sesuai kebutuhan
                jenis = self.tbl_detail.item(r,7).text()
                items.append(ReturnItem(produk_id, produk_nama, qty_return, harga, jenis))
        if not items:
            QMessageBox.warning(self,"Validasi","Belum ada item terpilih")
            return
        # kode_vcr = self.model.insert_return(self.transaksi_id_selected, items)
        jenis_returnnya='partial'
        if self.cb_jenis.currentIndex()==0:
            jenis_returnnya = 'partial'
        else:
            jenis_returnnya = 'full'

        kode_vcr = self.model.insert_return(
            self.transaksi_id_selected,
            items,
            jenis_returnnya # self.cb_jenis.currentText().lower()
        )

        QMessageBox.information(self,"Voucher Terbit",f"Return berhasil\nKode voucher: {kode_vcr}")
        self.voucher_terbit.emit(kode_vcr)
        printer = ReturnVoucherPrinter(self.model.conn, kode_vcr)
        printer.print_preview(self)

        self.accept()

