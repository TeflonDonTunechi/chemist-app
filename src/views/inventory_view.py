from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox, QSpinBox,
    QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from src.database import Session
from src.models import Drug, StockLot
from sqlalchemy import func
from src.utils.drug_importer import import_drugs_from_csv
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


class InventoryWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        # Toolbar
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("Add Drug")
        self.add_btn.clicked.connect(self.add_drug)
        toolbar.addWidget(self.add_btn)

        self.add_stock_btn = QPushButton("Add Stock")
        self.add_stock_btn.clicked.connect(self.add_stock)
        toolbar.addWidget(self.add_stock_btn)

        self.import_drugs_btn = QPushButton("Import Drugs (CSV)")
        self.import_drugs_btn.clicked.connect(self.import_drugs)
        toolbar.addWidget(self.import_drugs_btn)

        self.print_inv_btn = QPushButton("Print Inventory (PDF)")
        self.print_inv_btn.clicked.connect(self.print_inventory)
        toolbar.addWidget(self.print_inv_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(self.refresh_btn)

        self.layout().addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Brand", "Drug", "Strength", "Unit Price", "Stock", "Next Expiry"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout().addWidget(self.table)

        # Double-click to edit (admin only)
        if self.user.role == 'admin':
            self.table.doubleClicked.connect(self.edit_drug)

        self.load_data()

    def load_data(self):
        sess = Session()
        drugs = sess.query(Drug).all()
        self.table.setRowCount(len(drugs))
        for row, drug in enumerate(drugs):
            total_qty = sess.query(func.coalesce(func.sum(StockLot.quantity), 0)).filter(
                StockLot.drug_id == drug.id
            ).scalar()
            next_expiry = sess.query(StockLot).filter(
                StockLot.drug_id == drug.id,
                StockLot.quantity > 0
            ).order_by(StockLot.expiry_date).first()
            expiry_str = next_expiry.expiry_date.strftime('%Y-%m-%d') if next_expiry else 'N/A'
            self.table.setItem(row, 0, QTableWidgetItem(str(drug.id)))
            self.table.setItem(row, 1, QTableWidgetItem(drug.brand_name))
            self.table.setItem(row, 2, QTableWidgetItem(drug.drug_name))
            self.table.setItem(row, 3, QTableWidgetItem(drug.strength or ''))
            self.table.setItem(row, 4, QTableWidgetItem(f"{drug.unit_price:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(total_qty)))
            self.table.setItem(row, 6, QTableWidgetItem(expiry_str))
        sess.close()

    def add_drug(self):
        if self.user.role != 'admin':
            QMessageBox.warning(self, "Permission", "Admin only")
            return
        dialog = DrugEditDialog(parent=self)
        if dialog.exec():
            self.load_data()

    def add_stock(self):
        if self.user.role != 'admin':
            QMessageBox.warning(self, "Permission", "Admin only")
            return
        dialog = StockAddDialog(parent=self)
        if dialog.exec():
            self.load_data()

    def edit_drug(self, index):
        if self.user.role != 'admin':
            return
        row = index.row()
        drug_id = int(self.table.item(row, 0).text())
        sess = Session()
        drug = sess.query(Drug).get(drug_id)
        sess.close()
        if drug:
            dialog = DrugEditDialog(drug, parent=self)
            if dialog.exec():
                self.load_data()

    def delete_drug(self, drug_id):
        if self.user.role != 'admin':
            return
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Delete this drug and all stock lots?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            sess = Session()
            drug = sess.query(Drug).get(drug_id)
            if drug:
                sess.query(StockLot).filter_by(drug_id=drug_id).delete()
                sess.delete(drug)
                sess.commit()
                QMessageBox.information(self, "Deleted", "Drug deleted.")
            sess.close()
            self.load_data()

    def import_drugs(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select Drugs CSV",
            "",
            "CSV Files (*.csv)"
        )
        if filepath:
            try:
                count = import_drugs_from_csv(filepath)
                QMessageBox.information(self, "Success", f"Imported {count} drugs.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def print_inventory(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "No inventory to print.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Inventory Report", 
            f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", 
            "PDF Files (*.pdf)"
        )
        if not filepath:
            return
        
        try:
            self._generate_inventory_pdf(filepath)
            QMessageBox.information(self, "Success", f"Inventory saved to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{str(e)}")

    def _generate_inventory_pdf(self, filepath):
        c = canvas.Canvas(filepath, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height-2*cm, "Inventory Report - Zeitgeist Teflon Pharma")
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, height-2.7*cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(2*cm, height-3.4*cm, f"Total Drugs: {self.table.rowCount()}")
        
        y = height - 5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*cm, y, "ID")
        c.drawString(3*cm, y, "Brand")
        c.drawString(7*cm, y, "Drug")
        c.drawString(11*cm, y, "Strength")
        c.drawString(15*cm, y, "Price (KES)")
        c.drawString(19*cm, y, "Stock")
        c.drawString(23*cm, y, "Next Expiry")
        y -= 0.5*cm
        c.line(1*cm, y, width-1*cm, y)
        y -= 0.5*cm
        
        c.setFont("Helvetica", 9)
        for row in range(self.table.rowCount()):
            if y < 3*cm:
                c.showPage()
                y = height - 2*cm
                c.setFont("Helvetica", 9)
            c.drawString(1*cm, y, self.table.item(row, 0).text())
            c.drawString(3*cm, y, self.table.item(row, 1).text())
            c.drawString(7*cm, y, self.table.item(row, 2).text())
            c.drawString(11*cm, y, self.table.item(row, 3).text())
            c.drawString(15*cm, y, self.table.item(row, 4).text())
            c.drawString(19*cm, y, self.table.item(row, 5).text())
            c.drawString(23*cm, y, self.table.item(row, 6).text())
            y -= 0.5*cm
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(2*cm, 1.5*cm, "Zeitgeist Teflon Pharma © 2026 | All rights reserved.")
        c.save()


# ---------- Helper Dialogs ----------
class DrugEditDialog(QDialog):
    def __init__(self, drug=None, parent=None):
        super().__init__(parent)
        self.drug = drug
        self.setWindowTitle("Add/Edit Drug")
        self.setModal(True)
        layout = QFormLayout()
        self.brand_name = QLineEdit()
        self.drug_name = QLineEdit()
        self.strength = QLineEdit()
        self.dosing_bands = QLineEdit()
        self.moa = QLineEdit()
        self.unit_price = QLineEdit()
        if drug:
            self.brand_name.setText(drug.brand_name)
            self.drug_name.setText(drug.drug_name)
            self.strength.setText(drug.strength or '')
            self.dosing_bands.setText(drug.dosing_bands or '')
            self.moa.setText(drug.moa or '')
            self.unit_price.setText(str(drug.unit_price))
        layout.addRow("Brand Name:", self.brand_name)
        layout.addRow("Drug Name:", self.drug_name)
        layout.addRow("Strength:", self.strength)
        layout.addRow("Dosing Bands:", self.dosing_bands)
        layout.addRow("MOA:", self.moa)
        layout.addRow("Unit Price (KES):", self.unit_price)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save)
        layout.addRow(self.save_btn)
        self.setLayout(layout)

    def save(self):
        try:
            price = float(self.unit_price.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid price")
            return
        sess = Session()
        if self.drug:
            drug = sess.query(Drug).get(self.drug.id)
            drug.brand_name = self.brand_name.text()
            drug.drug_name = self.drug_name.text()
            drug.strength = self.strength.text()
            drug.dosing_bands = self.dosing_bands.text()
            drug.moa = self.moa.text()
            drug.unit_price = price
        else:
            drug = Drug(
                brand_name=self.brand_name.text(),
                drug_name=self.drug_name.text(),
                strength=self.strength.text(),
                dosing_bands=self.dosing_bands.text(),
                moa=self.moa.text(),
                unit_price=price
            )
            sess.add(drug)
        sess.commit()
        sess.close()
        self.accept()

class StockAddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Stock")
        self.setModal(True)
        layout = QFormLayout()
        self.drug_combo = QComboBox()
        sess = Session()
        drugs = sess.query(Drug).all()
        for d in drugs:
            self.drug_combo.addItem(f"{d.brand_name} ({d.drug_name})", d.id)
        sess.close()
        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(10000)
        self.expiry = QDateEdit()
        self.expiry.setDate(QDate.currentDate().addDays(90))
        self.expiry.setCalendarPopup(True)
        layout.addRow("Drug:", self.drug_combo)
        layout.addRow("Quantity:", self.quantity)
        layout.addRow("Expiry Date:", self.expiry)
        self.save_btn = QPushButton("Add Stock")
        self.save_btn.clicked.connect(self.save)
        layout.addRow(self.save_btn)
        self.setLayout(layout)

    def save(self):
        drug_id = self.drug_combo.currentData()
        qty = self.quantity.value()
        expiry_date = self.expiry.date().toPyDate()
        sess = Session()
        lot = StockLot(drug_id=drug_id, quantity=qty, expiry_date=expiry_date)
        sess.add(lot)
        sess.commit()
        sess.close()
        QMessageBox.information(self, "Success", "Stock added")
        self.accept()