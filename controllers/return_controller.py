from models.return_model import ReturnModel,ReturnItem
# from Qt import List

# ---------- CONTROLLER ---------- #
class ReturnController:
    def __init__(self, model: ReturnModel):
        self.model = model

    def proses_return(self, transaksi_id: str, selected_items: List[ReturnItem]):
        kode_voucher = self.model.insert_return(transaksi_id, selected_items)
        # TODO: panggil fungsi cetak struk voucher
        print(f"[DEBUG] Return berhasil. Kode voucher: {kode_voucher}")
        return kode_voucher
