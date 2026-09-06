# src/views/manage_users.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from src.database import Session
from src.models import User

class ManageUsersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_users)
        btn_layout.addWidget(self.refresh_btn)
        self.layout().addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Approved", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout().addWidget(self.table)

        self.load_users()

    def load_users(self):
        sess = Session()
        users = sess.query(User).all()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.role))
            self.table.setItem(row, 3, QTableWidgetItem("Yes" if user.is_approved else "No"))
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0,0,0,0)
            if not user.is_approved:
                approve_btn = QPushButton("Approve")
                approve_btn.clicked.connect(lambda checked, uid=user.id: self.approve_user(uid))
                actions_layout.addWidget(approve_btn)
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, uid=user.id: self.delete_user(uid))
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)
        sess.close()

    def approve_user(self, user_id):
        sess = Session()
        user = sess.query(User).get(user_id)
        if user:
            user.is_approved = True
            sess.commit()
            QMessageBox.information(self, "Approved", f"User {user.username} approved")
        sess.close()
        self.load_users()

    def delete_user(self, user_id):
        reply = QMessageBox.question(self, "Confirm", "Delete user?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            sess = Session()
            user = sess.query(User).get(user_id)
            if user:
                sess.delete(user)
                sess.commit()
                QMessageBox.information(self, "Deleted", "User deleted")
            sess.close()
            self.load_users()