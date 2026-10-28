# -*- coding: utf-8 -*-
"""图片画布：显示图片、叠加破损标记，支持壁画修补模式下的鼠标涂抹。"""
import cv2
import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QImage, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QRectF


def bgr_to_qimage(bgr):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    return QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()


class ImageCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._img = None          # BGR numpy 原图或结果图
        self._mask = None         # uint8 破损掩码（0/255）
        self._img_qimg = None
        self._mask_qimg = None
        self._brush = False
        self._brush_radius = 18
        self._dragging = False
        self.setMouseTracking(True)
        self.setMinimumSize(420, 340)

    # ---------- 对外接口 ----------
    def set_image(self, bgr):
        self._img = bgr
        h, w = bgr.shape[:2]
        self._mask = np.zeros((h, w), dtype=np.uint8)
        self._img_qimg = bgr_to_qimage(bgr)
        self._rebuild_mask_qimg()
        self.update()

    def set_result(self, bgr):
        """只读地展示结果图（清空涂抹标记）。"""
        self._img = bgr
        h, w = bgr.shape[:2]
        self._mask = np.zeros((h, w), dtype=np.uint8)
        self._img_qimg = bgr_to_qimage(bgr)
        self._mask_qimg = None
        self.update()

    def set_mask(self, mask):
        if self._img is None:
            return
        self._mask = mask.astype(np.uint8)
        self._rebuild_mask_qimg()
        self.update()

    def get_mask(self):
        return self._mask

    def has_image(self):
        return self._img is not None

    def set_brush_mode(self, enabled):
        self._brush = enabled
        self.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)

    def set_brush_radius(self, r):
        self._brush_radius = int(r)

    def clear_mask(self):
        if self._img is not None:
            self._mask = np.zeros(self._img.shape[:2], dtype=np.uint8)
            self._rebuild_mask_qimg()
            self.update()

    # ---------- 内部绘制 ----------
    def _rebuild_mask_qimg(self):
        if self._mask is None:
            self._mask_qimg = None
            return
        h, w = self._mask.shape
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        active = self._mask > 0
        rgba[active, 0] = 255
        rgba[active, 1] = 70
        rgba[active, 2] = 40
        rgba[active, 3] = 150
        self._mask_qimg = QImage(rgba.data, w, h, w * 4, QImage.Format_RGBA8888).copy()

    def _display_rect(self):
        if self._img is None:
            return None, None
        ih, iw = self._img.shape[:2]
        w, h = self.width(), self.height()
        scale = min(w / iw, h / ih)
        dw, dh = iw * scale, ih * scale
        ox, oy = (w - dw) / 2, (h - dh) / 2
        return QRectF(ox, oy, dw, dh), scale

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(26, 21, 16))
        if self._img is None:
            painter.setPen(QColor(150, 130, 95))
            f = QFont("Microsoft YaHei")
            f.setPointSize(13)
            painter.setFont(f)
            painter.drawText(self.rect(), Qt.AlignCenter,
                             "点击「上传图片」导入一张照片，开始你的西夏之旅")
            return
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        rect, _scale = self._display_rect()
        painter.drawImage(rect, self._img_qimg)
        if self._mask_qimg is not None:
            painter.drawImage(rect, self._mask_qimg)

    def _to_img_pos(self, pos):
        rect, scale = self._display_rect()
        if rect is None or scale is None:
            return None
        ix = (pos.x() - rect.x()) / scale
        iy = (pos.y() - rect.y()) / scale
        return int(ix), int(iy)

    # ---------- 鼠标涂抹 ----------
    def mousePressEvent(self, e):
        if self._brush and e.button() == Qt.LeftButton and self._img is not None:
            self._dragging = True
            self._paint_at(e.pos())

    def mouseMoveEvent(self, e):
        if self._dragging:
            self._paint_at(e.pos())

    def mouseReleaseEvent(self, e):
        self._dragging = False

    def _paint_at(self, pos):
        p = self._to_img_pos(pos)
        if p is None or self._mask is None:
            return
        x, y = p
        h, w = self._mask.shape
        if 0 <= x < w and 0 <= y < h:
            cv2.circle(self._mask, (x, y), self._brush_radius, 255, -1)
            self._rebuild_mask_qimg()
            self.update()
