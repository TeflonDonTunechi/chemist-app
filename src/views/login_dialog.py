from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QWidget
from PyQt6.QtCore import Qt
from src.models import User
from src.database import Session
from werkzeug.security import check_password_hash

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Zeitgeist Teflon Pharma")
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        panel = QWidget()
        panel.setFixedSize(400, 300)
        panel.setStyleSheet("background-color: #2d2d2d; border-radius: 10px; padding: 20px;")
        panel_layout = QVBoxLayout()
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Zeitgeist Teflon Pharma")
        title.setObjectName("login_title")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #6c3b9e;")
        panel_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setFixedWidth(250)
        self.username.setStyleSheet("background-color: #3c3c3c; color: white; border: 1px solid #6c3b9e;")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedWidth(250)
        self.password.setStyleSheet("background-color: #3c3c3c; color: white; border: 1px solid #6c3b9e;")
        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedWidth(250)
        self.login_btn.clicked.connect(self.attempt_login)

        panel_layout.addWidget(self.username, alignment=Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(self.password, alignment=Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        panel.setLayout(panel_layout)
        main_layout.addWidget(panel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)
        self.user = None

    def attempt_login(self):
        sess = Session()
        user = sess.query(User).filter_by(username=self.username.text()).first()
        if user and check_password_hash(user.password_hash, self.password.text()):
            if user.role == 'cashier' and not user.is_approved:
                QMessageBox.warning(self, "Pending", "Account not approved by admin")
                sess.close()
                return
            self.user = user
            sess.close()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Invalid credentials")
            sess.close()