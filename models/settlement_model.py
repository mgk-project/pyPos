import sqlite3
from datetime import datetime, time , date
import hashlib
from utils.mysql_connector import get_mysql_connection,lengkapi_data_mysql,lengkapi_detail_transaksi  # asumsi modul kamu namanya begitu


class SettlementModel:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        from utils.path_utils import get_db_path
        return sqlite3.connect(get_db_path())

    def get_transaksi_belum_settle(self):
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # yang perlu settlement hanya yang tunai ( settlement_id = 1 )
        today1 = datetime.now().strftime("%Y-%m-%d")
        # today = date(today1)
        today = date.today()
        batas_waktu = f"{today} 20:00:00"
        print(f'batas waktu = {batas_waktu}')
        # query = """
        # SELECT id, dtime as tanggal, customers_nama AS customer, transaksi_nilai AS total
        # FROM transaksi
        # WHERE settlement_id = 1 
        # AND date(dtime) < ?
        # ORDER BY datetime(dtime) ASC
        # """
        query = """
        SELECT id, dtime as tanggal, customers_nama AS customer, transaksi_nilai AS total
        FROM transaksi
        WHERE settlement_id = 1 
        AND datetime(dtime, '+10 hours') < ?
        ORDER BY datetime(dtime) ASC
        """
        print(f'{query}')
        print(f'{batas_waktu}')
        cursor.execute(query, (batas_waktu,))
        rows = cursor.fetchall()
        conn.close()
        # print(dict(row) for row in rows)
        return [dict(row) for row in rows]

    def get_detail_transaksi(self, transaksi_id):
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
        SELECT produk_nama AS nama, produk_ord_jml as jumlah, produk_ord_hrg AS total
        FROM transaksi_data
        WHERE transaksi_id = ?
        """
        cursor.execute(query, (transaksi_id,))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_list_admin(self):
        conn = self.connect()
        cursor = conn.cursor()

        query = """
        SELECT nama
        FROM per_employee
        WHERE LOWER(nama) LIKE 'admin%'
        """
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        return [row[0] for row in results]

    def verifikasi_admin(self, nama_admin, password_input):
        conn = self.connect()
        cursor = conn.cursor()

        query = """
        SELECT password
        FROM per_employee
        WHERE nama = ?
        """
        cursor.execute(query, (nama_admin,))
        result = cursor.fetchone()
        conn.close()

        if result:
            password_db = result[0]
            # Ubah input jadi hash MD5 dulu
            password_input_hash = hashlib.md5(password_input.encode()).hexdigest()
            return password_input_hash == password_db

        return False
    


    def cek_transaksi_settlement(self):
        try:
            from utils.path_utils import get_db_path
            conn = sqlite3.connect(get_db_path())
            print("DB Path:", get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # yang perlu di settle hanya yang tunai (settlement_id = 1,debit dan credit sudah lewat edc)
            today = date.today()
            batas_waktu = f"{today} 20:00:00"

            # query = """
            #     SELECT * FROM transaksi 
            #     WHERE jenis_label = 'invoice' 
            #     AND settlement_id = 1 
            #     AND datetime(dtime, '+10 hours') < datetime('now')
            # """
            query = """
                SELECT id, dtime as tanggal, customers_nama AS customer, transaksi_nilai AS total
                FROM transaksi
                WHERE settlement_id = 1 
                AND datetime(dtime, '+10 hours') < ?
                ORDER BY datetime(dtime) ASC
                """
            print(f'isi cek transaksi settlment = {query}')
            print(f'{batas_waktu}')
            cursor.execute(query, (batas_waktu,))
            # rows = cursor.fetchall()
            # conn.close()

            # print(f'isi cek transaksi settlment = {query}')
            # cursor.execute(query)
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

    def get_rekap_settlement(self):
        """
        Menghitung rekap transaksi tunai & non-tunai (per EDC).
        """
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # query = """
        # SELECT metode_bayar, receive_account, SUM(transaksi_nilai) as total
        # FROM transaksi
        # WHERE settlement_id = 1
        # GROUP BY metode_bayar, receive_account
        # """

        # query = """
        # SELECT settlement_id ,bank_nama AS jenis_edc,bank_from AS jenis_bank_cust,bank_rekening_nama AS rekening_cust, COUNT(id) AS jumlah_Nota, SUM(transaksi_nilai) AS total
        # FROM transaksi
        # WHERE bank_nama LIKE '#EDC%'
        # GROUP BY settlement_id, bank_nama,bank_from, bank_rekening_nama
        # """

        query = """
        SELECT settlement_id ,bank_nama AS jenis_edc,bank_from AS jenis_bank_cust,bank_rekening_nama AS rekening_cust, COUNT(id) AS jumlah_Nota, SUM(transaksi_nilai) AS total
        FROM transaksi
        
        GROUP BY settlement_id, bank_nama,bank_from, bank_rekening_nama
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        hasil = {"tunai": 0, "edc": {}}
        for row in rows:
            metode = row["settlement_id"]
            total = row["total"] or 0
            # settlement id = 1 artinya tunai
            # settlement id = 2 artinya kredit
            # settlement id = 3 artinya debit
            if metode == 0: #sudah di settle , biarkan saja
                print('SUDAH DI SETTLE')
            elif metode  ==  1 :
                hasil["tunai"] += total
            else:  # anggap metode lain adalah EDC
                edc_name = row["jenis_edc"] or "UNKNOWN"
                hasil["edc"][edc_name] = hasil["edc"].get(edc_name, 0) + total

        return hasil
    
    def set_settlement(self, transaksi_ids, admin, total_disetor):
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        conn_server = get_mysql_connection()
        cursor_server = conn_server.cursor()

        try:
            # hitung total transaksi yg di-settle # ditambahkan oleh tim 2 supaya yang di cek cuma yang tunai (settlement_id = 1)
            cursor.execute(f"""
                SELECT SUM(transaksi_nilai) as total
                FROM transaksi
                WHERE settlement_id = 1 and id IN ({','.join(['?'] * len(transaksi_ids))})
            """, transaksi_ids)
            total_harus = cursor.fetchone()["total"] or 0

            # simpan transaksi settlement (update transaksi)
            query_nomer_batch = f"""
                SELECT id, nomer FROM transaksi
                WHERE settlement_id = 1 and id IN ({','.join(['?'] * len(transaksi_ids))})
            """
            cursor.execute(query_nomer_batch, transaksi_ids)
            rows = cursor.fetchall()

            for row in rows:
                transaksi_id = row['id']
                nomer_transaksi = row['nomer']

                cursor.execute("UPDATE transaksi SET settlement_id = 0 WHERE id = ?", (transaksi_id,))
                cursor_server.execute("UPDATE transaksi SET settlement_id = 0 WHERE nomer = %s", (nomer_transaksi,))

            # hitung status setor
            selisih = total_disetor - total_harus
            if selisih == 0:
                status = "✔️ Sesuai"
            elif selisih > 0:
                status = f"➕ Lebih setor {selisih:,.0f}"
            else:
                status = f"➖ Kurang setor {abs(selisih):,.0f}"

            # simpan ke settlement_history
            cursor.execute("""
                INSERT INTO settlement_history (tanggal, admin, total_harus, total_disetor, selisih, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), admin, total_harus, total_disetor, selisih, status))

            conn.commit()
            conn_server.commit()

        except Exception as e:
            print("❌ Error settlement:", e)
            conn.rollback()
            conn_server.rollback()
        finally:
            conn.close()
            conn_server.close()

    # def set_settlement(self, transaksi_ids):
    #     import sqlite3

    #     # SQLite: koneksi lokal
    #     conn = self.connect()
    #     conn.row_factory = sqlite3.Row  # pastikan fetchone() mengembalikan dict-like row
    #     cursor = conn.cursor()

    #     # MySQL: koneksi server
    #     conn_server = get_mysql_connection()
    #     cursor_server = conn_server.cursor()

    #     try:
    #         # Ambil semua nomer transaksi dari ID dalam 1 query
    #         query_nomer_batch = f"""
    #             SELECT id, nomer FROM transaksi
    #             WHERE id IN ({','.join(['?'] * len(transaksi_ids))})
    #         """
    #         cursor.execute(query_nomer_batch, transaksi_ids)
    #         rows = cursor.fetchall()

    #         for row in rows:
    #             transaksi_id = row['id']
    #             nomer_transaksi = row['nomer']

    #             # Update lokal
    #             cursor.execute("""
    #                 UPDATE transaksi SET settlement_id = 0 WHERE id = ?
    #             """, (transaksi_id,))

    #             # Update server berdasarkan nomer
    #             cursor_server.execute("""
    #                 UPDATE transaksi SET settlement_id = 0 WHERE nomer = %s
    #             """, (nomer_transaksi,))

    #         conn.commit()
    #         conn_server.commit()

    #     except Exception as e:
    #         print("❌ Terjadi kesalahan saat update settlement:", str(e))
    #         conn.rollback()
    #         conn_server.rollback()

    #     finally:
    #         conn.close()
    #         conn_server.close()

    def get_last_settlements(self, limit=7):
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tanggal, admin, total_harus, total_disetor, selisih, status
            FROM settlement_history
            ORDER BY datetime(tanggal) DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def generate_settlement_number(self, conn):
        """Buat nomor settlement otomatis: ST-YYYYMMDD-XXX"""
        import datetime
        today_str = datetime.date.today().strftime("%Y%m%d")
        cur = conn.cursor()
        cur.execute("SELECT counter FROM transaksi_settlement WHERE counter LIKE ? ORDER BY id DESC LIMIT 1",
                    (f"ST-{today_str}-%",))
        row = cur.fetchone()
        if row:
            last_num = int(row[0].split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f"ST-{today_str}-{new_num:03d}"


    def simpan_settlement(self, kasir_id, kasir_nama, cabang_id, cabang_nama, transaksi_list):
        """
        Simpan hasil settlement ke tabel transaksi_settlement.
        transaksi_list = list of dict { 'id':..., 'nomer':..., 'total':..., 'metode':... }
        """
        import json, sqlite3
        from datetime import datetime

        conn = sqlite3.connect(self.db_path)
        try:
            counter = self.generate_settlement_number(conn)
            data_transaksi_id = json.dumps([t["id"] for t in transaksi_list])

            cur = conn.cursor()
            cur.execute("""
                INSERT INTO transaksi_settlement 
                (counter, oleh_id, oleh_dtime, data_transaksi_id, cabang_id, oleh_nama, cabang_nama)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                counter, kasir_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data_transaksi_id, cabang_id, kasir_nama, cabang_nama
            ))
            conn.commit()
            print(f"[Settlement] Berhasil disimpan dengan ID {counter}")
            return counter
        except Exception as e:
            print(f"[Settlement] Gagal simpan settlement: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def hitung_total_per_metode(self):
        """Ambil total penjualan per metode hari ini"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT settlement_id, SUM(transaksi_nilai)
            FROM transaksi
            WHERE DATE(dtime) = DATE('now')
            GROUP BY settlement_id
        """)
        result = cur.fetchall()
        conn.close()
        return {r[0]: r[1] for r in result}


    # def print_settlement_report(self, counter, kasir_nama, shift, total_dict, transaksi_list):
    #     """
    #     Cetak laporan settlement (POS Settlement Report)
    #     """
    #     from PySide6.QtGui import QTextDocument
    #     from PySide6.QtPrintSupport import QPrinter

    #     html = f"""
    #     <html><body>
    #     <pre>
    # ---------------------------------------
    #         POS Settlement Report
    # ---------------------------------------
    # Tanggal       : {datetime.now().strftime("%d/%m/%Y")}
    # Kasir         : {kasir_nama}
    # Shift         : {shift}
    # ---------------------------------------
    #     """

    #     grand_total = 0
    #     for metode, nilai in total_dict.items():
    #         html += f"{metode.ljust(15)}: Rp {nilai:,.0f}\n"
    #         grand_total += nilai

    #     html += f"---------------------------------------\nTOTAL{'':13}: Rp {grand_total:,.0f}\n---------------------------------------\n"

    #     html += "No. Transaksi  Jumlah      Metode\n"
    #     for t in transaksi_list:
    #         html += f"{t['nomer']:<13} Rp {t['total']:>10,.0f}  {t['metode']}\n"

    #     html += f"---------------------------------------\nSettlement ID : {counter}\n---------------------------------------\n"
    #     html += "</pre></body></html>"

    #     printer = QPrinter()
    #     doc = QTextDocument()
    #     doc.setHtml(html)
    #     doc.print_(printer)
    
    # def print_settlement_report(self, counter, kasir_nama, shift, total_dict, transaksi_list):
    #     from PySide6.QtGui import QTextDocument
    #     from PySide6.QtPrintSupport import QPrinter

    #     html = f"""
    #     <html><body style='font-family: monospace;'>
    #     <pre>
    # ---------------------------------------
    #         POS Settlement Report
    # ---------------------------------------
    # Tanggal  : {datetime.now().strftime("%d/%m/%Y")}
    # Kasir    : {kasir_nama}
    # Shift    : {shift}
    # ---------------------------------------
    # """

    #     grand_total = 0
    #     for metode, nilai in total_dict.items():
    #         html += f"{metode:<15}: Rp {nilai:>10,.0f}\n"
    #         grand_total += nilai

    #     html += f"---------------------------------------\nTOTAL{'':13}: Rp {grand_total:>10,.0f}\n---------------------------------------\n"

    #     html += "No. Transaksi     Jumlah      Metode\n"
    #     for t in transaksi_list:
    #         html += f"{t['id']:<15} Rp {t['total']:>10,.0f}  {t['metode']}\n"

    #     html += f"---------------------------------------\nSettlement ID : {counter}\n---------------------------------------\n"
    #     html += "</pre></body></html>"

    #     printer = QPrinter()
    #     printer.setPrinterName("EPPOS 58 Bluetooth")
    #     doc = QTextDocument()
    #     doc.setHtml(html)
    #     doc.print_(printer)

    def print_settlement_report(self, counter, kasir_nama, shift, total_dict, transaksi_list):
        from PySide6.QtGui import QTextDocument
        from PySide6.QtPrintSupport import QPrinter
        from datetime import datetime

        html = f"""
        <html><body style='font-family: monospace;'>
        <pre>
    ---------------------------------------
            POS Settlement Report
    ---------------------------------------
    Tanggal  : {datetime.now().strftime("%d/%m/%Y %H:%M")}
    Kasir    : {kasir_nama}
    Shift    : {shift}
    ---------------------------------------
    """

        # print(f'nilati var transaksi list = {transaksi_list}')
        # ---- Bagian total per metode pembayaran ----
        grand_total = 0
        for metode, nilai in total_dict.items():
            html += f"{metode:<15}: Rp {nilai:>10,.0f}\n"
            grand_total += nilai

        html += f"---------------------------------------\nTOTAL{'':13}: Rp {grand_total:>10,.0f}\n---------------------------------------\n"
        html += "No. Transaksi   Jumlah       Metode\n"

        # ---- Baris transaksi individual ----
        for t in transaksi_list:
            # Ambil kolom yang ada — fleksibel dengan nama kolom di database
            total = (
                t.get("total")
                or t.get("total_harga")
                or t.get("grand_total")
                or t.get("jumlah_bayar")
                or 0
            )
            metode = (
                t.get("metode")
                or t.get("payment_method")
                or t.get("settlement_metode")
                or "-"
            )
            nomor = t.get("nomer") or t.get("id") or "-"

            html += f"{nomor:<13} Rp {total:>10,.0f}  {metode}\n"

        html += f"---------------------------------------\nSettlement ID : {counter}\n---------------------------------------\n"
        html += "</pre></body></html>"

        # ---- Cetak langsung ke printer ----
        printer = QPrinter()
        printer.setPrinterName("EPPOS 58 Bluetooth")
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

        print(f"[Print] Settlement {counter} berhasil dicetak.")


    def sudah_disettle_hari_ini(self, kasir_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM transaksi_settlement
            WHERE oleh_id = ? AND DATE(oleh_dtime) = DATE('now')
        """, (kasir_id,))
        count = cur.fetchone()[0]
        conn.close()
        return count > 0
