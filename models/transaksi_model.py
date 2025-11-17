import sqlite3, math
from datetime import datetime
from dataclasses import dataclass
from utils.mysql_connector import get_mysql_connection,lengkapi_data_mysql,lengkapi_detail_transaksi,get_and_increment_counter_server,generate_nomer2  # asumsi modul kamu namanya begitu
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QCompleter
from PySide6.QtCore import QEvent, Qt
import requests

def update_quota_free_produk_ke_server(arr_free_produk):
    """
    Kirim data free produk ke server saat transaksi disimpan (settle).
    """
    url = "https://beta.mayagrahakencana.com/main_sb/eusvc/proDiskon/saveFreeProduk"
    form_data = {}

    for i, item in enumerate(arr_free_produk):
        prefix = f'arr[{i}]'
        form_data[f'{prefix}[diskon_id]'] = item.get("diskon_id")
        form_data[f'{prefix}[produk_id]'] = item.get("produk_id")
        form_data[f'{prefix}[produk_nama]'] = item.get("produk_nama")
        form_data[f'{prefix}[free_produk_id]'] = item.get("free_produk_id")
        form_data[f'{prefix}[free_produk_nama]'] = item.get("free_produk_nama")
        form_data[f'{prefix}[free_qty]'] = item.get("free_qty")
        form_data[f'{prefix}[kelipatan]'] = item.get("kelipatan", 1)
        form_data[f'{prefix}[quota_global]'] = item.get("quota_global", 0)
        form_data[f'{prefix}[quota_used]'] = item.get("quota_used", 0)
        form_data[f'{prefix}[date]'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        form_data[f'{prefix}[settlement]'] = 1
        form_data[f'{prefix}[transaksi_id]'] = item.get("transaksi_id", "")
        form_data[f'{prefix}[transaksi_no]'] = item.get("transaksi_no", "")
        form_data[f'{prefix}[toko_id]'] = 1001
        form_data[f'{prefix}[oleh_id]'] = item.get("oleh_id")
        form_data[f'{prefix}[oleh_nama]'] = item.get("oleh_nama")
        form_data[f'{prefix}[customer_id]'] = item.get("customer_id", 1)
        form_data[f'{prefix}[customer_nama]'] = item.get("customer_nama", "Tunai")

    try:
        response = requests.post(url, data=form_data)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.RequestException as e:
        print("❌ Error update quota free produk:", e)
        return {"status": 0, "reason": str(e)}

@dataclass
class DetailTransaksi:
    produk_id: int
    produk_nama: str
    produk_ord_hrg: float
    produk_ord_jml: int
    produk_jenis: str
    produk_ord_diskon: float

    def __iter__(self):
        return iter((
            self.produk_id,
            self.produk_nama,
            self.produk_ord_hrg,
            self.produk_ord_jml,
            self.produk_jenis,
            self.produk_ord_diskon,
        ))

class TransaksiModel:
    def __init__(self, db_path):
        self.db_path = db_path

    # import requests
    # import datetime


    def get_produk_autocomplete(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.nama, 
                   MAX(CASE WHEN price.jenis_value = 'harga_list' THEN price.nilai ELSE NULL END) AS harga_jual
            FROM produk p
            INNER JOIN price ON p.id = price.produk_id
            GROUP BY p.id, p.nama
            ORDER BY p.nama;
        """)
        results = cursor.fetchall()
        conn.close()

        barang_list = []
        mapping = {}
        for row in results:
            text = f"{row['nama']} - {row['harga_jual']}"
            barang_list.append(text)
            mapping[text] = {
                "id": row["id"], "nama": row["nama"], "harga_jual": row["harga_jual"]
            }
        return barang_list, mapping

    def cari_barang_by_id(self, id_produk, jumlah_beli):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # result = {
        #     "id": id_produk,
        #     "barcode" : None,
        #     "nama": None,
        #     "harga": None,
        #     "harga_normal": None,
        #     "flag_diskon_grosir": 0,
        #     "flag_diskon_free": 0,
        #     "diskon_persen": 0,
        #     "keterangan_diskon": "",
        #     "free_produk_nama": None,
        #     "kelipatan": None,
        #     "jumlah_free": 0,
        #     "jumlah": jumlah_beli,
        #     "hpp":None
        # }
        result = {
            "id": id_produk,
            "barcode" : None,
            "nama": None,
            "harga": None,
            "harga_normal": None,
            "flag_diskon_grosir": 0,
            "flag_diskon_free": 0,
            "diskon_persen": 0,
            "keterangan_diskon": "",
            "keterangan_diskon_free":"",
            "free_produk_id": None,
            "free_produk_nama": None,
            "kelipatan": None,
            "jumlah_free": 0,
            "jumlah": jumlah_beli,
            "hpp":None,
            "satuan":None
        }

        # tambahan untuk cek kuota global di server
        #         data = {
        #     # 'diskon_id': barang["diskon_id"],
        #     'produk_id': barang["id"], ok
        #     'produk_nama': barang["nama"], ok
        #     'free_produk_id': barang["free_produk_id"], 
        #     'free_produk_nama': barang["free_produk_nama"],
        #     'free_qty': barang["jumlah_free"],
        #     'kelipatan': barang.get("kelipatan", 1),
        #     'quota_global': barang.get("quota_global", 0),
        #     'quota_used': barang.get("quota_used", 0),
        #     'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #     'settlement': 1,  # <--- flag hanya check
        #     'transaksi_id': "",
        #     'transaksi_no': "",
        #     'toko_id': 1001,
        #     'oleh_id': 999,  # contoh, ganti dengan user login
        #     'oleh_nama': "kasir",
        #     'customer_id': 1,
        #     'customer_nama': "Tunai"
        # }

        # format api free produk di sever
        # arr[0][diskon_id] = 1724553389                              // diskon ID dari table diskon jenis freeproduk
        # arr[0][produk_id] = 11174                                   // id produk yang di beli
        # arr[0][produk_nama] = 'AOKA MIX'                            // nama produk yang di beli
        # arr[0][free_produk_id] = '11174'                            // id produk yang menjadi free produk
        # arr[0][free_produk_nama] = 'AOKA MIX'                       // nama produk yang menjadi free produk
        # arr[0][free_qty] = 1                                        // jumlah kuantiti free produk yang di dapatkan
        # arr[0][kelipatan] = 1                                       // dari setingan diskon free produk 1 = kelipatan | 0 = hanya sekali dalam 1 nota | dari table diskon jenis free_produk
        # arr[0][quota_global] = 16562                                // quota free produk table diskon jenis free_produk
        # arr[0][quota_used] = 8                                      // quota terpakai dari table diskon jenis free_produk
        # arr[0][date] = '2025-06-19 13:34:58'                        // waktu penjualan
        # arr[0][settlement] = 1                                      // flag angka 1
        # arr[0][transaksi_id] = 183                                  // transaksi id penjualan
        # arr[0][transaksi_no] = '582-101-1348-0033-0183-00332'       // nomor invoice/struk penjualan
        # arr[0][toko_id] = 1001                                      // toko id 1001 biarkan seperti ini
        # arr[0][oleh_id] = 183                                       // id kasir yang melakukan transaksi penjualan
        # arr[0][oleh_nama] = 'kasir3'                                // nama kasir yang melakukan transaksi penjualan
        # arr[0][customer_id] = 1                                     // id customer
        # arr[0][customer_nama] = 'Tunai'                             // nama customer

        # // jika ada banyak diskon free produk
        # arr[1][diskon_id] = 17245xxxxx
        # arr[1][produk_id] = 1xxxx
        # arr[1][produk_nama] = 'MIE GORxxx'
        # ..........
        

        try:
            # cursor.execute("""
            #     SELECT produk.nama, diskon.persen, diskon.nilai, diskon.harga,
            #            (diskon.nilai + diskon.harga) AS harga_setelah_diskon,produk.barcode,produk.hpp
            #     FROM produk
            #     INNER JOIN diskon ON produk.id = diskon.produk_id
            #     WHERE produk.id = ? AND diskon.jenis = 'produk_grosir'
            #       AND ? BETWEEN diskon.minim AND COALESCE(NULLIF(diskon.maxim, 0), 10000)
            #     ORDER BY diskon.id DESC LIMIT 1
            # """, (id_produk, jumlah_beli))
            # pertama cuma cek ada tidak diskon grosirnya tanpa melihat jumlah inputeannya 
            cursor.execute("""
                SELECT produk.nama, diskon.persen, diskon.nilai, diskon.harga,
                        (diskon.nilai + diskon.harga) AS harga_setelah_diskon,produk.barcode,produk.hpp,produk.satuan
                FROM produk
                INNER JOIN diskon ON produk.id = diskon.produk_id
                WHERE produk.id = ? AND diskon.jenis = 'produk_grosir'
                    
                ORDER BY diskon.id DESC LIMIT 1
            """, (id_produk,))

            grosir = cursor.fetchone()
            if grosir:
                print(f'masuk untuk aktifkan flag diskon grosir nya, id produk = {id_produk} . harga barang = {grosir["harga_setelah_diskon"]}')
                # cuma aktifkan flag diskon grosirnya
                result.update({

                    "nama" : grosir["nama"],
                    "flag_diskon_grosir": 1,
                    "harga": grosir["harga_setelah_diskon"],
                    "diskon_persen": 0,
                    "keterangan_diskon": f"Diskon 0 % = 0",
                    "barcode" : grosir["barcode"],
                    "hpp": grosir["hpp"],
                    "satuan":grosir["satuan"]
                })

                cursor.execute("""
                    SELECT produk.nama, diskon.persen, diskon.nilai, diskon.harga,
                        (diskon.nilai + diskon.harga) AS harga_setelah_diskon,produk.barcode,produk.hpp,produk.satuan
                    FROM produk
                    INNER JOIN diskon ON produk.id = diskon.produk_id
                    WHERE produk.id = ? AND diskon.jenis = 'produk_grosir'
                    AND ? BETWEEN diskon.minim AND COALESCE(NULLIF(diskon.maxim, 0), 10000)
                    ORDER BY diskon.id DESC LIMIT 1
                """, (id_produk, jumlah_beli))
                nominal_grosir = cursor.fetchone()
                
                # cek nominal diskon nya 
                if nominal_grosir:
                    result.update({
                        
                        "nama" : nominal_grosir["nama"],
                        "flag_diskon_grosir": 1,
                        "harga": nominal_grosir["harga_setelah_diskon"],
                        "diskon_persen": nominal_grosir["persen"],
                        "keterangan_diskon": f"Diskon {round(nominal_grosir['persen'])}% = {round(nominal_grosir['nilai'])}",
                        "barcode" : nominal_grosir["barcode"],
                        "hpp": nominal_grosir["hpp"],
                        "satuan":nominal_grosir["satuan"]
                    })

            # cursor.execute("""
            #     SELECT produk.nama, diskon.persen, diskon.nilai, diskon.harga,
            #             (diskon.nilai + diskon.harga) AS harga_setelah_diskon,produk.barcode,produk.hpp,produk.satuan
            #     FROM produk
            #     INNER JOIN diskon ON produk.id = diskon.produk_id
            #     WHERE produk.id = ? AND diskon.jenis = 'produk_grosir'
                    
            #     ORDER BY diskon.id DESC LIMIT 1
            # """, (id_produk,))

            cursor.execute("""
                SELECT diskon.free_produk_nama, diskon.kelipatan, diskon.minim , produk.barcode,produk.hpp,produk.satuan
                FROM produk
                INNER JOIN diskon ON produk.id = diskon.produk_id
                WHERE produk.id = ? AND diskon.jenis = 'free_produk'
                  AND DATE('now') BETWEEN diskon.dtime_start AND diskon.dtime_end
                   
                ORDER BY diskon.id DESC LIMIT 1
            """, (id_produk, ))

            # cursor.execute("""
            #     SELECT diskon.free_produk_nama, diskon.kelipatan, diskon.minim , produk.barcode,produk.hpp,produk.satuan
            #     FROM produk
            #     INNER JOIN diskon ON produk.id = diskon.produk_id
            #     WHERE produk.id = ? AND diskon.jenis = 'free_produk'
            #       AND DATE('now') BETWEEN diskon.dtime_start AND diskon.dtime_end
            #       AND ? BETWEEN diskon.minim AND COALESCE(NULLIF(diskon.maxim, 0), 10000)
            #     ORDER BY diskon.id DESC LIMIT 1
            # """, (id_produk, jumlah_beli))
            free = cursor.fetchone()
            if free:
                print(f'masuk untuk aktifkan flag diskon free nya, nama produk free = {free["free_produk_nama"]} . kelipatan = {free["kelipatan"]}')
                # cuma aktifkan flag diskon grosirnya
                result.update({
                    "flag_diskon_free": 1,
                    "free_produk_nama": free["free_produk_nama"],
                    "kelipatan": free["kelipatan"],
                    "jumlah_free": 0,
                    "barcode" : free["barcode"],
                    "hpp": free["hpp"],
                    "satuan":free["satuan"] 
                })
                if free["kelipatan"]==1:
                    result.update({
                        "keterangan_diskon_free": f'gratis produk {free["free_produk_nama"]} berlaku kelipatan setiap pembelian {free["minim"]}'
                    })
                else:
                     result.update({
                        "keterangan_diskon_free": f'gratis produk {free["free_produk_nama"]} tidak berlaku kelipatan minimal pembelian {free["minim"]}'
                    })
                     
                cursor.execute("""
                    SELECT diskon.free_produk_nama, diskon.kelipatan, diskon.minim , produk.barcode,produk.hpp,produk.satuan
                    FROM produk
                    INNER JOIN diskon ON produk.id = diskon.produk_id
                    WHERE produk.id = ? AND diskon.jenis = 'free_produk'
                      AND DATE('now') BETWEEN diskon.dtime_start AND diskon.dtime_end
                      AND ? BETWEEN diskon.minim AND COALESCE(NULLIF(diskon.maxim, 0), 10000)
                    ORDER BY diskon.id DESC LIMIT 1
                """, (id_produk, jumlah_beli))
                nominal_free = cursor.fetchone()

                # cek nominal diskon nya 
                if nominal_free:
                    print('mau update nominal freenya')
                    result.update({
                        "flag_diskon_free": 1,
                        "free_produk_nama": nominal_free["free_produk_nama"],
                        "kelipatan": nominal_free["kelipatan"],
                        "jumlah_free": math.floor(jumlah_beli / nominal_free["minim"]),
                        "barcode" : nominal_free["barcode"],
                        "hpp": nominal_free["hpp"],
                        "satuan":nominal_free["satuan"]

                        
                    })


            if not result["harga"]:
                cursor.execute("""
                    SELECT p.nama, 
                           MAX(CASE WHEN price.jenis_value = 'harga_list' THEN price.nilai END) AS harga_jual,p.barcode,p.hpp,p.satuan
                    FROM produk p
                    INNER JOIN price ON p.id = price.produk_id
                    WHERE p.id = ?
                    GROUP BY p.nama LIMIT 1
                """, (id_produk,))
                produk = cursor.fetchone()
                if produk:
                    result.update({
                        "harga": produk["harga_jual"],
                        "harga_normal": produk["harga_jual"],
                        "nama": produk["nama"],
                        "barcode" : produk["barcode"],
                        "hpp":produk["hpp"],
                        "satuan":produk["satuan"]
                    })
        except Exception as e:
            print("DB Error:", e)
        finally:
            conn.close()

        return result
    def cari_barang_by_nama(self, nama_barang):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produk WHERE nama LIKE ?", (f"%{nama_barang}%",))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    def cari_barang_by_barcode(self, barcode):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produk WHERE barcode = ?", (barcode,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_and_increment_counter(self, nama="transaksi") -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Ambil nilai counter sekarang
        cursor.execute("SELECT counter FROM penomoran WHERE nama = ?", (nama,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO penomoran (nama, counter) VALUES (?, ?)", (nama, 0))
            counter = 0
        else:
            counter = row[0]
        
        # 2. Increment dan update
        new_counter = counter + 1
        cursor.execute("UPDATE penomoran SET counter = ?, dtime_update = datetime('now') WHERE nama = ?", (new_counter, nama))
        conn.commit()
        
        return new_counter

# def simpan_transaksi(self, data: dict, kasir: str):
#     counter = self.get_and_increment_counter("transaksi")
#     nomer2 = generate_nomer2(counter, kasir)
#     data["nomer2"] = nomer2

# import sqlite3

    def ambil_diskon_by_produk(self,db_path, produk_id):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                nomer_diskon,
                produk_id,
                free_produk_id,
                free_produk_nama,
                kelipatan,
                quota_global,
                quota_used
            FROM diskon
            WHERE produk_id = ? AND jenis = 'free_produk'
            ORDER BY id DESC LIMIT 1
        """, (produk_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "nomer_diskon": row["nomer_diskon"],
                "produk_id": row["produk_id"],
                "free_produk_id": row["free_produk_id"],
                "free_produk_nama": row["free_produk_nama"],
                "kelipatan": row["kelipatan"],
                "quota_global": row["quota_global"],
                "quota_used": row["quota_used"],
            }
        else:
            return None

    # def simpan_transaksi(self, transaksi_data, detail_data,transaksi_data_dict):
    #     counter = self.get_and_increment_counter("transaksi")
    #     nomer2 = generate_nomer2(counter, transaksi_data_dict['oleh_nama'])

    #     # transaksi_data_dict["nomer2"] = nomer2
    #     print(f'transaksi_model,fungsi simpan_transaksi, counter sekarang = {counter}, nomer2 = {nomer2}, nilai transaksi_data_dict["nomer2"] = {transaksi_data_dict["nomer2"]}')
    #     print(f'transaksi_model,fungsi simpan_transaksi, transaksi nilai = {transaksi_data_dict["transaksi_nilai"]}')
    #     conn = sqlite3.connect(self.db_path)
    #     cursor = conn.cursor()
    #     print('fungsi simpan_transaksi, akan memasukkan data ke tabel transaksi master ')
    #     # Gabungkan transaksi_data dan nomer2 ke dalam satu tuple
    #     transaksi_data["settlement_id"]= transaksi_data_dict["settlement_id"]
    #     final_data = transaksi_data + (nomer2,)
    #     try:
    #         # Simpan ke lokal SQLite
    #         cursor.execute("""
    #             INSERT INTO transaksi (
    #                 nomer,dtime, transaksi_nilai, diskon_persen, ppn_persen, transaksi_bulat,
    #                 customers_id, customers_nama, fulldate, oleh_id, oleh_nama, jenis_label,
    #                 transaksi_jenis, settlement_id ,nomer2 
    #             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?)
    #         """, final_data)
    def simpan_transaksi(self, transaksi_data, detail_data, transaksi_data_dict):
        counter = self.get_and_increment_counter("transaksi")
        nomer2 = generate_nomer2(counter, transaksi_data_dict['oleh_nama'])

        # Tambahkan nomer2 ke dict
        transaksi_data_dict["nomer2"] = nomer2

        print(f"transaksi_model,fungsi simpan_transaksi, counter sekarang = {counter}, nomer2 = {nomer2}")
        print(f"transaksi_model,fungsi simpan_transaksi, transaksi nilai = {transaksi_data_dict['transaksi_nilai']}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        print("fungsi simpan_transaksi, akan memasukkan data ke tabel transaksi master")

        try:
            # Buat query insert berdasarkan key dict
            columns = ", ".join(transaksi_data_dict.keys())
            placeholders = ", ".join(["?"] * len(transaksi_data_dict))
            values = list(transaksi_data_dict.values())
            # print("QUERY:", f"INSERT INTO transaksi ({columns}) VALUES ({placeholders})")
            # print("LEN cols:", len(columns.keys()))
            # print("LEN values:", len(values))
            # print("VALUES:", values)

            # Simpan ke SQLite
            cursor.execute(f"""
                INSERT INTO transaksi ({columns}) VALUES ({placeholders})
            """, values)

            transaksi_id = cursor.lastrowid

            for detail in detail_data:
                cursor.execute("""
                    INSERT INTO transaksi_data (
                        transaksi_id, produk_id, produk_nama, produk_ord_hrg,
                        produk_ord_jml, produk_jenis, produk_ord_diskon,satuan
                    ) VALUES (?, ?, ?, ?, ?, ?, ?,?)
                """, detail.to_tuple_with_transaksi_id(transaksi_id))
                detail_id = cursor.lastrowid
                detail = detail_data
                # catat kuota global di server

                # Siapkan list free_produk yang sudah dihitung sebelumnya
                # Contoh:
                arr_free_produk = []
                print('mau proses api free produk')
                for detail in detail_data:
                    print(f'jenis diskon produk ={detail.produk_jenis}')
                    if detail.produk_jenis == "free_produk" and detail.produk_ord_jml > 0:
                        print(f'free produk ={detail_id}')
                        diskon_data = self.ambil_diskon_by_produk(self.db_path, detail.produk_id)
                        if not diskon_data:
                            print(f"⚠️ Diskon tidak ditemukan untuk produk {detail.produk_id}")
                            continue   # skip atau beri default
                        else :
                            barang_detail = self.cari_barang_by_id(detail.produk_id, detail.produk_ord_jml)
                            # barang_detail = self.controller.data_barang_cache[str(barang_data['id'])]
                            jumlah_free = barang_detail.get("jumlah_free", 0)
                            
                            free_item = {
                                "diskon_id": diskon_data["nomer_diskon"],
                                "produk_id": detail.produk_id,
                                "produk_nama": detail.produk_nama,
                                "free_produk_id": diskon_data["free_produk_id"],
                                "free_produk_nama": diskon_data["free_produk_nama"],
                                "free_qty": jumlah_free,
                                "kelipatan": diskon_data["kelipatan"],
                                "quota_global": diskon_data["quota_global"],
                                "quota_used": diskon_data["quota_used"],
                                "transaksi_id": transaksi_id,
                                "transaksi_no": transaksi_data_dict["nomer"],
                                "oleh_id": transaksi_data_dict["oleh_id"],
                                "oleh_nama": transaksi_data_dict["oleh_nama"],
                                "customer_id": transaksi_data_dict.get("customers_id", 1),
                                "customer_nama": transaksi_data_dict.get("customers_nama", "Tunai"),
                            }
                        
                            arr_free_produk.append(free_item)
                            print(f'data arr produk = {free_item}')

                if arr_free_produk:
                    from models.transaksi_model import update_quota_free_produk_ke_server
                    result = update_quota_free_produk_ke_server(arr_free_produk)

                    if result.get("status") == 1:
                        print("✅ Kuota free produk berhasil diupdate ke server")
                    else:
                        print("❌ Gagal update free produk:", result.get("reason"))

            conn.commit()

            conn_server = get_mysql_connection()
            cursor_server = conn_server.cursor()

            # 1. Lengkapi data transaksi
            print('MASUK KE SIMPAN TRANSAKSI -lanjutkan pembayaran')
            data_lengkap = lengkapi_data_mysql(cursor_server, 'transaksi', transaksi_data_dict)
            print(f'settlement id untuk transaksi ini adalah = {transaksi_data_dict["settlement_id"]}')
            # 2. Insert transaksi
            cols = ', '.join(data_lengkap.keys())
            # print(f'kolom = {cols}')
            placeholders = ', '.join(['%s'] * len(data_lengkap))

            

            # print(f'palceholder = {placeholders}')
            values = list(data_lengkap.values())
            print("QUERY:", f"INSERT INTO transaksi ({cols}) VALUES ({placeholders})")
            print("LEN cols:", len(data_lengkap.keys()))
            print("LEN values:", len(values))
            print("VALUES:", values)

            # print(f'data lengkap simpan transaksi nya = {values}')
            # print(f'values nya = {values}')
            # cursor_server.execute(f"""
            #     INSERT INTO transaksi ({cols}) VALUES ({placeholders})
            # """, values)

            

            query = "INSERT INTO transaksi ({}) VALUES ({})".format(cols, placeholders)
            print("[DEBUG] Query MySQL:", query)
            print("[DEBUG] Placeholder count:", placeholders.count("%s"))
            print("[DEBUG] Values count:", len(values))
            cursor_server.execute(query, values)

            transaksi_id_server = cursor_server.lastrowid

            # 3. Insert detail transaksi
            for detail in detail_data:
                detail_dict = detail.to_dict_with_transaksi_id(transaksi_id_server)
                detail_dict_lengkap = lengkapi_data_mysql(cursor_server, 'transaksi_data', detail_dict)

                columns = ', '.join(detail_dict_lengkap.keys())
                placeholders = ', '.join(['%s'] * len(detail_dict_lengkap))
                values = list(detail_dict_lengkap.values())

                # cursor_server.execute(f"""
                #     INSERT INTO transaksi_data ({columns}) VALUES ({placeholders})
                # """, values)
                print("[DEBUG] Query MySQL transaksi data :", query)
                print("[DEBUG] Placeholder count:", placeholders.count("%s"))
                print("[DEBUG] Values count:", len(values))

                query_detail = "INSERT INTO transaksi_data ({}) VALUES ({})".format(columns, placeholders)
                cursor_server.execute(query_detail, values)


            conn_server.commit()

            return transaksi_id

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            conn.close()
            if 'conn_server' in locals():
                conn_server.close()

    def simpan_transaksi_f9(self, transaksi_data, detail_data):
    
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO transaksi (
                    nomer, dtime, transaksi_nilai, diskon_persen, ppn_persen, transaksi_bulat, 
                    customers_id, customers_nama, fulldate, oleh_id, oleh_nama, 
                    jenis_label, transaksi_jenis, settlement_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, transaksi_data)

            transaksi_id = cursor.lastrowid

            # for detail in detail_data:
            #     cursor.execute("""
            #         INSERT INTO transaksi_data (
            #             transaksi_id, produk_id, produk_nama, produk_ord_hrg,
            #             produk_ord_jml, produk_jenis, produk_ord_diskon
            #         ) VALUES (?, ?, ?, ?, ?, ?, ?)
            #     """, (transaksi_id, *detail))
            for detail in detail_data:
                cursor.execute("""
                    INSERT INTO transaksi_data (
                        transaksi_id, produk_id, produk_nama, produk_ord_hrg,
                        produk_ord_jml, produk_jenis, produk_ord_diskon,satuan
                    ) VALUES (?, ?, ?, ?, ?, ?, ?,?)
                """, detail.to_tuple_with_transaksi_id(transaksi_id))

            conn.commit()
            return transaksi_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_transaksi_terakhir(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM transaksi ORDER BY id DESC LIMIT 1")
        transaksi_row = cursor.fetchone()
        conn.close()

        return dict(transaksi_row) if transaksi_row else None

    def get_detail_transaksi(self, transaksi_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM transaksi_data WHERE transaksi_id = ?", (transaksi_id,))
        detail_rows = cursor.fetchall()
        conn.close()

        return detail_rows
