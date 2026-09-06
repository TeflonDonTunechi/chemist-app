# src/views/herbs_view.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLabel)
from PyQt6.QtCore import Qt
from src.database import Session
from src.models import Herb

class HerbsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        search_layout = QHBoxLayout()
        self.search_line = QLineEdit()
        self.search_line.setPlaceholderText("Search herbs by name or scientific name...")
        self.search_line.textChanged.connect(self.load_herbs)
        search_layout.addWidget(self.search_line)
        self.layout().addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Name", "Scientific Name", "Category", "Uses", "Contraindications", "Unit Price"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout().addWidget(self.table)

        self.load_herbs()

    def load_herbs(self):
        query = self.search_line.text().strip()
        sess = Session()
        herbs_query = sess.query(Herb)
        if query:
            herbs_query = herbs_query.filter(
                Herb.name.ilike(f'%{query}%') |
                Herb.scientific_name.ilike(f'%{query}%') |
                Herb.category.ilike(f'%{query}%')
            )
        herbs = herbs_query.order_by(Herb.name).all()
        self.table.setRowCount(len(herbs))
        for row, herb in enumerate(herbs):
            self.table.setItem(row, 0, QTableWidgetItem(herb.name))
            self.table.setItem(row, 1, QTableWidgetItem(herb.scientific_name or ''))
            self.table.setItem(row, 2, QTableWidgetItem(herb.category or ''))
            self.table.setItem(row, 3, QTableWidgetItem(herb.uses or ''))
            self.table.setItem(row, 4, QTableWidgetItem(herb.contraindications or ''))
            self.table.setItem(row, 5, QTableWidgetItem(f"${herb.unit_price:.2f}" if herb.unit_price else ''))
        sess.close()