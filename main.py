# main.py


import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from views.main_window import MainWindow



# def handle_exception(exc_type, exc_value, exc_traceback):
#     if issubclass(exc_type, KeyboardInterrupt):
#         sys.__excepthook__(exc_type, exc_value, exc_traceback)
#         return

#     # 印出錯誤（可選）
#     error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
#     print(error_msg)

#     # 顯示錯誤對話框
#     QMessageBox.critical(
#         None,
#         "發生錯誤",
#         f"程式發生未預期錯誤，將自動關閉：\n\n{exc_value}",
#     )

#     # 強制關閉程式
#     sys.exit(1)


def main():
    # sys.excepthook = handle_exception
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()