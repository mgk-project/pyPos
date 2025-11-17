from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton, QLabel,
    QLineEdit, QPushButton, QFormLayout, QButtonGroup, QGridLayout, QStackedLayout,QSpinBox
)
from PySide6.QtCore import Qt
from utils.db_helper import get_ppn_from_profile,get_credit_card_names,get_receive_on_account_names,get_debit_card_names,get_receive_on_account_debit  # jika kamu buat di file terpisah
from utils.path_utils import get_db_path 

class PembayaranView(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Pembayaran Transaksi")
        self.setMinimumWidth(800)
        self.init_ui()
        self.atur_style_form()
        

    def init_ui(self):
        self.main_layout = QVBoxLayout()

        # === Info Transaksi ===
        self.label_tanggal = QLabel()
        self.label_jenis = QLabel()
        self.label_qty = QLabel()
        self.label_total = QLabel()
        info_layout = QFormLayout()
        info_layout.addRow("Tanggal:", self.label_tanggal)
        info_layout.addRow("Jenis Item:", self.label_jenis)
        info_layout.addRow("Total Qty:", self.label_qty)
        info_layout.addRow("Total Belanja:", self.label_total)
        #kode voucher
        self.voucher_input = QLineEdit()
        info_layout.addRow("Kode Voucher Retur:", self.voucher_input)

        self.main_layout.addLayout(info_layout)

        # === Radio Button Metode Pembayaran ===
        self.radio_tunai = QRadioButton("Tunai")
        self.radio_credit = QRadioButton("Credit Card")
        self.radio_debit = QRadioButton("Debit Card")
        self.radio_tunai.setChecked(True)

        metode_group = QGroupBox("Metode Pembayaran")
        metode_layout = QVBoxLayout()
        metode_layout.addWidget(self.radio_tunai)
        metode_layout.addWidget(self.radio_credit)
        metode_layout.addWidget(self.radio_debit)
        metode_group.setLayout(metode_layout)

        self.metode_button_group = QButtonGroup()
        self.metode_button_group.addButton(self.radio_tunai)
        self.metode_button_group.addButton(self.radio_credit)
        self.metode_button_group.addButton(self.radio_debit)

        # === FORM TUNAI ===
        self.groupbox_tunai = QGroupBox("Pembayaran Tunai")
        form_tunai = QFormLayout()
        self.input_total_tunai = QLineEdit()

        # self.diskon_tambahan_tunai = QLineEdit()
        self.diskon_tambahan_tunai = QSpinBox()
        self.diskon_tambahan_tunai.setSuffix(" %")
        self.diskon_tambahan_tunai.setMaximum(30)

        self.ppn_tunai = QLineEdit()
        self.input_total_harus_dibayar_tunai = QLineEdit()
        self.input_bayar_tunai = QLineEdit()
        self.input_kembalian_tunai = QLineEdit()
        form_tunai.addRow("Total:", self.input_total_tunai)
        form_tunai.addRow("Diskon Tambahan (max 30%):", self.diskon_tambahan_tunai)
        self.nilai_ppn =  str(get_ppn_from_profile(get_db_path()))
        form_tunai.addRow(f"Nilai PPn {self.nilai_ppn}%:", self.ppn_tunai)
        # form_tunai.addRow("Nilai PPn :", self.ppn_tunai)
        

        form_tunai.addRow("Total Harus Dibayar:", self.input_total_harus_dibayar_tunai)
        form_tunai.addRow("Bayar Tunai:", self.input_bayar_tunai)
        form_tunai.addRow("Kembalian:", self.input_kembalian_tunai)
        self.groupbox_tunai.setLayout(form_tunai)
        


        # === FORM CREDIT ===
        self.groupbox_credit = QGroupBox("Pembayaran Credit Card")
        form_credit = QFormLayout()
        self.input_total_credit = QLineEdit()
        # self.diskon_tambahan_credit = QLineEdit()
        self.diskon_tambahan_credit = QSpinBox()
        self.diskon_tambahan_credit.setSuffix(" %")
        self.diskon_tambahan_credit.setMaximum(30)

        self.ppn_credit = QLineEdit()
        self.input_total_harus_dibayar_credit = QLineEdit()
        self.input_no_kartu_credit = QLineEdit()
        self.input_approval_credit = QLineEdit()
        form_credit.addRow("Total:", self.input_total_credit)
        form_credit.addRow("Diskon Tambahan (max 30%):", self.diskon_tambahan_credit)
        # form_credit.addRow("Diskon (%):", self.diskon_tambahan_credit)

        # nilai_ppn =  str(get_ppn_from_profile(get_db_path()))
        form_credit.addRow(f"Nilai PPn {self.nilai_ppn}%:", self.ppn_credit)

        # form_credit.addRow("PPN (%):", self.ppn_credit)
        form_credit.addRow("Total Bayar:", self.input_total_harus_dibayar_credit)
        form_credit.addRow("No. Kartu:", self.input_no_kartu_credit)
        form_credit.addRow("Approval Code:", self.input_approval_credit)

        credit_inner_layout = QGridLayout()
        credit_inner_layout.addLayout(form_credit, 0, 0)

        jenis_kartu_credit = QGroupBox("Jenis Credit Card")
        jenis_kartu_layout_credit = QVBoxLayout()

        # Ambil daftar bank dari query
        credit_card_names = get_credit_card_names()

        # Simpan radio button dalam list supaya bisa diakses lagi
        self.radio_credit_cards = []

        for idx, bank_name in enumerate(credit_card_names):
            radio_btn = QRadioButton(bank_name)
            if idx == 0:  # Radio pertama di-set terpilih default
                radio_btn.setChecked(True)
            jenis_kartu_layout_credit.addWidget(radio_btn)
            self.radio_credit_cards.append(radio_btn)

        jenis_kartu_credit.setLayout(jenis_kartu_layout_credit)
        credit_inner_layout.addWidget(jenis_kartu_credit, 0, 1)


        receive_credit = QGroupBox("Receive on Account")
        receive_layout_credit = QVBoxLayout()

        # Ambil daftar EDC dari query
        receive_names = get_receive_on_account_names()

        # Simpan radio button supaya bisa diakses nanti
        self.radio_receive_accounts = []

        for idx, receive_name in enumerate(receive_names):
            radio_btn = QRadioButton(receive_name)
            print(f'edc idx {idx} = {receive_name}')
            if idx == 0:  # Pilih default radio pertama
                radio_btn.setChecked(True)
            receive_layout_credit.addWidget(radio_btn)
            self.radio_receive_accounts.append(radio_btn)

        receive_credit.setLayout(receive_layout_credit)
        credit_inner_layout.addWidget(receive_credit, 0, 2)


        self.groupbox_credit.setLayout(credit_inner_layout)

        # === FORM DEBIT ===
        self.groupbox_debit = QGroupBox("Pembayaran Debit Card")
        form_debit = QFormLayout()
        self.input_total_debit = QLineEdit()
        # self.diskon_tambahan_debit = QLineEdit()
        self.diskon_tambahan_debit = QSpinBox()
        self.diskon_tambahan_debit.setSuffix(" %")
        self.diskon_tambahan_debit.setMaximum(100)
        # self.diskon_tambahan_debit.valueChanged.connect(self.update_ringkasan)

        self.ppn_debit = QLineEdit()
        self.input_total_harus_dibayar_debit = QLineEdit()
        self.input_no_kartu_debit = QLineEdit()
        self.input_approval_debit = QLineEdit()
        form_debit.addRow("Total:", self.input_total_debit)
        form_debit.addRow("Diskon Tambahan (max 30%):", self.diskon_tambahan_debit)
        # form_debit.addRow("Diskon Tambahan (Rp):", self.diskon_tambahan_debit)

        # nilai_ppn =  str(get_ppn_from_profile(get_db_path()))
        form_debit.addRow(f"Nilai PPn {self.nilai_ppn}%:", self.ppn_debit)
        # form_debit.addRow("Diskon Member (%):", self.ppn_debit)
        form_debit.addRow("Total Bayar:", self.input_total_harus_dibayar_debit)
        form_debit.addRow("No. Kartu:", self.input_no_kartu_debit)
        form_debit.addRow("Approval Code:", self.input_approval_debit)

        debit_inner_layout = QGridLayout()
        debit_inner_layout.addLayout(form_debit, 0, 0)

        jenis_debit = QGroupBox("Jenis Debit Card")
        jenis_debit_layout = QVBoxLayout()

        # Ambil daftar debit card dari query
        debit_names = get_debit_card_names()

        # Simpan radio button supaya bisa diakses nanti
        self.radio_debit_cards = []

        for idx, debit_name in enumerate(debit_names):
            radio_btn = QRadioButton(debit_name)
            if idx == 0:  # Default pilih pertama
                radio_btn.setChecked(True)
            jenis_debit_layout.addWidget(radio_btn)
            self.radio_debit_cards.append(radio_btn)

        jenis_debit.setLayout(jenis_debit_layout)
        debit_inner_layout.addWidget(jenis_debit, 0, 1)

        receive_debit = QGroupBox("Receive on Account")
        receive_debit_layout = QVBoxLayout()

        # Ambil daftar receive on account dari query
        receive_names = get_receive_on_account_debit()

        # Simpan radio button untuk akses nanti
        self.radio_receive_debit = []

        for idx, receive_name in enumerate(receive_names):
            radio_btn = QRadioButton(receive_name)
            if idx == 0:  # default pilih pertama
                radio_btn.setChecked(True)
            receive_debit_layout.addWidget(radio_btn)
            self.radio_receive_debit.append(radio_btn)

        receive_debit.setLayout(receive_debit_layout)
        debit_inner_layout.addWidget(receive_debit, 0, 2)


        self.groupbox_debit.setLayout(debit_inner_layout)

        # === Stack Layout
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.groupbox_tunai)
        self.stacked_layout.addWidget(self.groupbox_credit)
        self.stacked_layout.addWidget(self.groupbox_debit)

        # Radio kontrol
        # self.radio_tunai.toggled.connect(self.update_stacked_layout)
        # self.radio_credit.toggled.connect(self.update_stacked_layout)
        # self.radio_debit.toggled.connect(self.update_stacked_layout)
        # Tambahkan koneksi dengan parameter checked
        self.radio_tunai.toggled.connect(lambda checked: self.update_stacked_layout("tunai") if checked else None)
        self.radio_credit.toggled.connect(lambda checked: self.update_stacked_layout("credit") if checked else None)
        self.radio_debit.toggled.connect(lambda checked: self.update_stacked_layout("debit") if checked else None)

        metode_dan_form = QHBoxLayout()
        metode_dan_form.addWidget(metode_group)
        metode_dan_form.addLayout(self.stacked_layout)
        self.main_layout.addLayout(metode_dan_form)

        # === Tombol
        tombol_layout = QHBoxLayout()
        self.batal_btn = QPushButton("Batal")
        self.batal_btn.setStyleSheet("""
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
        self.ok_btn = QPushButton("Lanjutkan Pembayaran")
        self.ok_btn.setStyleSheet("""
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
        self.batal_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.on_ok_pressed)
        tombol_layout.addStretch()
        tombol_layout.addWidget(self.batal_btn)
        tombol_layout.addWidget(self.ok_btn)

        self.main_layout.addLayout(tombol_layout)
        self.setLayout(self.main_layout)
        # self.input_total_tunai.setReadOnly(True) # bisa jalan

    def atur_style_form(self):
        print('masuk atur style')

        from utils.myhelper import set_readonly_style  # jika helper-nya kamu simpan di file terpisah
        set_readonly_style(self.input_total_tunai, True)
        print(type(self.input_total_tunai), self.input_total_tunai.isEnabled(), getattr(self.input_total_tunai, 'isReadOnly', lambda: 'n/a')())

        set_readonly_style(self.diskon_tambahan_tunai, False)
        print(type(self.diskon_tambahan_tunai), self.diskon_tambahan_tunai.isEnabled(), getattr(self.diskon_tambahan_tunai, 'isReadOnly', lambda: 'n/a')())

        set_readonly_style(self.ppn_tunai, True)
        set_readonly_style(self.input_total_harus_dibayar_tunai, True)
        set_readonly_style(self.input_bayar_tunai, False)
        set_readonly_style(self.input_kembalian_tunai, True)



    def update_stacked_layout(self, mode):
        if mode == "tunai":
            self.stacked_layout.setCurrentWidget(self.groupbox_tunai)
            self.controller.cek_radiobutton("tunai")
        elif mode == "credit":
            self.stacked_layout.setCurrentWidget(self.groupbox_credit)
            self.controller.cek_radiobutton("credit")
        elif mode == "debit":
            self.stacked_layout.setCurrentWidget(self.groupbox_debit)
            self.controller.cek_radiobutton("debit")


    def on_ok_pressed(self):
        jumlah_dibayar = self.controller.parse_rupiah(self.input_bayar_tunai.text())
        total_dibayar = self.controller.parse_rupiah(self.input_total_harus_dibayar_tunai.text())


        if jumlah_dibayar < total_dibayar:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Pembayaran Tidak Cukup", "Uang yang dibayarkan tidak boleh lebih kecil dari total yang harus dibayar.")
            return  # ❌ batalkan proses lanjut

        result = self.controller.get_payment_result()
        if result:
            self.controller.result = result
            self.accept()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Pembayaran Gagal", "Input belum lengkap atau invalid.")
            
    def format_rupiah(self, angka: float) -> str:
        """Mengubah angka float ke format rupiah lokal seperti 12.345,67"""
        return f"{angka:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

