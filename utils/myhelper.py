from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


def set_readonly_style(widget, readonly=True):
    palette = widget.palette()
    bg_color = "#F5F5F5" if readonly else "#FFFFFF"
    palette.setColor(QPalette.Base, QColor(bg_color))
    widget.setPalette(palette)
    print('mau set readonly nya')
    # widget.setReadOnly(readonly)
    # Perlakuan berdasarkan tipe widget
    if isinstance(widget, (QLineEdit, QTextEdit)):
        widget.setReadOnly(readonly)
    elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
        widget.setButtonSymbols(QSpinBox.NoButtons if readonly else QSpinBox.UpDownArrows)
        widget.setFocusPolicy(Qt.NoFocus if readonly else Qt.StrongFocus)
        widget.setEnabled(not readonly)
    else:
        widget.setEnabled(not readonly)

def set_table_row_editable(table, row, editable_column_indexes):
    for col in range(table.columnCount()):
        item = table.item(row, col)
        if not item:
            item = QTableWidgetItem()
            table.setItem(row, col, item)

        if col in editable_column_indexes:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setBackground(QColor("#FFFFFF"))  # putih
        else:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setBackground(QColor("#F5F5F5"))  # abu-abu muda

 
def set_editable_only_column(table, editable_column_index):
    for row in range(table.rowCount()):
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if not item:
                item = QTableWidgetItem()
                table.setItem(row, col, item)

            if col == editable_column_index:
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                item.setBackground(QColor("#FFFFFF"))  # putih
            else:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setBackground(QColor("#F50000"))  # abu-abu muda

