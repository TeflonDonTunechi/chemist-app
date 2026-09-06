from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime, timedelta
from src.database import Session
from src.models import Drug, StockLot, Sale
from sqlalchemy import func
from src.views.graph_widget import SalesGraphWidget

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #6c3b9e; margin: 10px;")
        self.layout().addWidget(title)

        # Stats cards (4 cards)
        self.stats_grid = QGridLayout()
        self.layout().addLayout(self.stats_grid)

        # Graph with time selector
        graph_header = QHBoxLayout()
        graph_label = QLabel("Sales Trend")
        graph_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d2d2d;")
        graph_header.addWidget(graph_label)
        graph_header.addStretch()
        self.time_combo = QComboBox()
        self.time_combo.addItems(["Hourly", "Daily", "Weekly", "Monthly"])
        self.time_combo.currentTextChanged.connect(self.update_graph)
        graph_header.addWidget(self.time_combo)
        self.layout().addLayout(graph_header)

        self.graph = SalesGraphWidget()
        self.layout().addWidget(self.graph)

        # Daily sales total & recent transactions
        bottom_layout = QHBoxLayout()
        self.daily_total_label = QLabel("Daily Sales: KES 0.00")
        self.daily_total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e67e22; padding: 10px; background-color: #2d2d2d; border-radius: 8px;")
        bottom_layout.addWidget(self.daily_total_label)

        # Recent transactions table (last 5)
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(3)
        self.recent_table.setHorizontalHeaderLabels(["Sale ID", "Date", "Amount (KES)"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_table.setMaximumHeight(150)
        self.recent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bottom_layout.addWidget(self.recent_table)
        self.layout().addLayout(bottom_layout)

        # Refresh every 30 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(30000)
        self.refresh_stats()

    def update_graph(self):
        self.graph.load_data(self.time_combo.currentText())

    def refresh_stats(self):
        # Clear and rebuild stats cards
        for i in reversed(range(self.stats_grid.count())):
            widget = self.stats_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        sess = Session()
        total_drugs = sess.query(Drug).count()
        low_stock = sess.query(StockLot.drug_id).group_by(StockLot.drug_id).having(func.sum(StockLot.quantity) < 10).count()
        expiring_soon = sess.query(StockLot).filter(StockLot.expiry_date <= datetime.now().date() + timedelta(days=30)).count()
        sales_today = sess.query(Sale).filter(func.date(Sale.timestamp) == datetime.now().date()).count()
        daily_total = sess.query(func.sum(Sale.total_amount)).filter(func.date(Sale.timestamp) == datetime.now().date()).scalar() or 0.0
        sess.close()

        # Update daily total label
        self.daily_total_label.setText(f"Daily Sales: KES {daily_total:.2f}")

        cards = [
            ("💊", "Total Drugs", total_drugs, "#4a6a8a"),
            ("📦", "Low Stock Items", low_stock, "#e67e22"),
            ("⏳", "Expiring Soon", expiring_soon, "#d9534f"),
            ("💰", "Sales Today", sales_today, "#6c3b9e"),
        ]
        row, col = 0, 0
        for icon, label, value, color in cards:
            card = QWidget()
            card.setObjectName("card")
            card.setStyleSheet(f"""
                background-color: {color};
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
                color: white;
            """)
            card_layout = QVBoxLayout()
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 32px;")
            value_label = QLabel(str(value))
            value_label.setStyleSheet("font-size: 28px; font-weight: bold;")
            label_label = QLabel(label)
            label_label.setStyleSheet("font-size: 14px;")
            card_layout.addWidget(icon_label)
            card_layout.addWidget(value_label)
            card_layout.addWidget(label_label)
            card.setLayout(card_layout)
            self.stats_grid.addWidget(card, row, col)
            col += 1
            if col == 4:
                col = 0
                row += 1

        # Refresh recent transactions
        sess = Session()
        recent = sess.query(Sale).order_by(Sale.timestamp.desc()).limit(5).all()
        self.recent_table.setRowCount(len(recent))
        for row, sale in enumerate(recent):
            self.recent_table.setItem(row, 0, QTableWidgetItem(str(sale.id)))
            self.recent_table.setItem(row, 1, QTableWidgetItem(sale.timestamp.strftime('%Y-%m-%d %H:%M')))
            self.recent_table.setItem(row, 2, QTableWidgetItem(f"{sale.total_amount:.2f}"))
        sess.close()

        # Refresh the graph
        self.graph.load_data(self.time_combo.currentText())