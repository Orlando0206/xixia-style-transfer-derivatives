# -*- coding: utf-8 -*-
"""图片读写：使用 imdecode/imencode 兼容中文路径。"""
import os
import cv2
import numpy as np

_VALID_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".webp")


def load_image(path):
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img


def save_image(path, bgr):
    ext = os.path.splitext(path)[1].lower()
    if ext not in _VALID_EXT:
        ext = ".png"
        path = os.path.splitext(path)[0] + ext
    ok, buf = cv2.imencode(ext, bgr)
    if ok:
        buf.tofile(path)
    return ok, path
