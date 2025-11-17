from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsDropShadowEffect


class DashboardInfoView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # QFrame sebagai satu-satunya box (1 kotak fisik)
        self.box = QFrame()
        self.box.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ccc;
                border-left: 5px solid #2980b9;
                padding: 20px;
            }
        """)
        self.box.setFrameShape(QFrame.StyledPanel)

        # Tambahkan efek bayangan
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(2, 2)
        self.box.setGraphicsEffect(shadow)

        # # Label-label di dalam box
        # self.label_title = QLabel("🧾 Transaksi Hari Ini")
        # self.label_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        # self.label_title.setStyleSheet("color: #2c3e50;")

        # self.label_transaksi = QLabel("💰 0 transaksi hari ini")
        # self.label_transaksi.setFont(QFont("Segoe UI", 12))

        # self.label_retur = QLabel("🔁 0 retur hari ini")
        # self.label_retur.setFont(QFont("Segoe UI", 12))

        # self.label_retur2 = QLabel("🔁 0 retur hari ini")
        # self.label_retur2.setFont(QFont("Segoe UI", 12))

        # self.label_update = QLabel("🕒 Terakhir diperbarui: -")
        # self.label_update.setFont(QFont("Segoe UI", 10))
        # self.label_update.setStyleSheet("color: #7f8c8d;")

        # # Susun label dalam 1 layout
        # box_layout = QVBoxLayout()
        # box_layout.addWidget(self.label_title)
        # box_layout.addSpacing(10)
        # box_layout.addWidget(self.label_transaksi)
        # box_layout.addWidget(self.label_retur)
        # box_layout.addWidget(self.label_retur2)

        # box_layout.addSpacing(10)
        # box_layout.addWidget(self.label_update)
        # Label judul
        # self.label_title = QLabel("🧾 Transaksi Hari Ini")
        # self.label_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        # self.label_title.setStyleSheet("color: #2c3e50;")

        # Label isi utama (semua info jadi satu label)
        # self.label_info = QLabel()
        # self.label_info.setFont(QFont("Segoe UI", 11))
        # self.label_info.setStyleSheet("color: #444;")
        # self.label_info.setAlignment(Qt.AlignLeft)
        # self.label_info.setText("🧾 Transaksi Hari Ini : \n\n 💰 0 transaksi hari ini\n🔁 0 retur hari ini\n🕒 Terakhir diperbarui: -")
        # Label tunggal berisi judul + isi
        self.label_info = QLabel()
        self.label_info.setFont(QFont("Segoe UI", 11))
        self.label_info.setStyleSheet("color: #2c3e50;")  # warna sedikit lebih gelap untuk judul
        self.label_info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.label_info.setText(
            "🧾 Transaksi Hari Ini\n"
            "💰 0 transaksi hari ini\n"
            "🔁 0 retur hari ini\n"
            "🕒 Terakhir diperbarui: -"
        )

        # Layout
        box_layout = QVBoxLayout()
        box_layout.addWidget(self.label_info)

        # Layout
        box_layout = QVBoxLayout()
        # box_layout.addWidget(self.label_title)
        # box_layout.addSpacing(10)
        box_layout.addWidget(self.label_info)

        self.box.setLayout(box_layout)

        # Layout utama widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.box)
        self.setLayout(main_layout)

        self.setFixedSize(400, 300)


    # def update_info(self, transaksi_count, retur_count):
    #     self.label_transaksi.setText(f"💰 {transaksi_count} transaksi hari ini")
    #     self.label_retur.setText(f"🔁 {retur_count} retur hari ini")

    #     from datetime import datetime
    #     waktu = datetime.now().strftime("%H:%M:%S")
    #     self.label_update.setText(f"🕒 Terakhir diperbarui: {waktu}")
    # def update_info(self, transaksi_count, retur_count):
    #     from datetime import datetime
    #     waktu = datetime.now().strftime("%H:%M:%S")
    #     info_text = (
    #         f"💰 {transaksi_count} transaksi hari ini\n"
    #         f"🔁 {retur_count} retur hari ini\n"
    #         f"🕒 Terakhir diperbarui: {waktu}"
    #     )
    #     self.label_info.setText(info_text)

    # def update_info(self, transaksi_count, retur_count):
    #     from datetime import datetime
    #     waktu = datetime.now().strftime("%H:%M:%S")
    #     info_text = (
    #         "🧾 Transaksi Hari Ini\n"
    #         f"💰 {transaksi_count} transaksi hari ini\n"
    #         f"🔁 {retur_count} retur hari ini\n"
    #         f"🕒 Terakhir diperbarui: {waktu}"
    #     )
    #     self.label_info.setText(info_text)

    def update_info(self, transaksi_count, transaksi_total, retur_count, retur_total):
        from datetime import datetime

        # Format total ke rupiah dengan pemisah ribuan
        def format_rupiah(angka):
            return f"Rp {angka:,.0f}".replace(",", ".")

        waktu = datetime.now().strftime("%H:%M:%S")
        info_text = (
            "🧾 Transaksi Hari Ini\n"
            f"💰 {transaksi_count} transaksi | {format_rupiah(transaksi_total)}\n"
            f"🔁 {retur_count} retur | {format_rupiah(retur_total)}\n"
            f"🕒 Terakhir diperbarui: {waktu}"
        )
        self.label_info.setText(info_text)
