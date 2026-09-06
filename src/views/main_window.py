import sys
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QToolBar, QStatusBar, QLabel
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from src.views.login_dialog import LoginDialog
from src.views.dashboard import DashboardWidget
from src.views.inventory_view import InventoryWidget
from src.views.pos_view import POSWidget
from src.views.reports_view import ReportsWidget
from src.views.manage_users import ManageUsersWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user = None
        self.show_login()
        if not self.user:
            sys.exit()

        self.setWindowTitle("Zeitgeist Teflon Pharma")
        self.setGeometry(100, 100, 1400, 800)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # All users see these
        self.dashboard = DashboardWidget()
        self.pos = POSWidget(self.user)
        self.reports = ReportsWidget()

        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.pos, "POS")
        self.tabs.addTab(self.reports, "Reports")

        # Admin‑only tabs
        if self.user.role == 'admin':
            self.inventory = InventoryWidget(self.user)
            self.users = ManageUsersWidget()
            self.tabs.addTab(self.inventory, "Inventory")
            self.tabs.addTab(self.users, "Manage Users")

        self.create_toolbar()
        self.create_status_bar()

    def create_toolbar(self):
        toolbar = self.addToolBar("Main")
        logout_act = QAction("Logout", self)
        logout_act.triggered.connect(self.logout)
        toolbar.addAction(logout_act)

    def create_status_bar(self):
        status_bar = QStatusBar()
        # Center the footer message
        footer_label = QLabel("Zeitgeist Teflon Pharma v1.0 | © 2026 jardani | All rights reserved.")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_bar.addWidget(footer_label, 1)  # stretch factor 1 centers it
        self.setStatusBar(status_bar)

    def show_login(self):
        login = LoginDialog()
        if login.exec():
            self.user = login.user
        else:
            sys.exit()

    def logout(self):
        self.user = None
        self.close()
        self.show_login()
        if self.user:
            self.show()
        else:
            sys.exit()