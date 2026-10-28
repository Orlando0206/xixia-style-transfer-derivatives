# -*- coding: utf-8 -*-
"""主窗口：侧边栏导航 + 多页内容。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QStackedWidget, QButtonGroup,
)
from PySide6.QtCore import Signal

from . import config
from .pages.workbench import WorkbenchPage
from .pages.derivatives_page import DerivativesPage
from .pages.knowledge import KnowledgePage
from .pages.forum import ForumPage
from .pages.history_page import HistoryPage

_NAV = [
    ("workbench", "创作工作台"),
    ("derivatives", "文创工坊"),
    ("knowledge", "西夏知库"),
    ("forum", "交流论坛"),
    ("history", "我的记录"),
]


class MainWindow(QWidget):
    logout = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setObjectName("AppRoot")
        self.setWindowTitle(f"{config.APP_NAME} · {config.APP_VERSION}")
        self.resize(1280, 820)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_stack(), 1)
        root.addLayout(body, 1)

    def _build_header(self):
        header = QFrame()
        header.setObjectName("Header")
        lay = QHBoxLayout(header)
        lay.setContentsMargins(20, 12, 20, 12)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel(config.APP_NAME)
        title.setObjectName("TitleLabel")
        sub = QLabel(config.APP_SLOGAN + " · 文化数字化保护")
        sub.setObjectName("SloganLabel")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        lay.addLayout(title_box)

        lay.addStretch(1)

        user_lab = QLabel("当前用户：" + self.user["username"])
        user_lab.setObjectName("SectionLabel")
        lay.addWidget(user_lab)

        logout_btn = QPushButton("退出登录")
        logout_btn.setObjectName("DangerButton")
        logout_btn.clicked.connect(lambda: self.logout.emit())
        lay.addWidget(logout_btn)
        return header

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(180)
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(10, 16, 10, 16)
        lay.setSpacing(6)

        brand = QLabel("西夏 · 密卷")
        brand.setObjectName("SectionLabel")
        brand.setContentsMargins(6, 0, 0, 10)
        lay.addWidget(brand)

        self._nav_btns = {}
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        for key, label in _NAV:
            btn = QPushButton(label)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _=False, k=key: self._switch(k))
            self._nav_group.addButton(btn)
            self._nav_btns[key] = btn
            lay.addWidget(btn)
        lay.addStretch(1)

        foot = QLabel(config.APP_VERSION)
        foot.setObjectName("HintLabel")
        foot.setContentsMargins(6, 0, 0, 0)
        lay.addWidget(foot)
        return sidebar

    def _build_stack(self):
        self.stack = QStackedWidget()
        self.workbench = WorkbenchPage(self.user)
        self.derivatives = DerivativesPage(self.user)
        self.knowledge = KnowledgePage(self.user)
        self.forum = ForumPage(self.user)
        self.history = HistoryPage(self.user)

        self.stack.addWidget(self.workbench)
        self.stack.addWidget(self.derivatives)
        self.stack.addWidget(self.knowledge)
        self.stack.addWidget(self.forum)
        self.stack.addWidget(self.history)

        # 工作台产生新结果时，同步刷新「我的记录」
        self.workbench.history_changed.connect(self.history.refresh)

        self._switch("workbench")
        return self.stack

    def _switch(self, key):
        index = [k for k, _ in _NAV].index(key)
        self.stack.setCurrentIndex(index)
        self._nav_btns[key].setChecked(True)
