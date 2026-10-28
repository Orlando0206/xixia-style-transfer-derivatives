# -*- coding: utf-8 -*-
"""登录 / 注册窗口。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
)
from PySide6.QtCore import Qt, Signal

from . import auth, config


class LoginWindow(QWidget):
    login_success = Signal(dict)

    def __init__(self):
        super().__init__()
        self._register_mode = False
        self.setObjectName("AppRoot")
        self.setWindowTitle(config.APP_NAME)
        self.setFixedSize(460, 560)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("Card")
        outer.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(48, 48, 48, 40)
        lay.setSpacing(14)

        title = QLabel(config.APP_NAME)
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        slogan = QLabel(config.APP_SLOGAN)
        slogan.setObjectName("SloganLabel")
        slogan.setAlignment(Qt.AlignCenter)
        lay.addWidget(slogan)

        lay.addSpacing(20)

        self.mode_label = QLabel("登 录")
        self.mode_label.setObjectName("SectionLabel")
        self.mode_label.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.mode_label)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("用户名")
        lay.addWidget(self.user_edit)

        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.pwd_edit.setPlaceholderText("密码")
        lay.addWidget(self.pwd_edit)

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setPlaceholderText("确认密码")
        self.confirm_edit.hide()
        lay.addWidget(self.confirm_edit)

        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setMinimumHeight(18)
        lay.addWidget(self.msg_label)

        self.submit_btn = QPushButton("登 录")
        self.submit_btn.setObjectName("PrimaryButton")
        self.submit_btn.setMinimumHeight(44)
        self.submit_btn.clicked.connect(self._on_submit)
        lay.addWidget(self.submit_btn)

        self.switch_btn = QPushButton("还没有账号？去注册")
        self.switch_btn.setFlat(True)
        self.switch_btn.setCursor(Qt.PointingHandCursor)
        self.switch_btn.clicked.connect(self._toggle_mode)
        lay.addWidget(self.switch_btn)

        lay.addStretch(1)

        footer = QLabel("软件工程课程设计 · 文化数字化保护")
        footer.setObjectName("HintLabel")
        footer.setAlignment(Qt.AlignCenter)
        lay.addWidget(footer)

    def _toggle_mode(self):
        self._register_mode = not self._register_mode
        if self._register_mode:
            self.mode_label.setText("注 册")
            self.confirm_edit.show()
            self.submit_btn.setText("注 册")
            self.switch_btn.setText("已有账号？去登录")
        else:
            self.mode_label.setText("登 录")
            self.confirm_edit.hide()
            self.submit_btn.setText("登 录")
            self.switch_btn.setText("还没有账号？去注册")
        self.msg_label.setText("")

    def _show_msg(self, text, error=False):
        color = "#c96f5a" if error else "#8fae6a"
        self.msg_label.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.msg_label.setText(text)

    def _on_submit(self):
        username = self.user_edit.text().strip()
        password = self.pwd_edit.text()
        if self._register_mode:
            if password != self.confirm_edit.text():
                self._show_msg("两次输入的密码不一致", error=True)
                return
            ok, msg = auth.register(username, password)
            self._show_msg(msg, error=not ok)
            if ok:
                self._toggle_mode()
                self.user_edit.clear()
                self.pwd_edit.clear()
                self.confirm_edit.clear()
        else:
            ok, msg, user = auth.login(username, password)
            if ok:
                self.login_success.emit(user)
            else:
                self._show_msg(msg, error=True)
