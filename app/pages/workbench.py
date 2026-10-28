# -*- coding: utf-8 -*-
"""创作工作台：风格迁移 + 壁画修补 + 图片画布。"""
import os
from datetime import datetime

import cv2
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QFileDialog, QSlider, QStackedWidget, QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from .. import config
from ..database import add_history
from ..style_transfer import transfer_xixia, make_xixia_style_image
from ..inpaint import build_mask_from_damage, inpaint_image
from ..paint_label import ImageCanvas
from ..image_io import load_image, save_image


class WorkbenchPage(QWidget):
    """风格迁移与壁画修补工作台。"""
    history_changed = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self._src_bgr = None
        self._result_bgr = None
        self._saved_mask = None
        self._src_path = ""
        self._style_path = ""
        self._mode = "transfer"
        self._showing_result = False

        self.canvas = ImageCanvas()
        self._build()

    # ---------- 界面搭建 ----------
    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        root.addWidget(self._build_left_panel())
        root.addWidget(self.canvas, 1)

    def _build_left_panel(self):
        panel = QFrame()
        panel.setObjectName("Panel")
        panel.setFixedWidth(262)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        title = QLabel("操作台")
        title.setObjectName("SectionLabel")
        lay.addWidget(title)

        self.upload_btn = QPushButton("上传图片")
        self.upload_btn.setObjectName("PrimaryButton")
        self.upload_btn.clicked.connect(self._on_upload)
        lay.addWidget(self.upload_btn)

        mode_box = QHBoxLayout()
        mode_box.setSpacing(8)
        self.btn_transfer = QPushButton("风格迁移")
        self.btn_transfer.setCheckable(True)
        self.btn_transfer.setChecked(True)
        self.btn_inpaint = QPushButton("壁画修补")
        self.btn_inpaint.setCheckable(True)
        self.btn_transfer.clicked.connect(lambda: self._set_mode("transfer"))
        self.btn_inpaint.clicked.connect(lambda: self._set_mode("inpaint"))
        mode_box.addWidget(self.btn_transfer)
        mode_box.addWidget(self.btn_inpaint)
        lay.addLayout(mode_box)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_transfer_page())
        self.stack.addWidget(self._build_inpaint_page())
        lay.addWidget(self.stack)

        self.view_btn = QPushButton("当前：原图")
        self.view_btn.clicked.connect(self._on_toggle_view)
        lay.addWidget(self.view_btn)

        self.download_btn = QPushButton("下载结果")
        self.download_btn.clicked.connect(self._on_download)
        self.download_btn.setEnabled(False)
        lay.addWidget(self.download_btn)

        self.status_lab = QLabel("就绪")
        self.status_lab.setObjectName("HintLabel")
        self.status_lab.setWordWrap(True)
        lay.addWidget(self.status_lab)

        lay.addStretch(1)
        return panel

    def _build_transfer_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(8)

        self.transfer_btn = QPushButton("一键风格迁移")
        self.transfer_btn.setObjectName("PrimaryButton")
        self.transfer_btn.clicked.connect(self._on_transfer)
        lay.addWidget(self.transfer_btn)

        self.style_btn = QPushButton("选择风格图")
        self.style_btn.clicked.connect(self._on_choose_style)
        lay.addWidget(self.style_btn)

        hint = QLabel(
            "基于 Reinhard 色彩迁移与纹理注入，秒级完成，"
            "输出西夏壁画的赭石、朱砂红、棕褐与米色质感。")
        hint.setObjectName("HintLabel")
        hint.setWordWrap(True)
        lay.addWidget(hint)
        lay.addStretch(1)
        return page

    def _build_inpaint_page(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(8)

        self.detect_btn = QPushButton("自动检测破损")
        self.detect_btn.clicked.connect(self._on_auto_detect)
        lay.addWidget(self.detect_btn)

        self.brush_btn = QPushButton("涂抹标记破损")
        self.brush_btn.setCheckable(True)
        self.brush_btn.toggled.connect(self._on_brush_toggled)
        lay.addWidget(self.brush_btn)

        self.clear_btn = QPushButton("清除标记")
        self.clear_btn.clicked.connect(self._on_clear_mask)
        lay.addWidget(self.clear_btn)

        radius_row = QHBoxLayout()
        radius_row.setSpacing(6)
        rlab = QLabel("笔刷")
        rlab.setObjectName("HintLabel")
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(5, 60)
        self.radius_slider.setValue(18)
        self.radius_slider.valueChanged.connect(self._on_radius)
        self.radius_val = QLabel("18")
        self.radius_val.setObjectName("HintLabel")
        self.radius_val.setFixedWidth(24)
        radius_row.addWidget(rlab)
        radius_row.addWidget(self.radius_slider, 1)
        radius_row.addWidget(self.radius_val)
        lay.addLayout(radius_row)

        self.inpaint_btn = QPushButton("一键修补")
        self.inpaint_btn.setObjectName("PrimaryButton")
        self.inpaint_btn.clicked.connect(self._on_inpaint)
        lay.addWidget(self.inpaint_btn)

        hint = QLabel("先标记破损区域（自动检测或鼠标涂抹），再点击一键修补。")
        hint.setObjectName("HintLabel")
        hint.setWordWrap(True)
        lay.addWidget(hint)
        lay.addStretch(1)
        return page

    # ---------- 交互逻辑 ----------
    def _set_mode(self, mode):
        self._mode = mode
        self.btn_transfer.setChecked(mode == "transfer")
        self.btn_inpaint.setChecked(mode == "inpaint")
        self.stack.setCurrentIndex(0 if mode == "transfer" else 1)
        if mode == "inpaint":
            self.brush_btn.setChecked(False)
            self.canvas.set_brush_mode(False)

    def _set_status(self, text, error=False):
        color = "#c96f5a" if error else "#8f7c5a"
        self.status_lab.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.status_lab.setText(text)

    def _busy(self, busy):
        for b in (self.upload_btn, self.transfer_btn, self.style_btn,
                  self.inpaint_btn, self.detect_btn, self.brush_btn,
                  self.clear_btn, self.download_btn, self.view_btn):
            b.setEnabled(not busy)
        if not busy:
            self.download_btn.setEnabled(self._result_bgr is not None)

    def _on_upload(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", config.IMAGE_FILTER)
        if not path:
            return
        img = load_image(path)
        if img is None:
            QMessageBox.warning(self, "提示", "无法读取该图片，请更换文件。")
            return
        h, w = img.shape[:2]
        if max(h, w) > 2000:
            scale = 2000 / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)),
                             interpolation=cv2.INTER_AREA)
        self._src_bgr = img
        self._src_path = path
        self._result_bgr = None
        self._showing_result = False
        self._saved_mask = None
        self.canvas.set_image(img)
        self.view_btn.setText("当前：原图")
        self.download_btn.setEnabled(False)
        self._set_status(f"已加载：{os.path.basename(path)}（{w}×{h}）")

    def _on_transfer(self):
        if self._src_bgr is None:
            self._set_status("请先上传图片", error=True)
            return
        self._set_status("正在迁移西夏风格，请稍候…")
        self._busy(True)
        try:
            self._saved_mask = None
            style = self._get_style_image()
            result, _ = transfer_xixia(self._src_bgr, style)
            self._finish_result(result, "风格迁移")
        except Exception as e:  # noqa: BLE001
            self._set_status(f"处理失败：{e}", error=True)
        finally:
            self._busy(False)

    def _on_choose_style(self):
        start = os.path.join(config.ASSET_DIR, "styles")
        path, _ = QFileDialog.getOpenFileName(
            self, "选择风格图", start if os.path.isdir(start) else "",
            config.IMAGE_FILTER)
        if not path:
            return
        img = load_image(path)
        if img is None:
            self._set_status("无法读取风格图", error=True)
            return
        self._style_path = path
        self._set_status(f"已选择风格图：{os.path.basename(path)}")

    def _get_style_image(self):
        if self._style_path and os.path.exists(self._style_path):
            img = load_image(self._style_path)
            if img is not None:
                return img
        default = os.path.join(config.ASSET_DIR, "styles", "风格图.jpg")
        if os.path.exists(default):
            img = load_image(default)
            if img is not None:
                return img
        return make_xixia_style_image()

    def _on_auto_detect(self):
        if self._src_bgr is None:
            self._set_status("请先上传图片", error=True)
            return
        mask = build_mask_from_damage(self._src_bgr)
        self.canvas.set_mask(mask)
        n = int((mask > 0).sum())
        if n > 0:
            self._set_status(f"检测到破损区域，共 {n} 像素，可继续涂抹补充")
        else:
            self._set_status("未检测到明显破损，可用「涂抹标记」手动圈选")

    def _on_brush_toggled(self, checked):
        self.canvas.set_brush_mode(checked)
        self.brush_btn.setText("涂抹中…（再点结束）" if checked else "涂抹标记破损")

    def _on_radius(self, v):
        self.radius_val.setText(str(v))
        self.canvas.set_brush_radius(v)

    def _on_clear_mask(self):
        if self._src_bgr is None:
            return
        self.canvas.clear_mask()
        self._set_status("已清除标记")

    def _on_inpaint(self):
        if self._src_bgr is None:
            self._set_status("请先上传图片", error=True)
            return
        mask = self.canvas.get_mask()
        if mask is None or int(mask.max()) == 0:
            self._set_status("请先标记破损区域", error=True)
            return
        self._set_status("正在修补壁画，请稍候…")
        self._busy(True)
        try:
            self._saved_mask = mask.copy()
            result, _ = inpaint_image(self._src_bgr, mask)
            self.brush_btn.setChecked(False)
            self.canvas.set_brush_mode(False)
            self._finish_result(result, "壁画修补")
        except Exception as e:  # noqa: BLE001
            self._set_status(f"处理失败：{e}", error=True)
        finally:
            self._busy(False)

    def _finish_result(self, result, task_type):
        self._result_bgr = result
        self._showing_result = True
        self.canvas.set_result(result)
        self.view_btn.setText("当前：结果（点此看原图）")
        self.download_btn.setEnabled(True)

        out_dir = os.path.join(config.DATA_DIR, "outputs")
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(out_dir, f"{ts}_{task_type}.png")
        ok, _ = save_image(out_path, result)
        add_history(self.user["id"], task_type, self._src_path,
                    out_path if ok else "")
        self.history_changed.emit()
        self._set_status(f"{task_type}完成，结果已保存")

    def _on_toggle_view(self):
        if self._result_bgr is None:
            self._set_status("请先完成一次处理", error=True)
            return
        if self._showing_result:
            self._showing_result = False
            self.canvas.set_image(self._src_bgr)
            if self._saved_mask is not None and int(self._saved_mask.max()) > 0:
                self.canvas.set_mask(self._saved_mask)
            self.view_btn.setText("当前：原图（点此看结果）")
        else:
            self._showing_result = True
            self.canvas.set_result(self._result_bgr)
            self.view_btn.setText("当前：结果（点此看原图）")

    def _on_download(self):
        if self._result_bgr is None:
            self._set_status("暂无结果可下载", error=True)
            return
        default = os.path.join(
            os.path.expanduser("~"), "Desktop",
            datetime.now().strftime("%Y%m%d_%H%M%S") + "_塞上密卷.png")
        path, _ = QFileDialog.getSaveFileName(
            self, "保存结果", default, "PNG 图片 (*.png);;JPEG 图片 (*.jpg)")
        if not path:
            return
        ok, path = save_image(path, self._result_bgr)
        if ok:
            self._set_status(f"已保存到：{path}")
        else:
            self._set_status("保存失败", error=True)
