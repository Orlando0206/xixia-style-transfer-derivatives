# -*- coding: utf-8 -*-
"""文创衍生：把纹样 / 内容图合成到产品载体上（丝巾 / 明信片 / 手机壳 / 书签 / 帆布袋）。

全程离线、纯 OpenCV/NumPy。输入一张「纹样源图」（默认取自西夏风格图或风格迁移结果），
按产品形态做平铺 / 缩放裁剪，并叠加米色边框，输出可预览、可导出的产品图。
"""
import os

import cv2
import numpy as np

from . import config
from .image_io import load_image, save_image

# 产品定义：key / 名称 / 宽 / 高 / 合成方式（tile 平铺 / crop 裁剪填满）
PRODUCTS = [
    {"key": "scarf", "name": "丝巾 · 方巾", "w": 560, "h": 560, "mode": "tile"},
    {"key": "postcard", "name": "明信片", "w": 440, "h": 280, "mode": "crop"},
    {"key": "phone", "name": "手机壳", "w": 380, "h": 210, "mode": "crop"},
    {"key": "bookmark", "name": "书签", "w": 440, "h": 120, "mode": "crop"},
    {"key": "bag", "name": "帆布袋", "w": 480, "h": 440, "mode": "tile"},
]

_BORDER = (214, 202, 178)  # BGR 米色边框


def _tile(img, h, w):
    th, tw = img.shape[:2]
    if th <= 0 or tw <= 0:
        return np.zeros((h, w, 3), dtype=np.uint8)
    nrow = int(np.ceil(h / th))
    ncol = int(np.ceil(w / tw))
    tiled = np.tile(img, (nrow, ncol, 1))
    return tiled[:h, :w]


def _crop_fit(img, h, w):
    th, tw = img.shape[:2]
    if th <= 0 or tw <= 0:
        return np.zeros((h, w, 3), dtype=np.uint8)
    s = max(h / th, w / tw)
    rh, rw = int(th * s), int(tw * s)
    r = cv2.resize(img, (rw, rh), interpolation=cv2.INTER_AREA)
    y = (rh - h) // 2
    x = (rw - w) // 2
    return r[y:y + h, x:x + w]


def _add_border(img, color=_BORDER, b=10):
    return cv2.copyMakeBorder(img, b, b, b, b, cv2.BORDER_CONSTANT, value=color)


def product_def(key):
    for p in PRODUCTS:
        if p["key"] == key:
            return p
    return PRODUCTS[0]


def generate_product(source_bgr, key):
    """把 source_bgr 合成为指定产品图（BGR）。"""
    p = product_def(key)
    w, h = p["w"], p["h"]
    if p["mode"] == "tile":
        body = _tile(source_bgr, h, w)
    else:
        body = _crop_fit(source_bgr, h, w)
    return _add_border(body)


def default_motif():
    """默认纹样源：西夏风格图，缺失时程序化生成。"""
    path = os.path.join(config.ASSET_DIR, "styles", "风格图.jpg")
    img = load_image(path) if os.path.exists(path) else None
    if img is not None:
        return img
    from .style_transfer import make_xixia_style_image
    return make_xixia_style_image()


def default_portrait():
    """默认人像源：西夏女供养人像。"""
    path = os.path.join(config.ASSET_DIR, "styles", "西夏女供养人像.png")
    img = load_image(path) if os.path.exists(path) else None
    if img is not None:
        return img
    return default_motif()


def _source_for(key):
    # 手机壳 / 书签用竖版人像更有叙事感，其余用纹样平铺
    if key in ("phone",):
        return default_portrait()
    return default_motif()


def ensure_showcase_images():
    """生成 5 张默认产品展示图到 data/outputs/derivatives/，返回 {key: path}。"""
    os.makedirs(config.DERIVATIVE_DIR, exist_ok=True)
    out = {}
    for p in PRODUCTS:
        key = p["key"]
        path = os.path.join(config.DERIVATIVE_DIR, f"{key}.png")
        if not os.path.exists(path):
            img = generate_product(_source_for(key), key)
            save_image(path, img)
        out[key] = path
    return out
