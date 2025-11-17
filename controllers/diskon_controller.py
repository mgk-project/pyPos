from views.diskon_view import DiskonView
from models.diskon_model import DiskonModel

class DiskonController:
    # def __init__(self, model, view):
    def __init__(self):
        # self.model = model
        # self.view = view
        self.model = DiskonModel(base_url="http://127.0.0.1:5000")
        self.view = DiskonView()



    def tampilkan_keterangan_produk_grosir(self, produk_id):
        print('masuk ke tampilkan keterangan produk grosir')
        data = self.model.get_keterangan_grosir(produk_id)
        # print(f'isi data = {data}')
        if not data:
            self.view.tampilkan_keterangan_diskon("Tidak ada diskon grosir.")
            return

        array_ket = []
        idx_awal = -1
        idx_akhir = -1

        # Cari index awal & akhir
        for i in range(len(data)):
            if data[i]['maxim'] == 100000:
                if idx_awal == -1:
                    idx_awal = i
                else:
                    idx_akhir = i - 1
                    break
        if idx_akhir == -1:
            idx_akhir = len(data) - 1

        batas_jml = 0
        harga_jual = data[idx_awal]['harga_jual']
        for i in range(idx_awal, idx_akhir + 1):
            baris = data[i]
            harga_diskon = baris['harga_diskon']
            nilai_diskon = baris['nilai']
            persen_diskon = float(baris['persen'])

            total_diskon = harga_diskon * baris['minim']

            if baris['maxim'] == 100000:
                ket = f"{baris['minim']} s/d ~ harga Rp {harga_diskon:,.0f} (disc Rp {nilai_diskon:,.0f} / {persen_diskon:.2f}%) (Rp {total_diskon:,.0f} / {baris['minim']})"
            else:
                ket = f"{baris['minim']} s/d {baris['maxim']} harga Rp {harga_diskon:,.0f} (disc Rp {nilai_diskon:,.0f} / {persen_diskon:.2f}%) (Rp {total_diskon:,.0f} / {baris['minim']})"
                batas_jml = baris['minim'] - 1

            array_ket.append(ket)
        if batas_jml==0 :
            batas_jml = baris['minim'] - 1

        array_ket.append(f"1 s/d {batas_jml} harga Rp {harga_jual:,.0f} belum dapat diskon")
        array_ket.reverse()

        hasil_keterangan = "\n".join(array_ket)
        print(f'hasil keterangan diskon = {hasil_keterangan}')
        return hasil_keterangan
        # self.view.tampilkan_keterangan_diskon(hasil_keterangan)

    def tampilkan_keterangan_produk_free(self, produk_id):
        print('masuk ke tampilkan keterangan produk free')
        data = self.model.get_keterangan_free(produk_id)
        if not data:
            self.view.tampilkan_keterangan_diskon("Tidak ada diskon grosir.")
            return

        array_ket = []
        baris = data[0]
        print(f'baris = {baris["kelipatan"]}')
        if baris["kelipatan"]==1:
            array_ket.append(f'gratis produk {baris["free_produk_nama"]} ')
            array_ket.append(f'berlaku kelipatan setiap pembelian {baris["minim"]}')
                    # result.update({
                    #     "keterangan_diskon_free": f'gratis produk {free["free_produk_nama"]} berlaku kelipatan setiap pembelian {free["minim"]}'
                    # })
        else:
            array_ket.append(f'gratis produk {baris["free_produk_nama"]} ')
            array_ket.append(f'tidak berlaku kelipatan minimal pembelian {baris["minim"]}')
                    # result.update({
                    #     "keterangan_diskon_free": f'gratis produk {free["free_produk_nama"]} tidak berlaku kelipatan minimal pembelian {free["minim"]}'
                    # })

        # array_ket.append(f"1 s/d {batas_jml} harga Rp {harga_jual:,.0f} belum dapat diskon")
        hasil_keterangan = "\n".join(array_ket)
        print(f'hasil keterangan diskon = {hasil_keterangan}')
        return hasil_keterangan
    

