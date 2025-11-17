import json
import os
# from utils.path_utils import get_db_path

class PrinterSettingsModel:
    """Model untuk menyimpan konfigurasi printer pada berkas JSON."""
# setting_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'setting_struk.csv')
    def __init__(self):
        base_dir =  os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(base_dir, '..', 'resources', 'printers.json')
        self.file_path = os.path.abspath(self.file_path)
        # self.file_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'printers.json')

        # Pastikan berkas konfigurasi ada
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as fh:
                json.dump({"printers": []}, fh, indent=2)

    # ------------------------------------------------------------------
    def load_printers(self):
        with open(self.file_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        return data.get('printers', [])

    def save_printers(self, printers):
        with open(self.file_path, 'w', encoding='utf-8') as fh:
            json.dump({"printers": printers}, fh, indent=2)

    # ------------------------------------------------------------------
    def add_printer(self, printer):
        printers = self.load_printers()
        printers.append(printer)
        self.save_printers(printers)

    def remove_printer(self, index):
        printers = self.load_printers()
        if 0 <= index < len(printers):
            printers.pop(index)
            self.save_printers(printers)

    def set_default(self, index):
        printers = self.load_printers()
        for i, p in enumerate(printers):
            p['default'] = i == index
        self.save_printers(printers)