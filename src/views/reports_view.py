from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
                             QLabel, QTabWidget, QComboBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from src.database import Session
from src.models import Sale, SaleItem, StockLot, User, Drug
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

class ReportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.tabs = QTabWidget()
        self.layout().addWidget(self.tabs)

        # ----- Sales Report Tab -----
        self.sales_tab = QWidget()
        sales_layout = QVBoxLayout()
        self.sales_tab.setLayout(sales_layout)
        
        # Filter layout
        filter_layout = QHBoxLayout()
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        
        # Cashier filter
        self.cashier_combo = QComboBox()
        self.cashier_combo.addItem("All Cashiers", None)
        sess = Session()
        users = sess.query(User).all()
        for u in users:
            self.cashier_combo.addItem(f"{u.username} ({u.role})", u.id)
        sess.close()
        
        self.load_sales_btn = QPushButton("Load Sales")
        self.load_sales_btn.clicked.connect(self.load_sales)
        self.print_sales_btn = QPushButton("Print Sales (PDF)")
        self.print_sales_btn.clicked.connect(self.print_sales)
        
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.from_date)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.to_date)
        filter_layout.addWidget(QLabel("Cashier:"))
        filter_layout.addWidget(self.cashier_combo)
        filter_layout.addWidget(self.load_sales_btn)
        filter_layout.addWidget(self.print_sales_btn)
        sales_layout.addLayout(filter_layout)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["Sale ID", "Date", "Cashier", "Total (KES)", "Items"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        sales_layout.addWidget(self.sales_table)
        self.tabs.addTab(self.sales_tab, "Sales History")

        # ----- Expiry Report Tab -----
        self.expiry_tab = QWidget()
        expiry_layout = QVBoxLayout()
        self.expiry_tab.setLayout(expiry_layout)
        
        expiry_btn_layout = QHBoxLayout()
        self.load_expiry_btn = QPushButton("Load Expiring Lots (90 days)")
        self.load_expiry_btn.clicked.connect(self.load_expiry)
        self.print_expiry_btn = QPushButton("Print Expiry Report (PDF)")
        self.print_expiry_btn.clicked.connect(self.print_expiry)
        expiry_btn_layout.addWidget(self.load_expiry_btn)
        expiry_btn_layout.addWidget(self.print_expiry_btn)
        expiry_layout.addLayout(expiry_btn_layout)

        self.expiry_table = QTableWidget()
        self.expiry_table.setColumnCount(5)
        self.expiry_table.setHorizontalHeaderLabels(["Drug", "Quantity", "Expiry Date", "Days Left", "Status"])
        self.expiry_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        expiry_layout.addWidget(self.expiry_table)
        self.tabs.addTab(self.expiry_tab, "Expiry Report")

        # Load initial data
        self.load_sales()
        self.load_expiry()

    def load_sales(self):
        from_date = self.from_date.date().toPyDate()
        to_date = self.to_date.date().toPyDate()
        cashier_id = self.cashier_combo.currentData()
        
        sess = Session()
        query = sess.query(Sale).filter(Sale.timestamp >= from_date, Sale.timestamp <= to_date)
        if cashier_id:
            query = query.filter(Sale.cashier_id == cashier_id)
        sales = query.order_by(Sale.timestamp.desc()).all()
        
        self.sales_table.setRowCount(len(sales))
        for row, sale in enumerate(sales):
            cashier = sess.query(User).get(sale.cashier_id)
            item_count = sess.query(SaleItem).filter(SaleItem.sale_id == sale.id).count()
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale.id)))
            self.sales_table.setItem(row, 1, QTableWidgetItem(sale.timestamp.strftime('%Y-%m-%d %H:%M')))
            self.sales_table.setItem(row, 2, QTableWidgetItem(cashier.username if cashier else 'Unknown'))
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"{sale.total_amount:.2f}"))
            self.sales_table.setItem(row, 4, QTableWidgetItem(str(item_count)))
        sess.close()

    def print_sales(self):
        if self.sales_table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "No sales to print.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Sales Report", 
            f"sales_report_{datetime.now().strftime('%Y%m%d')}.pdf", 
            "PDF Files (*.pdf)"
        )
        if not filepath:
            return
        
        try:
            self._generate_sales_pdf(filepath)
            QMessageBox.information(self, "Success", f"Report saved to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{str(e)}")

    def _generate_sales_pdf(self, filepath):
        c = canvas.Canvas(filepath, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height-2*cm, "Sales Report - Zeitgeist Teflon Pharma")
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, height-2.7*cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(2*cm, height-3.4*cm, f"Period: {self.from_date.date().toPyDate()} to {self.to_date.date().toPyDate()}")
        cashier_text = self.cashier_combo.currentText()
        c.drawString(2*cm, height-4.1*cm, f"Cashier: {cashier_text}")
        
        y = height - 5.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*cm, y, "ID")
        c.drawString(3*cm, y, "Date")
        c.drawString(8*cm, y, "Cashier")
        c.drawString(14*cm, y, "Total (KES)")
        c.drawString(19*cm, y, "Items")
        y -= 0.5*cm
        c.line(1*cm, y, width-1*cm, y)
        y -= 0.5*cm
        
        c.setFont("Helvetica", 9)
        for row in range(self.sales_table.rowCount()):
            if y < 3*cm:
                c.showPage()
                y = height - 2*cm
                c.setFont("Helvetica", 9)
            c.drawString(1*cm, y, self.sales_table.item(row, 0).text())
            c.drawString(3*cm, y, self.sales_table.item(row, 1).text())
            c.drawString(8*cm, y, self.sales_table.item(row, 2).text())
            c.drawString(14*cm, y, self.sales_table.item(row, 3).text())
            c.drawString(19*cm, y, self.sales_table.item(row, 4).text())
            y -= 0.5*cm
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, 1.5*cm, "Zeitgeist Teflon Pharma © 2026 | All rights reserved.")
        c.save()

    def load_expiry(self):
        sess = Session()
        today = datetime.now().date()
        expiry_limit = today + timedelta(days=90)
        lots = sess.query(StockLot).filter(StockLot.quantity > 0, StockLot.expiry_date <= expiry_limit).order_by(StockLot.expiry_date).all()
        
        self.expiry_table.setRowCount(len(lots))
        for row, lot in enumerate(lots):
            drug = sess.query(Drug).get(lot.drug_id)
            days_left = (lot.expiry_date - today).days
            status = "Critical" if days_left < 30 else "Warning" if days_left < 60 else "OK"
            
            self.expiry_table.setItem(row, 0, QTableWidgetItem(drug.brand_name if drug else 'Unknown'))
            self.expiry_table.setItem(row, 1, QTableWidgetItem(str(lot.quantity)))
            self.expiry_table.setItem(row, 2, QTableWidgetItem(lot.expiry_date.strftime('%Y-%m-%d')))
            self.expiry_table.setItem(row, 3, QTableWidgetItem(str(days_left)))
            status_item = QTableWidgetItem(status)
            if days_left < 30:
                status_item.setBackground(Qt.GlobalColor.red)
            elif days_left < 60:
                status_item.setBackground(Qt.GlobalColor.yellow)
            self.expiry_table.setItem(row, 4, status_item)
        sess.close()

    def print_expiry(self):
        if self.expiry_table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "No expiring items to print.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Expiry Report", 
            f"expiry_report_{datetime.now().strftime('%Y%m%d')}.pdf", 
            "PDF Files (*.pdf)"
        )
        if not filepath:
            return
        
        try:
            self._generate_expiry_pdf(filepath)
            QMessageBox.information(self, "Success", f"Report saved to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{str(e)}")

    def _generate_expiry_pdf(self, filepath):
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height-2*cm, "Expiry Report - Zeitgeist Teflon Pharma")
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, height-2.7*cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        y = height - 4.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y, "Drug")
        c.drawString(8*cm, y, "Quantity")
        c.drawString(11*cm, y, "Expiry Date")
        c.drawString(15*cm, y, "Days Left")
        c.drawString(19*cm, y, "Status")
        y -= 0.5*cm
        c.line(2*cm, y, width-2*cm, y)
        y -= 0.5*cm
        
        c.setFont("Helvetica", 9)
        for row in range(self.expiry_table.rowCount()):
            if y < 3*cm:
                c.showPage()
                y = height - 2*cm
                c.setFont("Helvetica", 9)
            c.drawString(2*cm, y, self.expiry_table.item(row, 0).text())
            c.drawString(8*cm, y, self.expiry_table.item(row, 1).text())
            c.drawString(11*cm, y, self.expiry_table.item(row, 2).text())
            c.drawString(15*cm, y, self.expiry_table.item(row, 3).text())
            status = self.expiry_table.item(row, 4).text()
            if status == "Critical":
                c.setFillColorRGB(1, 0, 0)
            elif status == "Warning":
                c.setFillColorRGB(1, 0.5, 0)
            c.drawString(19*cm, y, status)
            c.setFillColorRGB(0, 0, 0)
            y -= 0.5*cm
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, 1.5*cm, "Zeitgeist Teflon Pharma © 2026 | All rights reserved.")
        c.save()