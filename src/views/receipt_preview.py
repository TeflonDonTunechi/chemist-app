from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
import os
import subprocess
import shutil

class ReceiptPreviewDialog(QDialog):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.setWindowTitle("Receipt Generated")
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Message
        msg = QLabel("Receipt generated successfully.\nWhat would you like to do with it?")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)

        # Buttons
        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open & Preview")
        open_btn.clicked.connect(self.open_pdf)
        save_btn = QPushButton("&Save As...")
        save_btn.clicked.connect(self.save_receipt)
        discard_btn = QPushButton("&Discard")
        discard_btn.clicked.connect(self.reject)
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(discard_btn)
        layout.addLayout(btn_layout)

        self._saved = False

    def open_pdf(self):
        """Open the PDF in the system default viewer."""
        try:
            subprocess.Popen(['xdg-open', self.pdf_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open PDF:\n{e}")
        # Accept the dialog (we consider it handled)
        self.accept()

    def save_receipt(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Receipt",
            os.path.expanduser("~/Documents/receipts/receipt.pdf"),
            "PDF Files (*.pdf)"
        )
        if save_path:
            shutil.copy2(self.pdf_path, save_path)
            QMessageBox.information(self, "Saved", f"Receipt saved to:\n{save_path}")
            self._saved = True
            self.accept()
        # else user cancelled save – dialog stays open

    def reject(self):
        """Discard: delete the temp file and close."""
        try:
            os.remove(self.pdf_path)
        except:
            pass
        super().reject()