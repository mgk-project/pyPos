import sys
from PySide6.QtWidgets import QApplication, QStackedWidget

from views.login_window import LoginWindow
from views.dashboard_window import DashboardWindow
import os
class AppController(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi POS Beta")

        self.login_window = LoginWindow(self)
        self.dashboard_window = None
        self.addWidget(self.login_window)
        self.setCurrentWidget(self.login_window)

        self.resize(400, 300)
        self.show()

    def login_success(self, user_info):
        # Hapus dashboard sebelumnya jika ada
        if self.dashboard_window:
            self.removeWidget(self.dashboard_window)
            self.dashboard_window.deleteLater()

        self.dashboard_window = DashboardWindow(user_info, self)
        self.addWidget(self.dashboard_window)
        self.setCurrentWidget(self.dashboard_window)

        self.showMaximized()

    def show_login(self):
        self.setCurrentWidget(self.login_window)
        self.resize(400, 300)
        self.showNormal()
        self.login_window.clear_fields()
