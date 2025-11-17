from views.pembayaran_view import PembayaranView
from models.pembayaran_model import PembayaranModel,PaymentResult
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QFormLayout, QGroupBox, QRadioButton, QGridLayout
# import sip
from collections import namedtuple
from utils.db_helper import get_ppn_from_profile,parse_int_safely  # jika kamu buat di file terpisah
from utils.path_utils import get_db_path 

PaymentResult = namedtuple("PaymentResult", [
    "metode", "jumlah_dibayar", "diskon_rp", "diskon_member_persen",
    "total_dibayar", "kembali", "kartu", "approval_code",
    "jenis_edc", "jenis_kartu"
])

class PembayaranController:
    def __init__(self, parent=None, info_transaksi=None):
        self.result = None  # untuk menyimpan hasil
        self.form_state = {
            "tunai": {},
            "credit": {},
            "debit": {}
        }

        self.model = PembayaranModel()
        if info_transaksi:
            self.model.info_transaksi = info_transaksi
        # self.view = PembayaranView(self, parent)
        # self.update_info_label()
        self.view = PembayaranView(self, parent)
        self.update_info_label()
        # self.show_tunai_form()  # ✅ dipanggil di sini, setelah self.view ada
        # self.cek_radiobutton()
        # Setelah self.view dibuat
        self.view.stacked_layout.setCurrentWidget(self.view.groupbox_tunai)
        self.show_tunai_form()

    

    def show(self):
        return self.view.exec()
    

    def get_payment_result(self):
        view = self.view
        if not hasattr(view, "input_bayar_tunai"):
            print("❌ input_bayar_tunai belum ada!")
        print("input bayar:", view.input_bayar_tunai.text())
        print("harus bayar:", view.input_total_harus_dibayar_tunai.text())
    #     def proses_pembayaran(self):
    # kode_voucher = self.view.voucher_input.text().strip()
    # nilai_voucher = 0

    # if kode_voucher:
    #     result = self.model.cek_voucher_valid(kode_voucher)
    #     if result:
    #         nilai_voucher = result["nilai"]
    #     else:
    #         QMessageBox.warning(None, "Voucher Tidak Valid", "Kode voucher tidak ditemukan atau sudah digunakan.")
    #         return

    # total_tagihan = self.model.hitung_total_setelah_diskon()
    # total_bayar = total_tagihan - nilai_voucher
        if view.radio_tunai.isChecked():
            try:
                jumlah_dibayar = self.parse_rupiah(view.input_bayar_tunai.text())
                total_dibayar = self.parse_rupiah(view.input_total_harus_dibayar_tunai.text())
                kembali = jumlah_dibayar - total_dibayar
                # return PaymentResult(
                #     metode="tunai",
                #     jumlah_dibayar=jumlah_dibayar,
                #     diskon_rp=int(view.diskon_tambahan_tunai.text()),
                #     diskon_member_persen=float(view.diskon_persen_member_tunai.text()),
                #     total_dibayar=total_dibayar,
                #     kembali=kembali,
                #     kartu=None,
                #     approval_code=None,
                #     jenis_edc=None,
                #     jenis_kartu=None
                # )
                return PaymentResult(
                    metode="tunai",
                    jumlah_dibayar=jumlah_dibayar,
                    diskon_rp=int(view.diskon_tambahan_tunai.value()),
                    diskon_member_persen=int(self.view.diskon_tambahan_tunai.value()),
                    total_dibayar=total_dibayar,
                    kembali=kembali,
                    kartu=None,
                    approval_code=None,
                    jenis_edc=None,
                    jenis_kartu=None
                )
            except Exception as e:
                print("❌ Validasi tunai gagal:", e)
                return None

        elif view.radio_credit.isChecked():
            try:
                # cara tahu user pilih radio credit yang mana
                selected_card = None
                for btn in self.view.radio_credit_cards:
                    if btn.isChecked():
                        selected_card = btn.text()
                        break
                print("Jenis kartu dipilih:", selected_card)
                jenis_kartu = selected_card

                # jenis_kartu = "Visa" if view.radio_visa_credit.isChecked() else "Master"
                # cara tahu user pilih edc yang mana
                selected_receive = None
                for btn in self.view.radio_receive_accounts:
                    if btn.isChecked():
                        selected_receive = btn.text()
                        break
                print("Receive on Account dipilih:", selected_receive)
                jenis_edc = selected_receive

                # jenis_edc = "#EDC1" if view.radio_edc1_credit.isChecked() else "#EDC2"
                return PaymentResult(
                    metode="kredit",
                    jumlah_dibayar=self.parse_rupiah(view.input_total_credit.text()),
                    diskon_rp=parse_int_safely(view.diskon_tambahan_credit.text()),

                    # diskon_rp=int(view.diskon_tambahan_credit.text()),
                    diskon_member_persen=int(self.view.diskon_tambahan_credit.value()) ,
                    total_dibayar=self.parse_rupiah(view.input_total_harus_dibayar_credit.text()),
                    kembali=0,
                    kartu=view.input_no_kartu_credit.text(),
                    approval_code=view.input_approval_credit.text(),
                    jenis_edc=jenis_edc,
                    jenis_kartu=jenis_kartu
                )
            except Exception as e:
                print("❌ Validasi credit gagal:", e)
                return None

        elif view.radio_debit.isChecked():
            try:
                # if view.radio_mandiri.isChecked():
                #     jenis_kartu = "Mandiri"
                # elif view.radio_bca.isChecked():
                #     jenis_kartu = "BCA"
                # else:
                #     jenis_kartu = "Prima"
                selected_debit = None
                for btn in self.view.radio_debit_cards:
                    if btn.isChecked():
                        selected_debit = btn.text()
                        break
                print("Debit Card dipilih:", selected_debit)
                jenis_kartu = selected_debit

                selected_receive = None
                for btn in self.view.radio_receive_debit:
                    if btn.isChecked():
                        selected_receive_debit = btn.text()
                        break
                print("Receive on Account Debit dipilih:", selected_receive_debit)
                jenis_edc = selected_receive_debit


                # jenis_edc = "#EDC1" if view.radio_edc1_debit.isChecked() else "#EDC2"

                return PaymentResult(
                    metode="debit",
                    jumlah_dibayar=self.parse_rupiah(view.input_total_debit.text()),
                    diskon_rp=parse_int_safely(view.diskon_tambahan_debit.text()),
                    diskon_member_persen=int(self.view.diskon_tambahan_debit.value()),
                    total_dibayar=self.parse_rupiah(view.input_total_harus_dibayar_debit.text()),
                    kembali=0,
                    kartu=view.input_no_kartu_debit.text(),
                    approval_code=view.input_approval_debit.text(),
                    jenis_edc=jenis_edc,
                    jenis_kartu=jenis_kartu
                )
            except Exception as e:
                print("❌ Validasi debit gagal:", e)
                return None

        return None
    
    def show(self):
        return self.view.exec()


    # def parse_rupiah(self, text: str) -> int:
    #     text = text.replace(".", "").replace(",", "").replace("Rp", "").strip()
    #     return int(text) if text.isdigit() else 0
    # def parse_rupiah(self, text):
    #     text = text.strip().replace(".", "").replace(",00", "")
    #     return int(text or 0)  # agar tidak error jika kosong
    # def parse_rupiah(self, text: str) -> float:
    #     """
    #     Membersihkan teks rupiah dan mengubah ke float.
    #     Contoh: '4.015,00' -> 4015.0
    #     """
    #     if not text:
    #         return 0.0
    #     try:
    #         cleaned = text.replace(".", "").replace(",00", ".")
    #         return float(cleaned)
    #     except Exception as e:
    #         print(f"❌ Error parse_rupiah: {e}")
    #         return 0.0
    # terakhir
    # def parse_rupiah(self, text: str) -> float:
    #     """
    #     Membersihkan teks rupiah dan mengubah ke float.
    #     Contoh: '4.015,00' -> 4015.0
    #     """
    #     if not text:
    #         return 0.0
    #     try:
    #         cleaned = text.replace(".", "").replace(",", ".")
    #         return float(cleaned)
    #     except Exception as e:
    #         print(f"❌ Error parse_rupiah: {e} | raw: {text}")
    #         return 0.0
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

    def update_info_label(self):
        info = self.model.info_transaksi
        self.view.label_tanggal.setText(info.tanggal)
        self.view.label_jenis.setText(str(info.jenis_item))
        self.view.label_qty.setText(str(info.total_qty))
        self.view.label_total.setText(f"{info.total_belanja:,.0f}")

    # def cek_radiobutton(self):
    def cek_radiobutton(self, mode: str):
        print(f"[DEBUG] Cek radiobutton untuk mode: {mode}")
        if mode == "tunai":
            self.show_tunai_form()
        elif mode == "credit":
            self.show_credit_form()
        elif mode == "debit":
            self.show_debit_form()

    def show_credit_form(self):
        print('masuk ke show credit')
        state = self.form_state.get("credit", {})

        # Ambil total dari model
        total_awal = self.model.info_transaksi.total_belanja
        total_text = self.view.format_rupiah(total_awal)

        self.view.input_total_credit.setText(total_text)
        # self.view.diskon_tambahan_credit.setText(state.get("diskon", "0"))
        
        # self.view.ppn_credit.setText(state.get("ppn", "10"))  # default PPN 10%

        # Ambil nilai PPN dari DB
        ppn_value = get_ppn_from_profile(get_db_path()) # state.get("ppn") or get_ppn_from_profile(self.db_path)
        print(f'nilai ppn = {ppn_value}')
        self.view.ppn_credit.setText(ppn_value)

        self.view.input_no_kartu_credit.setText("")
        self.view.input_approval_credit.setText("")

        # Bind event textChanged
        self.view.diskon_tambahan_credit.textChanged.connect(self.hitung_total_harus_dibayar_credit)
        self.view.ppn_credit.textChanged.connect(self.hitung_total_harus_dibayar_credit)

        # Hitung awal
        self.hitung_total_harus_dibayar_credit()
        self.view.diskon_tambahan_credit.setFocus()

    def show_debit_form(self):
        print('masuk ke show debit')
        state = self.form_state.get("debit", {})

        # Ambil total dari model
        total_awal = self.model.info_transaksi.total_belanja
        total_text = self.view.format_rupiah(total_awal)

        self.view.input_total_debit.setText(total_text)
        # self.view.diskon_tambahan_debit.setText(state.get("diskon", "0"))
        
        # Ambil nilai PPN dari DB
        ppn_value = get_ppn_from_profile(get_db_path()) # state.get("ppn") or get_ppn_from_profile(self.db_path)
        self.view.ppn_debit.setText(ppn_value)
        # self.view.ppn_debit.setText(state.get("ppn", "10"))  # default PPN 10%

        self.view.input_no_kartu_debit.setText("")
        self.view.input_approval_debit.setText("")

        # Bind event textChanged
        
        self.view.diskon_tambahan_debit.textChanged.connect(self.hitung_total_harus_dibayar_debit)
        self.view.ppn_debit.textChanged.connect(self.hitung_total_harus_dibayar_debit)

        # Hitung awal
        self.hitung_total_harus_dibayar_debit()
        self.view.diskon_tambahan_debit.setFocus()



    def show_tunai_form(self):

        print('masuk ke show tunai')
        # # atur_style_form_tunai() 
        # self.atur_style_form_tunai()

        state = self.form_state.get("tunai", {})

        total_awal = self.model.info_transaksi.total_belanja
        total_text = self.view.format_rupiah(total_awal)

        self.view.input_total_tunai.setText(total_text)
        
        # Ambil nilai PPN dari DB
        ppn_value = get_ppn_from_profile(get_db_path()) # state.get("ppn") or get_ppn_from_profile(self.db_path)
        self.view.ppn_tunai.setText(ppn_value)
        # self.view.ppn_tunai.setText(state.get("ppn", "10"))  # default PPN 10%
        
        self.view.input_kembalian_tunai.setText("")
        self.view.input_total_harus_dibayar_tunai.setText("")

        # Bind event textChanged
        # self.view.diskon_tambahan_tunai.textChanged.connect(self.hitung_total_harus_dibayar)
        self.view.diskon_tambahan_tunai.valueChanged.connect(self.hitung_total_harus_dibayar)

        # self.view.ppn_tunai.textChanged.connect(self.hitung_total_harus_dibayar)
        self.view.input_bayar_tunai.textChanged.connect(self.hitung_kembalian_otomatis)

        self.hitung_total_harus_dibayar()
        self.view.input_bayar_tunai.setFocus()

    def hitung_total_harus_dibayar_debit(self):
        try:
            # total = self.parse_rupiah(self.view.input_total_debit.text())
            # diskon_persen = float(self.view.diskon_tambahan_debit.text().replace(",", ".") or 0)
            # diskon_nilai = int(total * diskon_persen / 100)
            # # ppn_persen = float(self.view.ppn_debit.text().replace(".","").replace(",","") ) 
            # ppn_nilai = total * 0.1
            # total_nilai = total - diskon_nilai + ppn_nilai
            # self.view.ppn_debit.setText(self.view.format_rupiah(ppn_nilai))
            # print(f'diskon = {diskon_nilai}, ppn nilai {ppn_nilai}')
            # self.view.input_total_harus_dibayar_debit.setText(self.view.format_rupiah(total_nilai))

            total = self.parse_rupiah(self.view.input_total_debit.text())
            diskon_persen = self.view.diskon_tambahan_debit.value()
            diskon_nilai = int(total * diskon_persen / 100)
            
            
            # Ambil nilai PPN dari DB
            ppn_value = int(get_ppn_from_profile(get_db_path())) # state.get("ppn") or get_ppn_from_profile(self.db_path)
            ppn_nilai = (total-diskon_nilai) * (ppn_value / 100 ) # 0.1
            total_nilai = total - diskon_nilai #+ ppn_nilai
            self.view.ppn_debit.setText(self.view.format_rupiah(ppn_nilai))
            print(f'diskon % = {diskon_persen}, ppn nilai {ppn_nilai}')
            self.view.input_total_harus_dibayar_debit.setText(self.view.format_rupiah(total_nilai))

        except Exception as e:
            print("❌ Error hitung_total_harus_dibayar_debit:", e)
            self.view.input_total_harus_dibayar_debit.setText("0")

    def hitung_total_harus_dibayar_credit(self):
        try:

            # total = self.parse_rupiah(self.view.input_total_credit.text())
            # diskon_persen = float(self.view.diskon_tambahan_credit.text().replace(",", ".") or 0)
            # diskon_nilai = int(total * diskon_persen / 100)
            # ppn_persen = self.parse_rupiah(self.view.ppn_credit.text()) 
            # ppn_nilai = total * ppn_persen / 100
            # total_nilai = total - diskon_nilai + ppn_nilai
            # self.view.ppn_credit.setText(self.view.format_rupiah(ppn_nilai))

            # self.view.input_total_harus_dibayar_credit.setText(self.view.format_rupiah(total_nilai))

            total = self.parse_rupiah(self.view.input_total_credit.text())
            diskon_persen = self.view.diskon_tambahan_credit.value()
            diskon_nilai = int(total * diskon_persen / 100)
            # Ambil nilai PPN dari DB
            ppn_value = int(get_ppn_from_profile(get_db_path())) # state.get("ppn") or get_ppn_from_profile(self.db_path)
            ppn_nilai = (total-diskon_nilai) * (ppn_value / 100 ) # 0.1
            # ppn_nilai = (total-diskon_nilai) * 0.1
            total_nilai = total - diskon_nilai #+ ppn_nilai
            self.view.ppn_credit.setText(self.view.format_rupiah(ppn_nilai))
            print(f'diskon % = {diskon_persen}, ppn nilai {ppn_nilai}')
            self.view.input_total_harus_dibayar_credit.setText(self.view.format_rupiah(total_nilai))



        except Exception as e:
            print("❌ Error hitung_total_harus_dibayar_credit:", e)
            self.view.input_total_harus_dibayar_credit.setText("0")

    def hitung_total_harus_dibayar(self):
        try:
            # total = self.model.info_transaksi.total_belanja

            # diskon_persen = float(self.view.diskon_tambahan_tunai.text().replace(",", ".") or 0)
            # diskon_nilai = int(total * diskon_persen / 100)

            # ppn_persen = float(self.view.ppn_tunai.text().replace(",", ".") or 0)
            # ppn_nilai = int((total - diskon_nilai) * ppn_persen / 100)

            # total_final = total - diskon_nilai + ppn_nilai
            # if total_final < 0:
            #     total_final = 0

            # self.view.ppn_tunai.setText(self.view.format_rupiah(ppn_nilai))

            # self.view.input_total_harus_dibayar_tunai.setText(self.view.format_rupiah(total_final))
            # self.view.input_bayar_tunai.setText(self.view.format_rupiah(total_final))
            
            total = self.parse_rupiah(self.view.input_total_tunai.text())
            diskon_persen = self.view.diskon_tambahan_tunai.value()
            diskon_nilai = int(total * diskon_persen / 100)
            # Ambil nilai PPN dari DB
            ppn_value = int(get_ppn_from_profile(get_db_path())) # state.get("ppn") or get_ppn_from_profile(self.db_path)
            ppn_nilai = (total-diskon_nilai) * (ppn_value / 100 ) # 0.1
            # ppn_nilai = (total-diskon_nilai) * 0.1
            total_nilai = total - diskon_nilai #+ ppn_nilai
            self.view.ppn_tunai.setText(self.view.format_rupiah(ppn_nilai))
            print(f'diskon % = {diskon_persen}, ppn nilai {ppn_nilai}, total nilai = {total_nilai}')
            self.view.input_total_harus_dibayar_tunai.setText(self.view.format_rupiah(total_nilai))
            
            
            self.view.input_bayar_tunai.setText(self.view.format_rupiah(total_nilai))
            
        except Exception as e:
            print("❌ Error hitung total harus dibayar:", e)
            self.view.input_total_harus_dibayar_tunai.setText("0")

        self.hitung_kembalian_otomatis()

    # def hitung_kembalian_otomatis(self):
    #     try:
    #         bayar = self.parse_rupiah(self.view.input_bayar_tunai.text()) #int(self.view.input_bayar_tunai.text().replace(".", "").replace(",00", "") or 0)
    #         harus_bayar = self.parse_rupiah(self.view.input_total_harus_dibayar_tunai.text()) #int(self.view.input_total_harus_dibayar_tunai.text().replace(".", "").replace(",00", "") or 0)
    #         kembali = bayar - harus_bayar
    #         self.view.input_kembalian_tunai.setText(self.view.format_rupiah(kembali))
    #     except Exception as e:
    #         print("❌ Error hitung kembalian:", e)
    #         self.view.input_kembalian_tunai.setText("0")
    def hitung_kembalian_otomatis(self):
        try:
            bayar = self.parse_rupiah(self.view.input_bayar_tunai.text())
            harus_bayar = self.parse_rupiah(self.view.input_total_harus_dibayar_tunai.text())
            print(f"input bayar: {bayar}")
            print(f"harus bayar: {harus_bayar}")
            kembali = bayar - harus_bayar
            self.view.input_kembalian_tunai.setText(self.view.format_rupiah(kembali))
        except Exception as e:
            print("❌ Error hitung kembalian:", e)
            self.view.input_kembalian_tunai.setText("0")


