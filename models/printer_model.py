# import sqlite3
# models/printer_model.py
# import sqlite3
# from escpos.printer import Usb, Network
# import usb.core, usb.util
# from utils.path_utils import get_db_path

# models/printer_model.py
import sqlite3
from escpos.printer import Usb, Network
import usb.core
from utils.path_utils import get_db_path

class PrinterModel:
    def __init__(self, db_path=get_db_path()):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        """Buat tabel jika belum ada"""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS printer_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT,
                koneksi TEXT,
                address TEXT,
                lebar_kertas TEXT,
                margin INTEGER DEFAULT 0,
                driver TEXT DEFAULT 'escpos',
                auto_cut INTEGER DEFAULT 1,
                copies INTEGER DEFAULT 1,
                is_default INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def get_all(self):
        """Ambil semua printer dari database"""
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM printer_settings")
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_printer(self, data):
        """Tambah printer baru"""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO printer_settings 
            (nama, koneksi, address, lebar_kertas, margin, driver, auto_cut, copies, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("nama"), data.get("koneksi"), data.get("address"),
            data.get("lebar_kertas"), data.get("margin", 0),
            data.get("driver", "escpos"), data.get("auto_cut", 1),
            data.get("copies", 1), data.get("is_default", 0)
        ))
        conn.commit()
        conn.close()

    def update_printer(self, printer_id, data):
        """Update data printer"""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            UPDATE printer_settings SET 
                nama=?, koneksi=?, address=?, lebar_kertas=?, margin=?,
                driver=?, auto_cut=?, copies=?, is_default=?
            WHERE id=?
        """, (
            data.get("nama"), data.get("koneksi"), data.get("address"),
            data.get("lebar_kertas"), data.get("margin", 0),
            data.get("driver", "escpos"), data.get("auto_cut", 1),
            data.get("copies", 1), data.get("is_default", 0),
            printer_id
        ))
        conn.commit()
        conn.close()

    def delete_printer(self, printer_id):
        """Hapus printer"""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM printer_settings WHERE id=?", (printer_id,))
        conn.commit()
        conn.close()

    def set_default(self, printer_id):
        """Set printer sebagai default"""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("UPDATE printer_settings SET is_default=0")
        cur.execute("UPDATE printer_settings SET is_default=1 WHERE id=?", (printer_id,))
        conn.commit()
        conn.close()

    def get_default(self):
        """Ambil printer default"""
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM printer_settings WHERE is_default=1 LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def test_connection(self, koneksi, address):
        """
        Test koneksi printer dan kirim cetak dummy.
        koneksi: usb | lan
        address: "VID:PID" (untuk USB) atau "IP:PORT" (untuk LAN)
        """
        try:
            if koneksi.lower() == "usb":
                try:
                    vid, pid = address.split(":")
                    vid, pid = int(vid, 16), int(pid, 16)
                except Exception:
                    return False, "❌ Format USB harus 'VID:PID' (hex)"

                dev = usb.core.find(idVendor=vid, idProduct=pid)
                if dev is None:
                    return False, f"❌ Printer USB tidak ditemukan (VID={hex(vid)} PID={hex(pid)})"

                printer = Usb(vid, pid)
                printer.text("=== TEST PRINT USB ===\n")
                printer.text("Berhasil terkoneksi via USB!\n\n")
                printer.cut()
                return True, "✅ Test print USB berhasil"

            elif koneksi.lower() == "lan":
                try:
                    ip, port = address.split(":")
                    port = int(port)
                except Exception:
                    return False, "❌ Format LAN harus 'IP:PORT'"

                printer = Network(ip, port=port, timeout=3)
                printer.text("=== TEST PRINT LAN ===\n")
                printer.text("Berhasil terkoneksi via Network!\n\n")
                printer.cut()
                return True, "✅ Test print LAN berhasil"

            else:
                return False, f"❌ Jenis koneksi '{koneksi}' belum didukung"

        except Exception as e:
            return False, f"❌ Gagal konek printer: {str(e)}"

# class PrinterModel:

#     def __init__(self, db_path=get_db_path()):
#         self.db_path = db_path
#         # self.conn = None

# # class PrinterModel:
# #     def __init__(self, db_path):
# #         self.db_path = db_path
#     def close(self):
#         if self.conn:
#             self.conn.close()
#             self.conn = None

#     def connect(self):
#         return sqlite3.connect(self.db_path)

#     def get_all(self):
#         conn = self.connect()
#         conn.row_factory = sqlite3.Row
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM printer_settings")
#         rows = cur.fetchall()
#         conn.close()
#         return [dict(r) for r in rows]

#     def add_printer(self, data):
#         conn = self.connect()
#         cur = conn.cursor()
#         cur.execute("""
#             INSERT INTO printer_settings 
#             (nama, koneksi, address, lebar_kertas, margin, driver, auto_cut, copies, is_default)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """, (
#             data["nama"], data["koneksi"], data.get("address"), data["lebar_kertas"],
#             data.get("margin", 0), data.get("driver", "escpos"),
#             data.get("auto_cut", 1), data.get("copies", 1), data.get("is_default", 0)
#         ))
#         conn.commit()
#         conn.close()

#     def set_default(self, printer_id):
#         conn = self.connect()
#         cur = conn.cursor()
#         cur.execute("UPDATE printer_settings SET is_default=0")
#         cur.execute("UPDATE printer_settings SET is_default=1 WHERE id=?", (printer_id,))
#         conn.commit()
#         conn.close()

 

#     def connect_db(self):
#         return sqlite3.connect(self.db_path)

#     def test_printer_connection(self, printer_config: dict) -> tuple:
#         """
#         Test koneksi printer dan kirim cetak dummy.
#         printer_config contoh:
#         {
#             "nama": "Eppos Kasir",
#             "type": "usb" | "network",
#             "vid": "0x04b8",
#             "pid": "0x0202",
#             "ip": "192.168.1.100",
#             "port": 9100
#         }
#         return (True/False, pesan)
#         """
#         try:
#             if printer_config["type"].lower() == "usb":
#                 vid = int(printer_config.get("vid", "0x0"), 16)
#                 pid = int(printer_config.get("pid", "0x0"), 16)

#                 # cek apakah device ada
#                 dev = usb.core.find(idVendor=vid, idProduct=pid)
#                 if dev is None:
#                     return False, f"❌ Printer USB tidak ditemukan (VID={hex(vid)} PID={hex(pid)})"

#                 printer = Usb(vid, pid)
#                 printer.text("=== TEST PRINT ===\n")
#                 printer.text(f"Printer: {printer_config['nama']}\n")
#                 printer.text("Berhasil terkoneksi via USB!\n\n")
#                 printer.cut()
#                 return True, "✅ Test print USB berhasil"

#             elif printer_config["type"].lower() == "network":
#                 ip = printer_config.get("ip")
#                 port = int(printer_config.get("port", 9100))

#                 printer = Network(ip, port=port, timeout=3)
#                 printer.text("=== TEST PRINT ===\n")
#                 printer.text(f"Printer: {printer_config['nama']}\n")
#                 printer.text("Berhasil terkoneksi via Network!\n\n")
#                 printer.cut()
#                 return True, "✅ Test print Network berhasil"

#             else:
#                 return False, "❌ Jenis printer belum didukung"

#         except Exception as e:
#             return False, f"❌ Gagal konek printer: {str(e)}"


