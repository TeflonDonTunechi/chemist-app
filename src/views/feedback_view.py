from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                             QLineEdit, QTextEdit, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt
from src.database import Session
from src.models import Feedback

class FeedbackWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        tabs = QTabWidget()
        self.layout().addWidget(tabs)

        # Submit tab
        submit_tab = QWidget()
        submit_layout = QVBoxLayout()
        submit_tab.setLayout(submit_layout)
        submit_layout.addWidget(QLabel("Submit Feedback"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Your name (optional)")
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Your email (optional)")
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Subject")
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Your message...")
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit_feedback)
        submit_layout.addWidget(self.name_edit)
        submit_layout.addWidget(self.email_edit)
        submit_layout.addWidget(self.subject_edit)
        submit_layout.addWidget(self.message_edit)
        submit_layout.addWidget(submit_btn)
        tabs.addTab(submit_tab, "Submit")

        # View tab (admin only)
        self.view_tab = QWidget()
        view_layout = QVBoxLayout()
        self.view_tab.setLayout(view_layout)
        self.feedback_table = QTableWidget()
        self.feedback_table.setColumnCount(5)
        self.feedback_table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Subject", "Message"])
        self.feedback_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        view_layout.addWidget(self.feedback_table)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_feedback)
        view_layout.addWidget(refresh_btn)
        tabs.addTab(self.view_tab, "View All")

        self.load_feedback()

    def submit_feedback(self):
        name = self.name_edit.text().strip() or "Anonymous"
        email = self.email_edit.text().strip() or "no-reply@example.com"
        subject = self.subject_edit.text().strip() or "General Feedback"
        message = self.message_edit.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Error", "Message cannot be empty.")
            return
        sess = Session()
        fb = Feedback(name=name, email=email, subject=subject, message=message)
        sess.add(fb)
        sess.commit()
        sess.close()
        QMessageBox.information(self, "Thanks", "Your feedback has been submitted.")
        self.name_edit.clear()
        self.email_edit.clear()
        self.subject_edit.clear()
        self.message_edit.clear()

    def load_feedback(self):
        sess = Session()
        feedbacks = sess.query(Feedback).order_by(Feedback.created_at.desc()).all()
        self.feedback_table.setRowCount(len(feedbacks))
        for row, fb in enumerate(feedbacks):
            self.feedback_table.setItem(row, 0, QTableWidgetItem(str(fb.id)))
            self.feedback_table.setItem(row, 1, QTableWidgetItem(fb.name or ''))
            self.feedback_table.setItem(row, 2, QTableWidgetItem(fb.email or ''))
            self.feedback_table.setItem(row, 3, QTableWidgetItem(fb.subject or ''))
            self.feedback_table.setItem(row, 4, QTableWidgetItem(fb.message or ''))
        sess.close()