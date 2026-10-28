# -*- coding: utf-8 -*-
"""程序入口。"""
import sys

from PySide6.QtWidgets import QApplication

from app import config
from app.database import init_db
from app.login_window import LoginWindow
from app.main_window import MainWindow
from app.theme import QSS


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setApplicationName(config.APP_NAME)

    login = LoginWindow()
    state = {"main": None}

    def show_login():
        if state["main"] is not None:
            state["main"].close()
            state["main"] = None
        login.show()

    def on_login(user):
        state["main"] = MainWindow(user)
        state["main"].logout.connect(show_login)
        login.hide()
        state["main"].show()

    login.login_success.connect(on_login)
    login.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
