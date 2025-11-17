# from PySide6.QtWidgets import QApplication, QLabel

# app = QApplication([])
# label = QLabel("Test GUI")
# label.show()
# app.exec()

from escpos.printer import Usb, Network

# contoh test cetak dummy via USB
p = Usb(0x04b8, 0x0202)  # ganti dengan VID & PID printer kamu
p.text("Hello ESC/POS\n")
p.cut()
