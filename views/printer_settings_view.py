from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QLabel, QComboBox, QLineEdit, QCheckBox, QMessageBox
)
from PySide6.QtPrintSupport import QPrinterInfo
from controllers.printer_settings_controller import PrinterSettingsController


class AddPrinterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Printer")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Nama Printer"))
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        for info in QPrinterInfo.availablePrinters():
            self.name_combo.addItem(info.printerName())
        layout.addWidget(self.name_combo)

        layout.addWidget(QLabel("Ukuran Kertas"))
        self.paper_combo = QComboBox()
        # Tambahkan 56mm sesuai kebutuhan
        self.paper_combo.addItems(["56mm", "58mm", "80mm", "100x150mm"])
        layout.addWidget(self.paper_combo)

        self.default_check = QCheckBox("Jadikan default")
        layout.addWidget(self.default_check)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Simpan")
        cancel_btn = QPushButton("Batal")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return {
            "name": self.name_combo.currentText(),
            "paper_size": self.paper_combo.currentText(),
            "default": self.default_check.isChecked(),
        }


# class PrinterSettingsView(QDialog):
#     def __init__(self, controller: PrinterSettingsController, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Pengaturan Printer")
#         self.controller = controller
#         self.resize(420, 320)

#         layout = QVBoxLayout(self)
#         self.list_widget = QListWidget()
#         layout.addWidget(self.list_widget)

#         btn_layout = QHBoxLayout()
#         add_btn = QPushButton("Tambah")
#         default_btn = QPushButton("Set Default")
#         remove_btn = QPushButton("Hapus")
#         test_btn = QPushButton("Tes Print")
#         preview_btn = QPushButton("Preview")
#         btn_layout.addWidget(add_btn)
#         btn_layout.addWidget(default_btn)
#         btn_layout.addWidget(remove_btn)
#         btn_layout.addWidget(test_btn)
#         btn_layout.addWidget(preview_btn)
#         layout.addLayout(btn_layout)

#         add_btn.clicked.connect(self.add_printer)
#         default_btn.clicked.connect(self.set_default)
#         remove_btn.clicked.connect(self.remove_printer)
#         test_btn.clicked.connect(self.test_print)
#         preview_btn.clicked.connect(self.preview_print)

#         self.load_printers()
from PySide6.QtWidgets import QRadioButton, QGroupBox, QFormLayout
import csv, os

class PrinterSettingsView(QDialog):
    def __init__(self, controller: PrinterSettingsController, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pengaturan Printer")
        self.controller = controller
        self.resize(420, 420)

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # === Tombol dasar ===
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Tambah")
        default_btn = QPushButton("Set Default")
        remove_btn = QPushButton("Hapus")
        test_btn = QPushButton("Tes Print")
        preview_btn = QPushButton("Preview")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(default_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(preview_btn)
        layout.addLayout(btn_layout)

        add_btn.clicked.connect(self.add_printer)
        default_btn.clicked.connect(self.set_default)
        remove_btn.clicked.connect(self.remove_printer)
        test_btn.clicked.connect(self.test_print)
        preview_btn.clicked.connect(self.preview_print)

        # === Pilihan Mode Cetak ===
        self.group_mode = QGroupBox("Mode Cetak Struk")
        mode_layout = QFormLayout()
        self.radio_preview = QRadioButton("Tampilkan Preview Dulu")
        self.radio_autoprint = QRadioButton("Langsung Auto Print")
        mode_layout.addRow(self.radio_preview)
        mode_layout.addRow(self.radio_autoprint)
        self.group_mode.setLayout(mode_layout)
        layout.addWidget(self.group_mode)

        # Tombol Simpan Pengaturan
        simpan_btn = QPushButton("Simpan Mode Cetak")
        layout.addWidget(simpan_btn)
        simpan_btn.clicked.connect(self.simpan_mode_cetak)

        self.load_printers()
        self.load_print_mode()

    # ------------------------------------------------------------------
    def load_print_mode(self):
        """Baca mode cetak dari setting_struk.csv"""
        csv_path = os.path.join(os.path.dirname(__file__), "..", "resources", "setting_struk.csv")
        csv_path = os.path.abspath(csv_path)
        mode = "preview"  # default
        if os.path.exists(csv_path):
            with open(csv_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("print_mode"):
                        parts = line.strip().split(",", 1)
                        if len(parts) == 2:
                            mode = parts[1].strip().lower()
                        break
        if mode == "auto":
            self.radio_autoprint.setChecked(True)
        else:
            self.radio_preview.setChecked(True)

    def simpan_mode_cetak(self):
        """Simpan pilihan ke setting_struk.csv"""
        csv_path = os.path.join(os.path.dirname(__file__), "..", "resources", "setting_struk.csv")
        csv_path = os.path.abspath(csv_path)

        # pastikan file ada
        if not os.path.exists(csv_path):
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write("print_mode,preview\n")

        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        found = False
        for line in lines:
            if line.strip().startswith("print_mode"):
                mode = "auto" if self.radio_autoprint.isChecked() else "preview"
                new_lines.append(f"print_mode,{mode}\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            mode = "auto" if self.radio_autoprint.isChecked() else "preview"
            new_lines.append(f"print_mode,{mode}\n")

        with open(csv_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        QMessageBox.information(self, "Sukses", "Mode cetak berhasil disimpan!")

    def load_printers(self):
        self.list_widget.clear()
        for p in self.controller.get_printers():
            text = f"{p['name']} ({p['paper_size']})"
            if p.get('default'):
                text += " [default]"
            self.list_widget.addItem(text)

    def add_printer(self):
        dlg = AddPrinterDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            # Validasi ringan
            name = (data.get("name") or "").strip()
            paper_size = (data.get("paper_size") or "").strip()
            is_default = bool(data.get("default"))
            if not name or not paper_size:
                QMessageBox.warning(self, "Data tidak lengkap", "Nama printer dan ukuran kertas wajib diisi.")
                return
            # Kirim ke controller
            self.controller.add_printer(name, paper_size, is_default)
            self.load_printers()

    def set_default(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.controller.set_default(row)
            self.load_printers()

    def remove_printer(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.controller.remove_printer(row)
            self.load_printers()

    def test_print(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            result = self.controller.test_print(row)
            msg = QMessageBox(self)
            if result:
                msg.setIcon(QMessageBox.Information)
                msg.setText("Tes print berhasil")
            else:
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Tes print gagal")
            msg.exec()

    def preview_print(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.controller.preview_print(row, self)
