from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QAbstractItemView
)
from PySide6.QtCore import Qt

class CustomerSearchView(QDialog):
    def __init__(self, controller, customer_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cari Customer (F3)")
        self.controller = controller
        self.customer_list = customer_list

        self.selected_customer_id = None

        layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik keyword untuk cari ID, Nama, Alamat, atau Telepon")
        self.search_input.textChanged.connect(self.controller.filter_table)
        layout.addWidget(self.search_input)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Alamat", "Telepon"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellClicked.connect(self.controller.handle_cell_clicked)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.resize(600, 400)
        # self.table.setFocus()
        self.search_input.setFocus()      # ✅ Fokus ke kolom pencarian

    def keyPressEvent(self, event):
        self.controller.key_pressed(event)

    def get_selected_customer_id(self):
        return self.selected_customer_id
