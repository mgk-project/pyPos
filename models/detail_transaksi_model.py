from dataclasses import dataclass

@dataclass
class DetailTransaksi:
    produk_id: int
    produk_nama: str
    produk_ord_hrg: float
    produk_ord_jml: int
    produk_jenis: str
    produk_ord_diskon: float
    satuan :str

    def to_tuple_with_transaksi_id(self, transaksi_id):
        return (
            transaksi_id,
            self.produk_id,
            self.produk_nama,
            self.produk_ord_hrg,
            self.produk_ord_jml,
            self.produk_jenis,
            self.produk_ord_diskon,
            self.satuan
        )
    def to_dict_with_transaksi_id(self, transaksi_id):
        return {
            'transaksi_id': transaksi_id,
            'produk_id': self.produk_id,
            'produk_nama': self.produk_nama,
            'produk_ord_hrg': self.produk_ord_hrg,
            'produk_ord_jml': self.produk_ord_jml,
            'produk_jenis': self.produk_jenis,
            'produk_ord_diskon': self.produk_ord_diskon,
            'satuan': self.satuan
        }

@dataclass
class TransaksiDetail:
    produk_id: int
    produk_nama: str
    produk_ord_hrg: float
    produk_ord_jml: int
    produk_jenis: str
    produk_ord_diskon: float
    satuan : str

    def to_dict_with_transaksi_id(self, transaksi_id):
        return {
            'transaksi_id': transaksi_id,
            'produk_id': self.produk_id,
            'produk_nama': self.produk_nama,
            'produk_ord_hrg': self.produk_ord_hrg,
            'produk_ord_jml': self.produk_ord_jml,
            'produk_jenis': self.produk_jenis,
            'produk_ord_diskon': self.produk_ord_diskon,
            'satuan':self.satuan
        }
