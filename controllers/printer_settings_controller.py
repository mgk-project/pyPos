from typing import Optional, List, Dict
from models.printer_settings_model import PrinterSettingsModel
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PySide6.QtGui import (
    QPageSize, QPageLayout, QTextDocument, QPainter, QFont, QFontMetricsF
)
from PySide6.QtCore import QDateTime, QSizeF, QMarginsF

import base64
from io import BytesIO
import os
from PySide6.QtPrintSupport import QPrinterInfo
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo



class PrinterSettingsController:
    """Controller pengaturan printer & cetak struk (stabil, rapi, + preview)."""

    def __init__(self):
        self.model = PrinterSettingsModel()

    # ------------------ CRUD daftar printer ------------------
    def get_printers(self) -> List[Dict]:
        return self.model.load_printers()

    def add_printer(self, name: str, paper_size: str, set_default: bool = False) -> None:
        printer = {"name": name, "paper_size": paper_size, "default": bool(set_default)}
        printers = self.model.load_printers()
        if set_default:
            for p in printers:
                p["default"] = False
        printers.append(printer)
        self.model.save_printers(printers)

    def remove_printer(self, index: int) -> None:
        self.model.remove_printer(index)

    def set_default(self, index: int) -> None:
        self.model.set_default(index)

    # ------------------ util ------------------
    def rupiah(self, n: int) -> str:
        return "Rp " + f"{n:,}".replace(",", ".")

    def _mm_to_points(self, mm: float) -> float:
        return (mm / 25.4) * 72.0

    # ------------------ preview printer (PDF, independen dari driver) ------------------
    def _make_preview_printer(self, w_mm: float) -> QPrinter:
        p = QPrinter(QPrinter.HighResolution)
        p.setOutputFormat(QPrinter.PdfFormat)   # penting: preview tidak ikut ukuran A4 driver
        p.setResolution(203)
        h_mm = 800.0  # tinggi cukup panjang untuk preview roll

        # PySide6: gunakan QPageSize + QPageLayout, mode FullPageMode
        size = QPageSize(QSizeF(w_mm, h_mm), QPageSize.Millimeter, f"Preview {int(w_mm)}mm")
        try:
            layout = p.pageLayout()
            layout.setPageSize(size)
            layout.setOrientation(QPageLayout.Portrait)
            layout.setMode(QPageLayout.FullPageMode)        # <-- benar untuk PySide6
            layout.setMargins(QMarginsF(0, 0, 0, 0))
            p.setPageLayout(layout)
        except Exception:
            # Fallback aman
            try:
                p.setPageSize(size)
            except Exception:
                pass
            try:
                p.setFullPage(True)
            except Exception:
                pass
        return p

    # ------------------ estimasi kolom untuk separator dinamis ------------------
    def _estimate_cols(self, printer: QPrinter, css_font_pt: float, family: str, paper_label: str) -> int:
        cols = 32
        try:
            font = QFont(family)
            font.setPointSizeF(css_font_pt)
            fm = QFontMetricsF(font)
            char_w = max(1.0, fm.horizontalAdvance("0"))
            page_w = float(printer.pageRect(QPrinter.DevicePixel).width())
            cols = int((page_w - 8.0) / char_w)
        except Exception:
            pass

        guess_map = {"56": 30, "56mm": 30, "58": 32, "58mm": 32, "80": 48, "80mm": 48, "100x150": 64, "100x150mm": 64}
        key = (paper_label or "").lower().strip()
        guess = guess_map.get(key)
        if guess:
            if cols < 24 or cols > 84:
                cols = guess
            else:
                cols = max(min(cols, guess + 6), guess - 6)
        return max(24, min(cols, 84))

    # ------------------ ukuran kertas (Qt6 + fallback aman) ------------------
    def _apply_paper_size(self, printer: QPrinter, paper_label: str) -> None:
        label = (paper_label or "").lower().strip()
        if label in ("56", "56mm"):
            w_mm, h_mm = 56.0, 300.0
        elif label in ("58", "58mm"):
            w_mm, h_mm = 58.0, 300.0
        elif label in ("80", "80mm"):
            w_mm, h_mm = 80.0, 300.0
        elif label in ("100x150", "100x150mm"):
            w_mm, h_mm = 100.0, 150.0
        else:
            w_mm, h_mm = 58.0, 300.0

        size = QPageSize(QSizeF(w_mm, h_mm), QPageSize.Millimeter, f"Receipt {int(w_mm)}mm")
        try:
            layout = printer.pageLayout()
            layout.setPageSize(size)
            layout.setOrientation(QPageLayout.Portrait)
            layout.setMode(QPageLayout.FullPageMode)        # pastikan full page
            layout.setMargins(QMarginsF(0, 0, 0, 0))
            printer.setPageLayout(layout)
        except Exception as e:
            print(f"[Printer] pageLayout gagal, fallback: {e}")
            try:
                printer.setPageSize(size)
            except Exception:
                pass
            try:
                printer.setFullPage(True)
            except Exception:
                pass

    # ------------------ QR Code (opsional) ------------------
    def _qr_png_base64(self, data: str, size_px: int = 200) -> Optional[str]:
        try:
            import qrcode  # optional
            qr = qrcode.QRCode(
                version=1, error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=4, border=2
            )
            qr.add_data(data or "")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            try:
                img = img.resize((size_px, size_px))
            except Exception:
                pass
            buf = BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return "data:image/png;base64," + b64
        except Exception as e:
            print(f"[QR] modul qrcode tidak tersedia/gagal: {e}")
            return None

    # ------------------ builder HTML ------------------
#     def _build_receipt_html(
#         self, items: List[Dict], payment_info: Dict, wifi_code: str, qr_data: str, cols: int
#     ) -> str:
#         # kolom untuk baris item
#         w_qty, w_price, w_subt = 3, 8, 9
#         w_name = max(10, cols - (1 + (w_qty + 3 + w_price + 1 + w_subt)))

#         lines = []
#         sep_eq = "=" * cols
#         sep_d = "-" * cols
#         now = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm:ss")

#         # ---------- BODY ITEMS (monospace) ----------
#         lines.append(sep_eq)

#         total = 0
#         for it in items:
#             name = (it.get("name") or "")[:w_name]
#             qty = int(it.get("qty") or 0)
#             price = int(it.get("price") or 0)
#             disc = int(it.get("disc") or 0)
#             is_free = bool(it.get("free") or False)

#             if is_free:
#                 lines.append(name)
#                 lines.append("FREE ITEM".ljust(cols))
#                 continue

#             lines.append(name)
#             subtotal = qty * price
#             if disc > 0:
#                 subtotal_after = max(0, subtotal - disc)
#                 left = f"{str(qty).rjust(w_qty)} x {str(price).rjust(w_price)} -"
#                 right = f"{subtotal}".rjust(w_subt)
#                 lines.append(left + " " + right)

#                 left = "DISKON".ljust(w_qty + 3 + w_price + 2)
#                 right = f"-{disc}".rjust(w_subt)
#                 lines.append(left + right)

#                 left = "SUBTOTAL".ljust(w_qty + 3 + w_price + 2)
#                 right = f"{subtotal_after}".rjust(w_subt)
#                 lines.append(left + right)
#                 total += subtotal_after
#             else:
#                 total += subtotal
#                 left = f"{str(qty).rjust(w_qty)} x {str(price).rjust(w_price)} ="
#                 right = f"{subtotal}".rjust(w_subt)
#                 lines.append(left + " " + right)

#         lines.append(sep_d)

#         # Ringkasan
#         ppn = int(total * 0.11)
#         grand = total + ppn

#         amt_w = min(14, max(10, int(cols * 0.38)))
#         lbl_w = max(10, cols - amt_w)

#         def line_amount(label: str, amount: int) -> None:
#             lbl = (label + ":").ljust(lbl_w)
#             amt = self.rupiah(amount).rjust(amt_w)
#             lines.append(lbl + amt)

#         line_amount("Subtotal", total)
#         line_amount("PPN 11%", ppn)
#         lines.append(sep_d)
#         lines.append("<b>" + ("TOTAL:".ljust(lbl_w)) + self.rupiah(grand).rjust(amt_w) + "</b>")

#         # Pembayaran (Debit Card)
#         method = (payment_info or {}).get("method", "Debit Card")
#         card_brand = (payment_info or {}).get("card_brand", "BANK")
#         last4 = (payment_info or {}).get("last4", "XXXX")
#         appr = (payment_info or {}).get("approval_code", "APPROVED")
#         lines.append("")
#         lines.append(f"Bayar : {method}")
#         lines.append(f"Bank  : {card_brand} •••• {last4}")
#         lines.append(f"Auth  : {appr}")

#         lines.append("")
#         lines.append(sep_eq)
#         lines.append(f"Wi-Fi Gratis: {wifi_code or '-'}")
#         lines.append("Scan QR di bawah untuk info/garansi")
#         lines.append(sep_eq)

#         # ---------- QR block ----------
#         data_uri = self._qr_png_base64(qr_data or "")
#         if data_uri:
#             qr_block = (
#                 '<img src="' + data_uri +
#                 '" alt="QR" style="display:block;margin:8px auto;width:160px;height:160px;" />'
#             )
#         else:
#             qr_block = (
#                 '<div style="width:160px;height:160px;border:2px dashed #000;'
#                 'margin:8px auto;display:flex;align-items:center;justify-content:center;">'
#                 '<div style="font-size:10pt;text-align:center;">QR CODE</div></div>'
#             )

#         # ---------- HTML: header & footer center+bold, body monospace ----------
#         html_head = """
# <html>
# <head>
# <meta charset="utf-8">
# <style>
#   body { margin:0; padding:0; }
#   .hdr { text-align:center; font-weight:bold; font-size: 12pt; line-height:1.2; margin: 0 0 4px 0; }
#   .sub { text-align:center; font-size: 10pt; line-height:1.2; margin: 0 0 6px 0; }
#   pre  {
#     white-space: pre-wrap;
#     font-family: "DejaVu Sans Mono","Courier New", monospace;
#     font-size: 10pt;
#     line-height: 1.5;
#     margin: 0;
#   }
#   .ftr { text-align:center; font-weight:bold; margin-top:6px; }
# </style>
# </head>
# <body>
# """
#         header_html = (
#             '<div class="hdr">TOKO CONTOH CABANG JKT</div>'
#             '<div class="sub">Jl. Raya Merdeka No.123</div>'
#             f'<div class="sub">{now}</div>'
#         )
#         pre_block = "<pre>" + "\n".join(lines) + "</pre>"
#         footer_html = '<div class="ftr">Terima kasih :)</div>'
#         html_tail = "</body></html>"

#         return html_head + header_html + pre_block + qr_block + footer_html + html_tail
    def _build_receipt_html(
        self, items: List[Dict], payment_info: Dict,
        wifi_code: str, qr_data: str, cols: int,
        setting: Dict, transaksi_data_dict: Dict
    ) -> str:
        """
        Build struk HTML dinamis, dengan header/footer dari setting_struk.csv
        dan data transaksi nyata.
        """
        

        # kolom untuk baris item
        w_qty, w_price, w_subt = 3, 8, 9
        w_name = max(10, cols - (1 + (w_qty + 3 + w_price + 1 + w_subt)))

        lines = []
        sep_eq = "=" * cols
        sep_d = "-" * cols
        now = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm:ss")

        # ---------- BODY ITEMS (monospace) ----------
        lines.append(sep_eq)

        total = 0
        for it in items:
            print(f'isi var it = {it}')
            name = (it.get("name") or "")[:w_name]
            qty = int(it.get("qty") or 0)
            price = int(it.get("price") or 0)
            disc = int(it.get("disc") or 0)
            is_free = bool(it.get("free") or False)
            print(f'is free nya bernilai {is_free}')
            # if is_free:
            #     lines.append(name)
            #     lines.append("FREE ITEM".ljust(cols))
            #     continue

            lines.append(name)
            subtotal = qty * price
            disc_value=0

            if disc > 0:
                # kalau disc <= 100 → anggap persen, kalau > 100 → anggap rupiah
                if disc <= 100:
                    disc_value = int(subtotal * disc / 100)
                else:
                    disc_value = disc

                # subtotal_after = max(0, subtotal - disc_value)
                # left = f"{str(qty).rjust(w_qty)} x {str(price).rjust(w_price)} -"
                # right = f"{subtotal}".rjust(w_subt)
                # lines.append(left + " " + right)
            
            # if disc > 0:
            #     subtotal_after = max(0, subtotal - disc_value)
            #     left = f"{str(qty).rjust(w_qty)} x {str(price).rjust(w_price)} -"
            #     right = f"{subtotal}".rjust(w_subt)
            #     lines.append(left + " " + right)
            subtotal_after = max(0, subtotal - disc_value)
            left = f"{str(qty).rjust(w_qty)} x {str(price).rjust(w_price)} -"
            right = f"{subtotal}".rjust(w_subt)
            lines.append(left + " " + right)

            if disc > 0:
                left = "DISKON".ljust(w_qty + 3 + w_price + 2)
                right = ("-" + self.rupiah(disc_value)).rjust(w_subt)
                lines.append(left + right)
            if is_free:
                lines.append(name)
                lines.append("FREE ITEM".ljust(cols))
                continue

                # left = "SUBTOTAL".ljust(w_qty + 3 + w_price + 2)
                # right = f"{subtotal_after}".rjust(w_subt)
                # lines.append(left + right)

                # total += subtotal_after
            left = "SUBTOTAL".ljust(w_qty + 3 + w_price + 2)
            right = f"{subtotal_after}".rjust(w_subt)
            lines.append(left + right)

            total += subtotal_after

            

        lines.append(sep_d)

        # # Ringkasan
        # ppn = int(total * 0.11)
        # grand = total + ppn
        # Ringkasan (edit by dodo)
        total = int(transaksi_data_dict.get("transaksi_bulat", 0))
        ppn_persen = int(transaksi_data_dict.get("ppn_persen",0))
        print(f'ppn persen = {transaksi_data_dict.get("ppn_persen",0)}')
        ppn = ppn_persen #  int(total * (ppn_persen / 100 ) )
        print(f'ppn nilai = {ppn}')
        diskon_tambahan_persen = int(transaksi_data_dict.get("diskon_persen",0))
        print(f'diskon tambahan persen = {transaksi_data_dict.get("diskon_persen",0)}')
        diskon_tambahan_rp = diskon_tambahan_persen * total / 100
        print(f'diskon tambahan rp = {diskon_tambahan_rp}')

        total_bayar = int(transaksi_data_dict.get("transaksi_nilai",0))
        grand = total_bayar


        amt_w = min(14, max(10, int(cols * 0.38)))
        lbl_w = max(10, cols - amt_w)

        def line_amount(label: str, amount: int) -> None:
            lbl = (label + ":").ljust(lbl_w)
            amt = self.rupiah(amount).rjust(amt_w)
            lines.append(lbl + amt)

        line_amount("Total Belanja", total)
        line_amount("PPN 11%", ppn)
        # tambahan by dodo 
        line_amount("Diskon tambahan ",diskon_tambahan_rp)
        # line_amount("TOtal harus  bayar ",total_bayar)

        lines.append(sep_d)
        lines.append("<b>" + ("TOTAL:".ljust(lbl_w)) + self.rupiah(grand).rjust(amt_w) + "</b>")

        # Pembayaran
        method = (payment_info or {}).get("method", "Debit Card")
        card_brand = (payment_info or {}).get("card_brand", "BANK")
        last4 = (payment_info or {}).get("last4", "XXXX")
        appr = (payment_info or {}).get("approval_code", "APPROVED")
        lines.append("")
        lines.append(f"Bayar : {method}")
        if method.lower() in ("debit", "kredit", "credit"):
            lines.append(f"Bank  : {card_brand} •••• {last4}")
            lines.append(f"Auth  : {appr}")

        lines.append("")
        lines.append(sep_eq)
        lines.append(f"Wi-Fi Gratis: {wifi_code or '-'}")
        lines.append("Scan QR di bawah untuk info/garansi")
        lines.append(sep_eq)

        # ---------- QR block ----------
        data_uri = self._qr_png_base64(qr_data or "")
        if data_uri:
            qr_block = (
                '<img src="' + data_uri +
                '" alt="QR" style="display:block;margin:8px auto;width:160px;height:160px;" />'
            )
        else:
            qr_block = (
                '<div style="width:160px;height:160px;border:2px dashed #000;'
                'margin:8px auto;display:flex;align-items:center;justify-content:center;">'
                '<div style="font-size:10pt;text-align:center;">QR CODE</div></div>'
            )

        # ---------- HTML: header & footer dinamis ----------
        html_head = """
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body { margin:0; padding:0; }
    .hdr { text-align:center; font-weight:bold; font-size: 12pt; line-height:1.2; margin: 0 0 4px 0; }
    .sub { text-align:center; font-size: 10pt; line-height:1.2; margin: 0 0 6px 0; }
    pre  {
        white-space: pre-wrap;
        font-family: "DejaVu Sans Mono","Courier New", monospace;
        font-size: 10pt;
        line-height: 1.5;
        margin: 0;
    }
    .ftr { text-align:center; font-weight:bold; margin-top:6px; }
    
    img.logo {
    display: block;
    margin: 0 auto 6px auto;
    max-width: 100px;     /* batas lebar logo */
    max-height: 60px;     /* batas tinggi logo */
    width: auto;
    height: auto;
    object-fit: contain;
    }

    </style>
    </head>
    <body>
    """
    #img.logo { display:block; margin:0 auto 6px auto; max-height:60px; }

        # # Logo (jika ada)
        # logo_html = ""
        # logo_path = setting.get("logo", "")
        # if logo_path and os.path.exists(logo_path):
        #     import base64
        #     with open(logo_path, "rb") as f:
        #         b64 = base64.b64encode(f.read()).decode("ascii")
        #     logo_html = f'<img src="data:image/png;base64,{b64}" class="logo" />'

        # # Logo (jika ada, dengan fallback ke resources/logo/)
        # logo_html = ""
        # logo_path = setting.get("logo", "")
        # if logo_path:
        #     import base64
        #     import os
        #     # Jika path relatif atau hanya nama file → cari di resources/logo/
        #     if not os.path.isabs(logo_path):
        #         base_dir = os.path.dirname(os.path.abspath(__file__))
        #         candidate_path = os.path.join(base_dir, "..", "resources", "logo", logo_path)
        #         if os.path.exists(candidate_path):
        #             logo_path = candidate_path
        #     # Jika sudah valid path
        #     if os.path.exists(logo_path):
        #         try:
        #             with open(logo_path, "rb") as f:
        #                 b64 = base64.b64encode(f.read()).decode("ascii")
        #             logo_html = f'<img src="data:image/png;base64,{b64}" class="logo" />'
        #         except Exception as e:
        #             print(f"‼️ Gagal load logo: {e}")

        # # Logo (jika ada, dengan fallback ke resources/logo/)
        # # Logo (jika ada, dengan fallback ke resources/logo/ atau URL)
        # logo_html = ""
        # logo_val = (setting.get("logo") or "").strip()
        # print(f'logo val nya = {logo_val}')
        # if logo_val:
        #     import base64, os
        #     if logo_val.lower().startswith("http://") or logo_val.lower().startswith("https://"):
        #         # Kalau URL, langsung embed pakai <img src="url">
        #         logo_html = f'<img src="{logo_val}" class="logo" />'
        #     else:
        #         # Kalau path lokal
        #         if not os.path.isabs(logo_val):
        #             base_dir = os.path.dirname(os.path.abspath(__file__))
        #             candidate_path = os.path.abspath(
        #                 os.path.join(base_dir, "..", "resources", "logo", logo_val)
        #             )
        #         else:
        #             candidate_path = logo_val

        #         print(f"[DEBUG] Cari logo di: {candidate_path}")

        #         if os.path.exists(candidate_path):
        #             try:
        #                 with open(candidate_path, "rb") as f:
        #                     b64 = base64.b64encode(f.read()).decode("ascii")
        #                 logo_html = f'<img src="data:image/png;base64,{b64}" class="logo" />'
        #             except Exception as e:
        #                 print(f"‼️ Gagal load logo: {e}")
        #         else:
        #             print("⚠️ File logo tidak ditemukan:", candidate_path)
        # ---------- Logo (lokal / URL) ----------
        logo_html = ""
        logo_val = (setting.get("logo") or "").strip()

        if logo_val:
            import base64, os
            try:
                if logo_val.lower().startswith("http://") or logo_val.lower().startswith("https://"):
                    # Unduh logo dari URL
                    import requests
                    resp = requests.get(logo_val, timeout=5)
                    if resp.status_code == 200:
                        b64 = base64.b64encode(resp.content).decode("ascii")
                        logo_html = f'<img src="data:image/png;base64,{b64}" class="logo" />'
                    else:
                        print(f"⚠️ Gagal download logo URL: status {resp.status_code}")
                else:
                    # Path lokal
                    if not os.path.isabs(logo_val):
                        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        candidate_path = os.path.join(root_dir, "resources", "logo", logo_val)
                    else:
                        candidate_path = logo_val

                    print(f"[DEBUG] Cari logo di: {candidate_path}")

                    if os.path.exists(candidate_path):
                        with open(candidate_path, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode("ascii")
                        logo_html = f'<img src="data:image/png;base64,{b64}" class="logo" />'
                    else:
                        print("⚠️ File logo tidak ditemukan:", candidate_path)
            except Exception as e:
                print(f"‼️ Error load logo: {e}")


        # Header toko
        headers = []
        for key in ("header1", "header2", "header3"):
            if setting.get(key):
                headers.append(f'<div class="hdr">{setting[key]}</div>')
        header_block = "\n".join(headers)

        # Info invoice
        nomor = transaksi_data_dict.get("nomer", "")
        dtime = transaksi_data_dict.get("dtime", "")
        try:
            waktu = datetime.strptime(dtime, "%Y-%m-%d %H:%M:%S")
            waktu_str = waktu.strftime("%d/%m/%Y %H:%M")
        except Exception:
            waktu_str = dtime
        kasir = transaksi_data_dict.get("oleh_nama", "")
        customer = transaksi_data_dict.get("customers_nama", "")

        info_block = (
            '<div class="sub"><b>INVOICE</b></div>'
            f'<div class="sub">{nomor}</div>'
            f'<div class="sub">{waktu_str} | {kasir}</div>'
            f'<div class="sub">{customer}</div>'
        )

        pre_block = "<pre>" + "\n".join(lines) + "</pre>"

        footer_lines = []
        for key in ("footer1", "footer2", "footer3"):
            if setting.get(key):
                footer_lines.append(f'<div class="ftr">{setting[key]}</div>')
        footer_html = "\n".join(footer_lines) or '<div class="ftr">Terima kasih :)</div>'

        html_tail = "</body></html>"
        # print(f'logo html = {logo_html}')
        return html_head + logo_html + header_block + info_block + pre_block + qr_block + footer_html + html_tail

    # ------------------ helpers dokumen & render ------------------
    # def _create_doc(self, items, payment, wifi_code, qr_data, cols) -> QTextDocument:
    #     doc = QTextDocument()
    #     doc.setHtml(self._build_receipt_html(items, payment, wifi_code, qr_data, cols))
    #     doc.setDocumentMargin(0)
    #     return doc
    def _create_doc(self,items: List[Dict],payment: Dict,wifi_code: str,qr_data: str,cols: int,setting: Dict,transaksi_data_dict: Dict) -> QTextDocument:
        """Buat QTextDocument berisi struk HTML dengan setting & transaksi nyata."""
        html = self._build_receipt_html(
            items, payment, wifi_code, qr_data, cols,
            setting=setting,
            transaksi_data_dict=transaksi_data_dict
        )
        doc = QTextDocument()
        doc.setHtml(html)
        doc.setDocumentMargin(0)
        return doc


    def _render_doc_to_printer(self, printer: QPrinter, doc: QTextDocument) -> bool:
        # Lebar area yang benar-benar bisa digambar (tanpa margin)
        try:
            paint_w_pt = float(printer.pageLayout().paintRect(QPageLayout.Point).width())
        except Exception:
            paint_w_pt = float(printer.pageRect(QPrinter.Point).width())

        if paint_w_pt > 0:
            doc.setTextWidth(paint_w_pt)
            doc.setPageSize(QSizeF(paint_w_pt, 1_000_000.0))  # kertas gulungan

        painter = QPainter(printer)
        if not painter.isActive():
            return False
        doc.drawContents(painter)
        painter.end()
        return True

    # ------------------ PREVIEW ------------------
    def preview_print(self, index: int, parent=None) -> bool:
        printers = self.model.load_printers()
        if not (0 <= index < len(printers)):
            return False

        cfg = printers[index]
        paper_label = cfg.get("paper_size", "")

        # Map label -> lebar mm
        label = (paper_label or "").lower().strip()
        if label in ("56", "56mm"):
            w_mm = 56.0
        elif label in ("58", "58mm"):
            w_mm = 58.0
        elif label in ("80", "80mm"):
            w_mm = 80.0
        elif label in ("100x150", "100x150mm"):
            w_mm = 100.0
        else:
            w_mm = 58.0

        # 1) Printer khusus PREVIEW (PdfFormat) dengan ukuran roll
        preview_printer = self._make_preview_printer(w_mm)

        # 2) Data contoh (ganti dengan data real jika perlu)
        items = [
            {"name": "Aqua Botol 600ml", "qty": 2, "price": 4500, "disc": 1000, "free": False},
            {"name": "Indomie Goreng",   "qty": 5, "price": 3000, "disc": 0,    "free": False},
            {"name": "Taro Snack",       "qty": 1, "price": 7000, "disc": 0,    "free": True},
            {"name": "Silverqueen 58g",  "qty": 1, "price": 14500,"disc": 1500, "free": False},
        ]
        payment = {"method": "Debit Card", "card_brand": "BCA", "last4": "1234", "approval_code": "A1B2C3"}
        wifi_code = "WIFI-9F3K-72BA"
        qr_data = "https://contoh.toko/struk/INV-23001?wifi=" + wifi_code

        cols = self._estimate_cols(preview_printer, css_font_pt=10.0, family="DejaVu Sans Mono", paper_label=paper_label)
        # doc = self._create_doc(items, payment, wifi_code, qr_data, cols)
        # Data dummy untuk preview
        setting = {
            "header1": "CV. SUMBER BOGA",
            "header2": "Jl. Kapten Patimura No 232, Purwokerto Barat",
            "header3": "Telp: 0811-26-99-776",
            "footer1": "BARANG YANG SUDAH DIBELI TIDAK DAPAT DITUKAR / DIKEMBALIKAN",
            "footer2": "IG: @sumberboga_karanglewas",
            "footer3": "Terima kasih atas kunjungan Anda!",
            "logo": "logo_boga_ori.png"
        }

        transaksi_data_dict = {
            "nomer": "INV-TEST-001",
            "dtime": QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "oleh_nama": "Kasir Demo",
            "customers_nama": "Customer Preview",
            "transaksi_bulat": 100000,
            "ppn_persen": 11,
            "diskon_persen": 5,
            "transaksi_nilai": 95000
        }

        doc = self._create_doc(items, payment, wifi_code, qr_data, cols, setting, transaksi_data_dict)


        # (opsional) kunci lebar doc ke lebar roll dalam point agar preview pasti pas
        w_pt = self._mm_to_points(w_mm)
        doc.setTextWidth(w_pt)
        doc.setPageSize(QSizeF(w_pt, 1_000_000.0))

        preview = QPrintPreviewDialog(preview_printer, parent)
        preview.setWindowTitle("Preview Struk")
        try:
            preview.setZoomMode(QPrintPreviewDialog.FitToWidth)
        except Exception:
            pass
        preview.paintRequested.connect(lambda p: self._render_doc_to_printer(p, doc))
        preview.exec()
        return True
    # from PySide6.QtPrintSupport import QPrinterInfo

    # def _get_default_printer_name(self):
    #     """Kembalikan nama printer default sistem (jika ada)."""
    #     try:
    #         default_info = QPrinterInfo.defaultPrinter()
    #         if default_info and default_info.isNull() is False:
    #             return default_info.printerName()
    #     except Exception as e:
    #         print(f"[Printer] Gagal ambil default printer: {e}")
    #     return None
    # review tim 1 #1 tanggal 1 oki 2025 
    def _get_default_printer_name(self):
        """
        Ambil default printer dari aplikasi (printers.json) dulu.
        Jika tidak ditemukan atau tidak tersedia di sistem, fallback ke default printer Windows.
        """
        import json, os
        from PySide6.QtPrintSupport import QPrinterInfo

        try:
            printers_file = os.path.join(os.path.dirname(__file__), "..", "resources", "printers.json")
            if os.path.exists(printers_file):
                with open(printers_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for p in data.get("printers", []):
                        if p.get("default", False):
                            app_default = p.get("name")
                            # cek apakah printer ini benar-benar tersedia di sistem
                            available = [x.printerName() for x in QPrinterInfo.availablePrinters()]
                            if app_default in available:
                                print(f"[Printer] Default printer dari aplikasi: {app_default}")
                                return app_default
                            else:
                                print(f"[Printer] Default printer di JSON tidak ditemukan di sistem: {app_default}")

            # fallback ke default printer sistem
            default_info = QPrinterInfo.defaultPrinter()
            if default_info and not default_info.isNull():
                sys_default = default_info.printerName()
                print(f"[Printer] Default printer dari sistem: {sys_default}")
                return sys_default
        except Exception as e:
            print(f"[Printer] Gagal ambil default printer: {e}")

        print("[Printer] Tidak ada default printer ditemukan.")
        return None


    # ------------------ CETAK LANGSUNG (Test Print) ------------------
    def test_print(self, index: int) -> bool:
        from PySide6.QtPrintSupport import QPrinter, QPrinterInfo  # pastikan ini di atas
        infos = QPrinterInfo.availablePrinters()
        print("[Printer List Detected by Qt:]")
        for p in infos:
            print(" -", p.printerName())



        printers = self.model.load_printers()
        if not (0 <= index < len(printers)):
            return False

        cfg = printers[index]
        printer_name = cfg.get("name", "")
        paper_label = cfg.get("paper_size", "")

        # from PySide6.QtPrintSupport import QPrinter, QPrinterInfo

        printer = QPrinter(QPrinter.HighResolution)

        # Ambil printer default sistem (misal EPPOS 58)
        default_name = self._get_default_printer_name()
        if default_name:
            printer.setPrinterName(default_name)
            print(f"[Printer] Default printer terdeteksi: {default_name}")
        else:
            print("[Printer] ⚠️ Tidak ada printer default, fallback ke PDF.")
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName("test_output.pdf")

        # Pastikan gunakan NativeFormat untuk kirim langsung ke printer fisik
        try:
            printer.setOutputFormat(QPrinter.NativeFormat)
        except Exception:
            pass

        # Terapkan ukuran kertas
        self._apply_paper_size(printer, cfg.get("paper_size", "80"))

        # printer = QPrinter(QPrinter.HighResolution)
        # printer.setPrinterName(printer_name)
        printer.setResolution(203)
        # pastikan format native untuk cetak nyata
        try:
            printer.setOutputFormat(QPrinter.NativeFormat)
        except Exception:
            pass
        self._apply_paper_size(printer, paper_label)

        items = [
            {"name": "Aqua Botol 600ml", "qty": 2, "price": 4500, "disc": 1000, "free": False},
            {"name": "Indomie Goreng",   "qty": 5, "price": 3000, "disc": 0,    "free": False},
            {"name": "Taro Snack",       "qty": 1, "price": 7000, "disc": 0,    "free": True},
            {"name": "Silverqueen 58g",  "qty": 1, "price": 14500,"disc": 1500, "free": False},
        ]
        payment = {"method": "Debit Card", "card_brand": "BCA", "last4": "1234", "approval_code": "A1B2C3"}
        wifi_code = "WIFI-9F3K-72BA"
        qr_data = "https://contoh.toko/struk/INV-23001?wifi=" + wifi_code

        cols = self._estimate_cols(printer, css_font_pt=10.0, family="DejaVu Sans Mono", paper_label=paper_label)
        # doc = self._create_doc(items, payment, wifi_code, qr_data, cols)
        setting = {
            "header1": "CV. SUMBER BOGA",
            "header2": "Jl. Kapten Patimura No 232, Purwokerto Barat",
            "header3": "Telp: 0811-26-99-776",
            "footer1": "BARANG YANG SUDAH DIBELI TIDAK DAPAT DITUKAR / DIKEMBALIKAN",
            "footer2": "IG: @sumberboga_karanglewas",
            "footer3": "Terima kasih atas kunjungan Anda!",
            "logo": "logo_boga_ori.png"
        }

        transaksi_data_dict = {
            "nomer": "INV-TEST-001",
            "dtime": QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "oleh_nama": "Kasir Demo",
            "customers_nama": "Customer Test",
            "transaksi_bulat": 100000,
            "ppn_persen": 11,
            "diskon_persen": 5,
            "transaksi_nilai": 95000
        }

        doc = self._create_doc(items, payment, wifi_code, qr_data, cols, setting, transaksi_data_dict)


        try:
            return self._render_doc_to_printer(printer, doc)
        except Exception as e:
            print(f"[TestPrint] Print error: {e}")
            return False

#     from PySide6.QtPrintSupport import QPrinterInfo
# from PySide6.QtWidgets import QMessageBox

# class PrinterSettingsController:
#     ...
# review tim 1 nomor 1 tanggal 1 oki 2025

    # ------------------ ambil printer default ------------------
    def get_default_printer(self) -> Optional[Dict]:
        printers = self.model.load_printers()
        for p in printers:
            if p.get("default"):
                return p

        # fallback ke default printer OS
        try:
            sys_printer = QPrinterInfo.defaultPrinter()
            if not sys_printer.isNull():
                return {
                    "name": sys_printer.printerName(),
                    "paper_size": "80mm",  # default asumsi, bisa kamu ganti
                    "default": True
                }
        except Exception:
            pass
        return None

    # ------------------ cetak langsung ------------------
    def print_struk(self, items, payment, wifi_code, qr_data, setting, transaksi_data_dict, copy_no: int = 0) -> bool:
        cfg = self.get_default_printer()
        if not cfg:
            QMessageBox.warning(None, "Printer", "⚠️ Belum ada default printer, silakan setting dulu!")
            return False

        printer_name = cfg.get("name", "")
        paper_label = cfg.get("paper_size", "")

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPrinterName(printer_name)
        printer.setResolution(203)
        try:
            printer.setOutputFormat(QPrinter.NativeFormat)
        except Exception:
            pass
        self._apply_paper_size(printer, paper_label)

        # hitung kolom
        cols = self._estimate_cols(printer, css_font_pt=10.0, family="DejaVu Sans Mono", paper_label=paper_label)

        # buat doc
        doc = self._create_doc(items, payment, wifi_code, qr_data, cols, setting, transaksi_data_dict)

        # tambahkan tanda copy jika perlu
        if copy_no > 0:
            html = doc.toHtml()
            html = html.replace("<body>", f"<body><div class='hdr'>*** COPY KE-{copy_no} ***</div>")
            doc.setHtml(html)

        try:
            return self._render_doc_to_printer(printer, doc)
        except Exception as e:
            print(f"[PrintStruk] Error cetak: {e}")
            return False

