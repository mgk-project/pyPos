# settlement_checker.py
import requests
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QSpinBox, QHeaderView, QDialog,
    QFormLayout, QDialogButtonBox, QCheckBox, QFrame, QAbstractItemView,
    QCompleter ,QPlainTextEdit,QRadioButton,QGroupBox, QMessageBox
)
import sqlite3

class SettlementChecker(QThread):
    hasil_cek = Signal(list)

    def run(self):
        try:
            response = requests.get("http://localhost:5000/cek_transaksi_settlement")
            print(f'hasil kembalian = {response.status_code}') 
            if response.status_code == 200:
                data = response.json()
                print(f'data = {data}') 
                self.hasil_cek.emit(data)
            else:
                self.hasil_cek.emit([])
        except Exception as e:
            print(f"Error saat memeriksa settlement: {e}")
            self.hasil_cek.emit([])


class SettlementHandler:
    def __init__(self, form_widget: QWidget, transaksi_modal: QDialog):
        self.form_widget = form_widget
        self.transaksi_modal = transaksi_modal

    def cek_transaksi_settlement(self):
        try:
            from utils.path_utils import get_db_path
            conn = sqlite3.connect(get_db_path())
            print("DB Path:", get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
                SELECT * FROM transaksi_copy 
                WHERE jenis_label = 'invoice' 
                AND settlement_id = 1 
                AND datetime(dtime, '+10 hours') < datetime('now')
            """
            cursor.execute(query)
            hasil = cursor.fetchall()

            # Konversi hasil ke list of dict agar bisa diolah
            result = [dict(row) for row in hasil]
            return result

        except sqlite3.Error as db_err:
            print(f"Kesalahan koneksi atau query SQLite: {db_err}", flush=True)
            return []  # Kembalikan list kosong agar tidak error di len(data)

        finally:
            cursor.close()
            conn.close()

    def cek_status_settlement(self):
        data = self.cek_transaksi_settlement()
        self.settlement_result(data)

    def settlement_result(self, data):
        print(f'masuk settlement result , jumlah data = {len(data)}')
        if len(data) > 0:
            self.transaksi_modal.exec()
            # self.load_master_transaksi()
            self.nonaktifkan_form()
            QMessageBox.warning(
                self.form_widget,
                "Perhatian",
                "Ada transaksi yang belum diselesaikan. Silakan selesaikan terlebih dahulu."
            )
        else:
            self.aktifkan_form()

    def nonaktifkan_form(self):
        widget_types = [QLineEdit, QComboBox, QPushButton]
        for widget_type in widget_types:
            for widget in self.form_widget.findChildren(widget_type):
                widget.setEnabled(False)

    def aktifkan_form(self):
        widget_types = [QLineEdit, QComboBox, QPushButton]
        for widget_type in widget_types:
            for widget in self.form_widget.findChildren(widget_type):
                widget.setEnabled(True)