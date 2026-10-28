# -*- coding: utf-8 -*-
"""文创工坊：西夏纹样衍生品的展示与生成。"""
import os
from datetime import datetime

import cv2
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QFileDialog, QButtonGroup,
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt

from .. import config
from ..derivatives import (
    PRODUCTS, generate_product, default_motif, ensure_showcase_images,
)
from ..style_transfer import transfer_xixia
from ..image_io import load_image, save_image
from ..paint_label import bgr_to_qimage


class DerivativesPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._source_bgr = None
        self._preview_bgr = None
        self._selected_key = PRODUCTS[0]["key"]
        self._product_btns = {}
        self._build()
        self._use_default_motif()

    # ---------- 界面 ----------
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        head = QHBoxLayout()
        title = QLabel("文创工坊")
        title.setObjectName("PageTitle")
        head.addWidget(title)
        head.addStretch(1)
        hint = QLabel("风格迁移 → 纹样提取 → 文创衍生应用")
        hint.setObjectName("HintLabel")
        head.addWidget(hint)
        root.addLayout(head)

        body = QHBoxLayout()
        body.setSpacing(16)
        body.addWidget(self._build_source_panel())
        body.addWidget(self._build_workspace(), 1)
        root.addLayout(body, 1)

    def _build_source_panel(self):
        panel = QFrame()
        panel.setObjectName("Panel")
        panel.setFixedWidth(300)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        lab = QLabel("纹样源")
        lab.setObjectName("SectionLabel")
        lay.addWidget(lab)

        self.source_lab = QLabel()
        self.source_lab.setObjectName("Panel")
        self.source_lab.setFixedHeight(230)
        self.source_lab.setAlignment(Qt.AlignCenter)
        self.source_lab.setScaledContents(False)
        lay.addWidget(self.source_lab)

        self.upload_btn = QPushButton("上传纹样图")
        self.upload_btn.setObjectName("PrimaryButton")
        self.upload_btn.clicked.connect(self._on_upload)
        lay.addWidget(self.upload_btn)

        self.style_btn = QPushButton("应用西夏风格")
        self.style_btn.clicked.connect(self._on_apply_style)
        lay.addWidget(self.style_btn)

        self.default_btn = QPushButton("使用默认纹样")
        self.default_btn.clicked.connect(self._use_default_motif)
        lay.addWidget(self.default_btn)

        self.status_lab = QLabel("就绪")
        self.status_lab.setObjectName("HintLabel")
        self.status_lab.setWordWrap(True)
        lay.addWidget(self.status_lab)

        lay.addStretch(1)
        return panel

    def _build_workspace(self):
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        prod_lab = QLabel("选择产品载体")
        prod_lab.setObjectName("SectionLabel")
        lay.addWidget(prod_lab)

        cards = QHBoxLayout()
        cards.setSpacing(10)
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        for p in PRODUCTS:
            btn = QPushButton(p["name"])
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setFixedSize(118, 128)
            btn.clicked.connect(lambda _=False, k=p["key"]: self._select(k))
            self._btn_group.addButton(btn)
            self._product_btns[p["key"]] = btn
            cards.addWidget(btn)
        cards.addStretch(1)
        lay.addLayout(cards)

        self.preview_lab = QLabel()
        self.preview_lab.setObjectName("Panel")
        self.preview_lab.setAlignment(Qt.AlignCenter)
        self.preview_lab.setMinimumHeight(300)
        lay.addWidget(self.preview_lab, 1)

        btns = QHBoxLayout()
        self.gen_btn = QPushButton("生成预览")
        self.gen_btn.setObjectName("PrimaryButton")
        self.gen_btn.clicked.connect(self._on_generate)
        btns.addWidget(self.gen_btn)

        self.save_btn = QPushButton("保存图片")
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setEnabled(False)
        btns.addWidget(self.save_btn)
        btns.addStretch(1)
        lay.addLayout(btns)

        return box

    # ---------- 缩略图 ----------
    def _set_label_pixmap(self, label, bgr, max_side=None):
        if bgr is None:
            label.clear()
            return
        qimg = bgr_to_qimage(bgr)
        pm = QPixmap.fromImage(qimg)
        if label.height() > 0:
            pm = pm.scaled(label.width(), label.height(),
                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pm)

    def _refresh_thumbnails(self):
        showcase = ensure_showcase_images()
        for p in PRODUCTS:
            btn = self._product_btns[p["key"]]
            path = showcase.get(p["key"])
            if path and os.path.exists(path):
                img = load_image(path)
                if img is not None:
                    qimg = bgr_to_qimage(img)
                    pm = QPixmap.fromImage(qimg).scaled(
                        100, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    btn.setIcon(QIcon(pm))
                    btn.setIconSize(pm.size())

    # ---------- 逻辑 ----------
    def _select(self, key):
        self._selected_key = key
        self._preview_bgr = None
        self.preview_lab.clear()
        self.save_btn.setEnabled(False)

    def _use_default_motif(self):
        self._source_bgr = default_motif()
        self._set_label_pixmap(self.source_lab, self._source_bgr)
        self._refresh_thumbnails()
        self._preview_bgr = None
        self.preview_lab.clear()
        self.save_btn.setEnabled(False)
        self._set_status("已加载默认西夏纹样")

    def _on_upload(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择纹样图", "", config.IMAGE_FILTER)
        if not path:
            return
        img = load_image(path)
        if img is None:
            self._set_status("无法读取图片", error=True)
            return
        self._source_bgr = img
        self._set_label_pixmap(self.source_lab, self._source_bgr)
        self._preview_bgr = None
        self.preview_lab.clear()
        self.save_btn.setEnabled(False)
        self._set_status(f"已上传：{os.path.basename(path)}")

    def _on_apply_style(self):
        if self._source_bgr is None:
            self._set_status("请先上传纹样图", error=True)
            return
        self._set_status("正在应用西夏风格…")
        try:
            self._source_bgr, _ = transfer_xixia(self._source_bgr)
            self._set_label_pixmap(self.source_lab, self._source_bgr)
            self._preview_bgr = None
            self.preview_lab.clear()
            self.save_btn.setEnabled(False)
            self._set_status("西夏风格已应用，可选择产品生成")
        except Exception as e:  # noqa: BLE001
            self._set_status(f"处理失败：{e}", error=True)

    def _on_generate(self):
        if self._source_bgr is None:
            self._set_status("请先上传纹样图", error=True)
            return
        try:
            self._preview_bgr = generate_product(self._source_bgr,
                                                 self._selected_key)
            self._set_label_pixmap(self.preview_lab, self._preview_bgr)
            self.save_btn.setEnabled(True)
            name = next(p["name"] for p in PRODUCTS
                        if p["key"] == self._selected_key)
            self._set_status(f"已生成「{name}」，点击保存图片导出")
        except Exception as e:  # noqa: BLE001
            self._set_status(f"生成失败：{e}", error=True)

    def _on_save(self):
        if self._preview_bgr is None:
            self._set_status("请先生成预览", error=True)
            return
        name = next(p["name"] for p in PRODUCTS
                    if p["key"] == self._selected_key)
        default = os.path.join(
            os.path.expanduser("~"), "Desktop",
            datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{name}.png")
        path, _ = QFileDialog.getSaveFileName(
            self, "保存产品图", default, "PNG 图片 (*.png);;JPEG 图片 (*.jpg)")
        if not path:
            return
        ok, path = save_image(path, self._preview_bgr)
        self._set_status(f"已保存到：{path}" if ok else "保存失败", error=not ok)

    def _set_status(self, text, error=False):
        color = "#c96f5a" if error else "#8f7c5a"
        self.status_lab.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.status_lab.setText(text)
