from PySide6.QtCore import QObject, Signal
from models.sinkron_model import SinkronModel
from PySide6.QtWidgets import QMessageBox

class SinkronWorker(QObject):
    progress = Signal(int, str, str)  # percent, status, detail_log
    selesai = Signal(int)             # total rows updated
    gagal = Signal(str)

    def __init__(self, table_list):
        super().__init__()
        self.table_list = table_list

# run pakai api yang tersedia di server 
# class SinkronWorker(QObject):
#     ...
    def run(self):
        try:
            model = SinkronModel()
            updated_total = 0

            # 1) Cek update server
            check = model.check_update_server(machine_id="4CE9341348", cabang_id=101)
            print("[DEBUG] checkUpdate:", check)

            if check.get("row", 0) == 0:
                self.progress.emit(100, "Up-to-date", "Tidak ada data baru")
                self.selesai.emit(0)
                return

            # 2) Ambil data update
            sync = model.sync_data_server("4CE9341348", 101, self.table_list)
            for tbl in self.table_list:
                new_data = sync["data"].get(tbl, {}).get("new", [])
                updated = model.apply_sync_result(tbl, new_data)
                updated_total += updated
                self.progress.emit(
                    50, f"Sinkron {tbl}", f"{updated} baris diperbarui"
                )

            model.close_connections()
            self.selesai.emit(updated_total)

        except Exception as e:
            self.gagal.emit(str(e))

    # def run(self):
    #     try:
    #         model = SinkronModel()
    #         updated_total = 0
    #         for i, table in enumerate(self.table_list, 1):
    #             print(f'sinkron worker tabel ke-{i} , nama tabel = {table}')
    #             if not model.is_data_updated(table):
    #                 print('not model.is_data_updated{table}')
    #                 self.progress.emit(int(i / len(self.table_list) * 100),
    #                                 f"{table} up-to-date", "Lewati sinkron")
    #                 continue

    #             updated = model.sync_table_last_update(table)
    #             updated_total += updated
    #             self.progress.emit(
    #                 int(i / len(self.table_list) * 100),
    #                 f"Menyinkronkan {table}...",
    #                 f"{updated} baris disinkron"
    #             )
    #         model.close_connections()
    #         # QMessageBox.information(None, "Sinkronisasi Data", "Sinkronisasi data server-lokal selesai")
    #         print(f'DATA YANG DI SINKRON = {updated_total}')
    #         self.selesai.emit(updated_total)


    #         # total_updated = 0
    #         # jumlah_tabel = len(self.table_list)
    #         # for i, tabel in enumerate(self.table_list, 1):
    #         #     updated = model.sync_table_last_update(tabel)
    #         #     total_updated += updated
    #         #     persen = int(i / jumlah_tabel * 100)
    #         #     detail = f"{updated} baris disinkron"
    #         #     self.progress.emit(persen, f"Menyinkronkan {tabel}...", detail)
    #         # model.close_connections()
    #         # self.selesai.emit(total_updated)
    #     except Exception as e:
    #         # self.gagal.emit(str(e))
    #         self.gagal.emit(str(e))  # ⛔ jangan diam-diam error, laporkan
