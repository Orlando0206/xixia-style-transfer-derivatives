# -*- coding: utf-8 -*-
"""文化主题样式：西夏 / 丝路 / 古卷配色。"""

QSS = """
* {
    font-family: "Microsoft YaHei", "PingFang SC", "SimHei", sans-serif;
    font-size: 14px;
}

QWidget#AppRoot {
    background: #1e1913;
}

/* ---------- 通用文字 ---------- */
QLabel {
    color: #e6d9bb;
    background: transparent;
}
QLabel#TitleLabel {
    font-size: 26px;
    font-weight: bold;
    color: #e8c987;
    letter-spacing: 2px;
}
QLabel#SloganLabel {
    color: #a08a5f;
    font-size: 13px;
}
QLabel#SectionLabel {
    color: #c9a15a;
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 1px;
}
QLabel#HintLabel {
    color: #8f7c5a;
    font-size: 12px;
}
QLabel#ErrorLabel {
    color: #c96f5a;
    font-size: 12px;
}
QLabel#SuccessLabel {
    color: #8fae6a;
    font-size: 12px;
}
QLabel#PageTitle {
    color: #e8c987;
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 2px;
}

/* ---------- 输入框 ---------- */
QLineEdit {
    background: #262017;
    border: 1px solid #4a3e29;
    border-radius: 8px;
    padding: 9px 12px;
    color: #e6d9bb;
    selection-background-color: #7a5f2e;
}
QLineEdit:focus {
    border: 1px solid #c9a15a;
}

QTextEdit {
    background: #262017;
    border: 1px solid #4a3e29;
    border-radius: 8px;
    padding: 9px 12px;
    color: #e6d9bb;
    selection-background-color: #7a5f2e;
}
QTextEdit:focus {
    border: 1px solid #c9a15a;
}

/* ---------- 按钮 ---------- */
QPushButton {
    background: #332a1d;
    color: #e0cf9f;
    border: 1px solid #5a4a2d;
    border-radius: 8px;
    padding: 9px 16px;
}
QPushButton:hover {
    background: #43371f;
    border: 1px solid #c9a15a;
    color: #f2e2b0;
}
QPushButton:pressed {
    background: #57421f;
}
QPushButton:disabled {
    background: #2a2318;
    color: #6e6247;
    border: 1px solid #3a3020;
}
QPushButton#PrimaryButton {
    background: #a8792f;
    color: #20180d;
    border: 1px solid #c9a15a;
    font-weight: bold;
}
QPushButton#PrimaryButton:hover {
    background: #c9a15a;
}
QPushButton#PrimaryButton:pressed {
    background: #8f6625;
}
QPushButton#DangerButton {
    background: #4a2620;
    color: #e0b0a0;
    border: 1px solid #7a3a2e;
}
QPushButton#DangerButton:hover {
    background: #5e2f26;
    border: 1px solid #c96f5a;
}

/* ---------- 侧边栏导航 ---------- */
QFrame#Sidebar {
    background: #241d14;
    border-right: 1px solid #3a3020;
}
QPushButton#NavButton {
    background: transparent;
    color: #cdb98d;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 13px 14px;
    text-align: left;
    font-size: 15px;
}
QPushButton#NavButton:hover {
    background: #332a1d;
    color: #f2e2b0;
}
QPushButton#NavButton:checked {
    background: #3c3020;
    color: #e8c987;
    border: 1px solid #5a4a2d;
    font-weight: bold;
}

/* ---------- 列表 ---------- */
QListWidget {
    background: #241e15;
    border: 1px solid #3a3020;
    border-radius: 8px;
    color: #cdb98d;
}
QListWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #2e261a;
}
QListWidget::item:selected {
    background: #3c3020;
}
QListWidget::item:hover {
    background: #2e261a;
}

/* ---------- 滚动条 ---------- */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #4a3e29;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #6a5530;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
}
QScrollBar::handle:horizontal {
    background: #4a3e29;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* ---------- 分组框 ---------- */
QGroupBox {
    border: 1px solid #3a3020;
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 6px;
    color: #c9a15a;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}

QToolTip {
    background: #2e261a;
    color: #e6d9bb;
    border: 1px solid #5a4a2d;
}

/* ---------- 面板与卡片 ---------- */
QFrame#Panel {
    background: #241d14;
    border: 1px solid #3a3020;
    border-radius: 10px;
}
QFrame#Card {
    background: #241d14;
    border: 1px solid #3a3020;
    border-radius: 14px;
}
QFrame#PostCard {
    background: #241d14;
    border: 1px solid #3a3020;
    border-radius: 12px;
}
QFrame#Header {
    background: #241d14;
    border-bottom: 1px solid #3a3020;
}
"""
