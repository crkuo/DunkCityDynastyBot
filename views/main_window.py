# views/main_window.py

import os
from PyQt6 import QtWidgets, uic, QtGui
from controllers.main_controller import MatchAutomationController

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # 1. 載入 UI
        ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.ui")
        uic.loadUi(ui_path, self)

        # 2. 設定視窗基本屬性
        self.setWindowTitle("自動掛機工具")
        self.setFixedSize(310, 460)
        self.setWindowIcon(QtGui.QIcon("main.ico"))

        # 4. 綁定 startButton → 執行控制器邏輯
        self.controller = MatchAutomationController(self)
        self.startButton.clicked.connect(self.handle_start_clicked)

    def handle_start_clicked(self):
        if self.controller:
            self.controller.start_or_stop()
