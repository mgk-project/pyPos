from views.customer_search_view import CustomerSearchView
from models.customer_search_model import CustomerSearchModel

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

# class CustomerSearchController:
#     def __init__(self, customer_list, parent=None):
#         self.customer_list = customer_list
#         self.view = CustomerSearchView(self, customer_list, parent)
#         self.populate_table()
class CustomerSearchController:
    def __init__(self, parent=None):
        model = CustomerSearchModel()
        self.customer_list = model.load_all_customers()
        self.view = CustomerSearchView(self, self.customer_list, parent)
        self.populate_table()

    def show(self):
        result = self.view.exec()
        if result == CustomerSearchView.Accepted:
            return self.view.get_selected_customer_id()
        return None

    def populate_table(self):
        self.view.table.setRowCount(0)
        for customer in self.customer_list:
            row = self.view.table.rowCount()
            self.view.table.insertRow(row)
            self.view.table.setItem(row, 0, QTableWidgetItem(str(customer["id"])))
            self.view.table.setItem(row, 1, QTableWidgetItem(customer["nama"]))
            self.view.table.setItem(row, 2, QTableWidgetItem(customer["alamat_1"]))
            self.view.table.setItem(row, 3, QTableWidgetItem(customer["tlp_1"]))
        if self.view.table.rowCount() > 0:
            self.view.table.selectRow(0)

    def filter_table(self, keyword):
        keyword = keyword.lower()
        first_visible_row = -1
        for row in range(self.view.table.rowCount()):
            visible = any(keyword in self.view.table.item(row, col).text().lower()
                          for col in range(4) if self.view.table.item(row, col))
            self.view.table.setRowHidden(row, not visible)
            if visible and first_visible_row == -1:
                first_visible_row = row
        if first_visible_row != -1:
            self.view.table.selectRow(first_visible_row)

    def handle_cell_clicked(self, row, column):
        self.select_row(row)

    def select_row(self, row):
        self.view.selected_customer_id = int(self.view.table.item(row, 0).text())
        self.view.accept()

    def key_pressed(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current_row = self.view.table.currentRow()
            if current_row != -1 and not self.view.table.isRowHidden(current_row):
                self.select_row(current_row)
        elif event.key() == Qt.Key_Escape:
            self.view.reject()
