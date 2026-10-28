# -*- coding: utf-8 -*-
"""我的记录：历史处理结果归档与回看。"""
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QListWidget, QListWidgetItem, QFileDialog,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from .. import config
from ..database import list_history
from ..image_io import load_image, save_image
from ..paint_label import bgr_to_qimage


class HistoryPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._current = None
        self._build()
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        head = QHBoxLayout()
        title = QLabel("我的记录")
        title.setObjectName("PageTitle")
        head.addWidget(title)
        head.addStretch(1)
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh)
        head.addWidget(self.refresh_btn)
        root.addLayout(head)

        body = QHBoxLayout()
        body.setSpacing(16)
        body.addWidget(self._build_list_panel())
        body.addWidget(self._build_detail_panel(), 1)
        root.addLayout(body, 1)

    def _build_list_panel(self):
        panel = QFrame()
        panel.setObjectName("Panel")
        panel.setFixedWidth(300)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)
        lab = QLabel("处理历史")
        lab.setObjectName("SectionLabel")
        lay.addWidget(lab)
        hint = QLabel("处理结果自动归档，点击可回看")
        hint.setObjectName("HintLabel")
        hint.setWordWrap(True)
        lay.addWidget(hint)
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self._on_clicked)
        lay.addWidget(self.history_list, 1)
        return panel

    def _build_detail_panel(self):
        panel = QFrame()
        panel.setObjectName("Panel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        self.meta_lab = QLabel("选择左侧记录查看详情")
        self.meta_lab.setObjectName("SectionLabel")
        self.meta_lab.setWordWrap(True)
        lay.addWidget(self.meta_lab)

        self.preview_lab = QLabel()
        self.preview_lab.setObjectName("Panel")
        self.preview_lab.setAlignment(Qt.AlignCenter)
        self.preview_lab.setMinimumHeight(280)
        lay.addWidget(self.preview_lab, 1)

        row = QHBoxLayout()
        self.open_btn = QPushButton("另存为…")
        self.open_btn.setObjectName("PrimaryButton")
        self.open_btn.clicked.connect(self._on_save_as)
        self.open_btn.setEnabled(False)
        row.addWidget(self.open_btn)
        row.addStretch(1)
        lay.addLayout(row)

        return panel

    def refresh(self):
        self.history_list.clear()
        rows = list_history(self.user["id"])
        for r in rows:
            label = f"{r['task_type']} · {r['created_at'][5:16]}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, r)
            item.setToolTip(os.path.basename(r["out_path"])
                            if r["out_path"] else "无结果")
            self.history_list.addItem(item)

    def _on_clicked(self, item):
        r = item.data(Qt.UserRole)
        if not r:
            return
        self._current = r
        self.meta_lab.setText(
            f"{r['task_type']} · {r['created_at']}\n"
            f"来源：{os.path.basename(r['src_path']) if r['src_path'] else '—'}")
        out = r.get("out_path")
        if out and os.path.exists(out):
            bgr = load_image(out)
            if bgr is not None:
                qimg = bgr_to_qimage(bgr)
                pm = QPixmap.fromImage(qimg).scaled(
                    self.preview_lab.width(), self.preview_lab.height(),
                    Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_lab.setPixmap(pm)
                self.open_btn.setEnabled(True)
                return
        self.preview_lab.clear()
        self.open_btn.setEnabled(False)

    def _on_save_as(self):
        if self._current is None:
            return
        out = self._current.get("out_path")
        if not out or not os.path.exists(out):
            return
        bgr = load_image(out)
        if bgr is None:
            return
        default = os.path.join(os.path.expanduser("~"), "Desktop",
                               os.path.basename(out))
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", default, "PNG 图片 (*.png);;JPEG 图片 (*.jpg)")
        if not path:
            return
        ok, path = save_image(path, bgr)
        if ok:
            self.meta_lab.setText(f"已保存到：{path}")
