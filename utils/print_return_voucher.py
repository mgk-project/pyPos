from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PySide6.QtGui import QPainter, QFont
from PySide6.QtCore import Qt
from datetime import datetime

class ReturnVoucherPrinter:
    def __init__(self, conn, kode_voucher):
        self.conn = conn
        self.kode_voucher = kode_voucher

    def print_preview(self, parent=None):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, parent)
        preview.paintRequested.connect(self.print_voucher)
        preview.exec()

    def print_voucher(self, printer):
        painter = QPainter(printer)
        painter.begin(printer)

        font_title = QFont("Arial", 14, QFont.Bold)
        font_normal = QFont("Arial", 10)

        y = 100
        line_height = 30
        x_margin = 100

        # def draw_line(text, font, y_offset=0):
        #     nonlocal y
        #     painter.setFont(font)
        #     painter.drawText(x_margin, y + y_offset, text)
        #     y += line_height
        page_width = printer.pageRect(QPrinter.DevicePixel).width()  # ✅ Fix di sini

        def draw_line(text, font, extra_space=0):
            nonlocal y
            painter.setFont(font)
            rect = painter.boundingRect(x_margin, y, page_width - 2 * x_margin, 100, Qt.TextWordWrap, text)
            painter.drawText(rect, Qt.TextWordWrap, text)
            y += rect.height() + extra_space

        cur = self.conn.cursor()

        # Ambil data master return
        cur.execute("""
            SELECT r.kode_voucher, r.tanggal_return, r.total_return, c.nama
            FROM return_transaksi_penjualan r
            LEFT JOIN per_customers c ON r.customer_id = c.id
            WHERE r.kode_voucher = ?
        """, (self.kode_voucher,))
        master = cur.fetchone()

        # Ambil detail return
        cur.execute("""
            SELECT produk_nama, jumlah, harga, subtotal
            FROM detail_return_transaksi_penjualan d
            JOIN return_transaksi_penjualan r ON d.return_id = r.id
            WHERE r.kode_voucher = ?
        """, (self.kode_voucher,))
        details = cur.fetchall()
        # page_width = printer.pageRect().width()

        draw_line("VOUCHER RETURN", font_title, 10)
        draw_line("-" * 80, font_normal)
        draw_line(f"Kode Voucher : {master[0]}", font_normal)
        draw_line(f"Tanggal Return     : {master[1]}", font_normal)
        draw_line(f"Tanggal Cetak     : {master[1]}", font_normal)

        draw_line(f"Customer     : {master[3]}", font_normal)
        draw_line(f"Total Return : Rp {master[2]:,.0f}", font_normal)
        draw_line("-" * 80, font_normal)
        draw_line("Detail Barang yang Direturn:", font_normal, 5)

        for produk_nama, jumlah, harga, subtotal in details:
            detail_line = f"- {produk_nama} | Qty: {jumlah} | Harga: Rp {harga:,.0f} | Subtotal: Rp {subtotal:,.0f}"
            draw_line(detail_line, font_normal)

        draw_line("-" * 70, font_normal, 5)
        draw_line("Gunakan voucher ini untuk pembelian berikutnya(masa berlaku voucher  max 24 jam).", font_normal)
        draw_line("Terima kasih.", font_normal)

        # draw_line("VOUCHER RETURN", font_title)
        # draw_line("-" * 80, font_normal)
        # draw_line(f"Kode Voucher : {master[0]}", font_normal)
        # draw_line(f"Tanggal      : {master[1]}", font_normal)
        # draw_line(f"Customer     : {master[3]}", font_normal)
        # draw_line(f"Total Return : Rp {master[2]:,.0f}", font_normal)
        # draw_line("-" * 80, font_normal)
        # draw_line("Detail Barang yang Direturn:", font_normal)

        # for produk_nama, jumlah, harga, subtotal in details:
        #     draw_line(f"- {produk_nama} | Qty: {jumlah} | Harga: Rp {harga:,.0f} | Subtotal: Rp {subtotal:,.0f}", font_normal)

        # draw_line("-" * 70, font_normal)
        # draw_line("Gunakan voucher ini untuk pembelian berikutnya.", font_normal)
        # draw_line("Terima kasih.", font_normal)

        painter.end()
