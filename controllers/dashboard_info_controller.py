from models.dashboard_info_model import DashboardInfoModel
from views.dashboard_info_view import DashboardInfoView
from PySide6.QtCore import QTimer

class DashboardInfoController:
    def __init__(self, db_path):
        self.model = DashboardInfoModel(db_path)
        self.view = DashboardInfoView()
        print('masuk dasboard info controller')
        # self.update_info()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5000)  # setiap 5 detik refresh

        self.refresh_data()

    def update_info(self):
        transaksi_count, transaksi_total,retur_count,retur_total = self.model.get_today_summary()
        self.view.update_info(transaksi_count, transaksi_total,retur_count,retur_total)

    def get_view(self):
        return self.view
    
    def refresh_data(self):
        # invoice_count = self.model.get_today_invoice_count()
        # retur_count = self.model.get_today_retur_count()
        self.update_info()

        
