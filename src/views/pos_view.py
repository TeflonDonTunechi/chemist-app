# src/views/pos_view.py
import os
import tempfile
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt

from src.database import Session
from src.models import Drug, StockLot, Sale, SaleItem
from src.utils.pdf_generator import generate_receipt
from src.views.receipt_preview import ReceiptPreviewDialog
from sqlalchemy import func


class POSWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart = []  # each item: {id, name, qty, price, subtotal}
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---- Search bar ----
        search_layout = QHBoxLayout()
        self.search_line = QLineEdit()
        self.search_line.setPlaceholderText("Search drug by brand or generic name...")
        self.search_line.textChanged.connect(self.search)
        search_layout.addWidget(self.search_line)
        self.layout().addLayout(search_layout)

        # ---- Results list ----
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.add_to_cart)
        self.layout().addWidget(self.results_list)

        # ---- Cart table ----
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Price (KES)", "Subtotal", "Actions"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout().addWidget(self.cart_table)

        # ---- Cart controls ----
        controls = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Cart")
        self.clear_btn.clicked.connect(self.clear_cart)
        self.checkout_btn = QPushButton("Checkout")
        self.checkout_btn.clicked.connect(self.checkout)
        controls.addWidget(self.clear_btn)
        controls.addWidget(self.checkout_btn)
        self.layout().addLayout(controls)

        # Initial search
        self.search()

    def search(self):
        """Search for drugs and populate the results list."""
        query = self.search_line.text().strip()
        self.results_list.clear()
        if len(query) < 2:
            return

        sess = Session()
        drugs = sess.query(Drug).filter(
            Drug.brand_name.ilike(f'%{query}%') |
            Drug.drug_name.ilike(f'%{query}%')
        ).all()

        for drug in drugs:
            stock = sess.query(func.coalesce(func.sum(StockLot.quantity), 0)).filter(
                StockLot.drug_id == drug.id
            ).scalar()
            if stock > 0:
                item_text = (
                    f"{drug.brand_name} ({drug.drug_name}) "
                    f"- {drug.strength or ''} - Stock: {stock} "
                    f"- KES {drug.unit_price:.2f}"
                )
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, {
                    'id': drug.id,
                    'name': f"{drug.brand_name} ({drug.drug_name})",
                    'price': drug.unit_price
                })
                self.results_list.addItem(item)
        sess.close()

    def add_to_cart(self, item):
        """Add selected drug to the shopping cart."""
        data = item.data(Qt.ItemDataRole.UserRole)
        # Check if already in cart
        for cart_item in self.cart:
            if cart_item['id'] == data['id']:
                cart_item['qty'] += 1
                cart_item['subtotal'] = cart_item['qty'] * cart_item['price']
                self.update_cart_table()
                return
        # New item
        data['qty'] = 1
        data['subtotal'] = data['price']
        self.cart.append(data)
        self.update_cart_table()

    def update_cart_table(self):
        """Refresh the cart table."""
        self.cart_table.setRowCount(len(self.cart))
        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(item['qty'])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"KES {item['price']:.2f}"))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"KES {item['subtotal']:.2f}"))

            # Remove button
            remove_btn = QPushButton("✕")
            remove_btn.setFixedWidth(30)
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_btn)

    def remove_from_cart(self, row):
        """Remove a row from the cart."""
        if 0 <= row < len(self.cart):
            del self.cart[row]
            self.update_cart_table()

    def clear_cart(self):
        """Empty the cart."""
        self.cart.clear()
        self.update_cart_table()

    def checkout(self):
        """Process the sale, generate receipt, and preview."""
        if not self.cart:
            QMessageBox.warning(self, "Empty Cart", "No items to checkout.")
            return

        total = sum(item['subtotal'] for item in self.cart)
        reply = QMessageBox.question(
            self,
            "Checkout",
            f"Total: KES {total:.2f}\nProceed with sale?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        sess = Session()
        try:
            # Create sale record
            sale = Sale(
                cashier_id=self.user.id,
                total_amount=total,
                sale_type='drug'
            )
            sess.add(sale)
            sess.flush()

            sale_items = []
            # Process each cart item (drugs only)
            for item in self.cart:
                drug = sess.query(Drug).get(item['id'])
                if not drug:
                    raise Exception(f"Drug with ID {item['id']} not found.")

                lots = sess.query(StockLot).filter(
                    StockLot.drug_id == drug.id,
                    StockLot.quantity > 0
                ).order_by(StockLot.expiry_date).all()

                qty_needed = item['qty']
                for lot in lots:
                    if qty_needed <= 0:
                        break
                    take = min(lot.quantity, qty_needed)
                    lot.quantity -= take
                    qty_needed -= take
                    sale_items.append({
                        'drug_id': drug.id,
                        'quantity': take,
                        'price': drug.unit_price,
                        'lot_id': lot.id
                    })
                if qty_needed > 0:
                    raise Exception(f"Insufficient stock for {drug.brand_name}")

            # Add sale items (no item_type field)
            for si in sale_items:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    drug_id=si['drug_id'],
                    quantity=si['quantity'],
                    price=si['price'],
                    lot_id=si['lot_id']
                )
                sess.add(sale_item)

            sess.commit()

            # ---- Generate receipt in temporary location ----
            temp_dir = tempfile.gettempdir()
            pdf_filename = f"receipt_{sale.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)

            # Build items list for PDF
            pdf_items = []
            for item in self.cart:
                pdf_items.append({
                    'name': item['name'],
                    'qty': item['qty'],
                    'price': item['price'],
                    'subtotal': item['subtotal']
                })

            generate_receipt(sale.id, pdf_items, total, self.user.username, pdf_path)

            # ---- Show preview dialog ----
            preview = ReceiptPreviewDialog(pdf_path, self)
            if preview.exec() == QDialog.DialogCode.Rejected:
                # User discarded – delete temp file
                try:
                    os.remove(pdf_path)
                except:
                    pass
                QMessageBox.information(self, "Cancelled", "Receipt was not saved.")
            else:
                # User saved – file is already copied by the dialog
                pass

            self.clear_cart()

        except Exception as e:
            sess.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            sess.close()