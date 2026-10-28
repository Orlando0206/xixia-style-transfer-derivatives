# -*- coding: utf-8 -*-
"""西夏文化风格迁移（传统方法增强版）。

在 Reinhard 色彩迁移基础上，叠加风格图的高频纹理、强化斑驳质感并加入暗角，
使输出呈现西夏壁画的色调、颗粒与古旧氛围。全程离线、纯 CPU，无任何外部依赖。
"""
import cv2
import numpy as np

# 西夏壁画典型矿物颜料色（BGR 顺序，源自真实风格图的赭石/朱砂红/棕褐/米色系）
_XIXIA_PALETTE = [
    (54, 77, 96),     # 深棕
    (83, 118, 157),   # 赭石
    (21, 34, 54),     # 深褐
    (41, 64, 157),    # 朱砂红
    (133, 171, 202),  # 米色
    (60, 90, 120),    # 赭红
]


def make_xixia_style_image(size=512, seed=7):
    """程序化生成一张「西夏风格基准图」，作为默认风格图与色彩迁移统计源。"""
    h = w = size
    img = np.zeros((h, w, 3), dtype=np.float32)
    top = np.array([133, 171, 202], dtype=np.float32)    # 顶部米色
    bottom = np.array([21, 34, 54], dtype=np.float32)    # 底部深褐
    for y in range(h):
        t = y / max(h - 1, 1)
        img[y, :, :] = top * (1 - t) + bottom * t

    rng = np.random.default_rng(seed)
    yy, xx = np.ogrid[:h, :w]
    for _ in range(48):
        cx = int(rng.integers(0, w))
        cy = int(rng.integers(0, h))
        rad = float(rng.integers(30, 130))
        color = np.array(_XIXIA_PALETTE[int(rng.integers(0, len(_XIXIA_PALETTE)))],
                         dtype=np.float32)
        alpha = float(rng.uniform(0.18, 0.5))
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        mask = np.clip(1 - dist / rad, 0, 1)
        for c in range(3):
            img[:, :, c] = img[:, :, c] * (1 - alpha * mask) + color[c] * (alpha * mask)

    noise = rng.normal(0, 7, (h, w, 3))
    return np.clip(img + noise, 0, 255).astype(np.uint8)


def _reinhard_transfer(content_bgr, style_bgr):
    """Reinhard 色彩迁移：逐通道匹配均值与标准差。"""
    content = cv2.cvtColor(content_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    style = cv2.cvtColor(style_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    out = np.zeros_like(content)
    for c in range(3):
        cs = content[:, :, c]
        ss = style[:, :, c]
        mc, sc = cs.mean(), cs.std() + 1e-6
        ms, sds = ss.mean(), ss.std() + 1e-6
        out[:, :, c] = (cs - mc) * (sds / sc) + ms
    out = np.clip(out, 0, 255).astype(np.uint8)
    return cv2.cvtColor(out, cv2.COLOR_LAB2BGR)


def _extract_texture(bgr, sigma=2.5):
    """提取图像高频纹理分量（笔触/颗粒）。"""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    blur = cv2.GaussianBlur(gray, (0, 0), sigmaX=sigma)
    return gray - blur


def _overlay_texture(img_bgr, texture, strength):
    """把纹理叠加到亮度通道，产生笔触/颗粒感。"""
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    if texture.shape != lab[:, :, 0].shape:
        texture = cv2.resize(texture, (lab.shape[1], lab.shape[0]),
                             interpolation=cv2.INTER_LINEAR)
    lab[:, :, 0] += texture * strength
    lab = np.clip(lab, 0, 255).astype(np.uint8)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def apply_aged_texture(bgr, alpha=0.9, beta=5, seed=1):
    """古旧质感：轻微降对比、提亮度、叠加细腻噪点，模拟壁画斑驳。"""
    bgr = cv2.convertScaleAbs(bgr, alpha=alpha, beta=beta)
    noise = np.random.default_rng(seed).normal(0, 3, bgr.shape)
    return np.clip(bgr.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def _add_vignette(bgr, strength=0.3):
    """暗角，营造古旧氛围。"""
    h, w = bgr.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    max_d = np.sqrt(cx ** 2 + cy ** 2)
    vignette = 1 - strength * np.clip(dist / max_d, 0, 1) ** 2
    out = bgr.astype(np.float32) * vignette[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


def transfer_xixia(content_bgr, style_bgr=None, texture_strength=0.7):
    """对内容图执行西夏风格迁移，返回 (结果图, 实际使用的风格图)。"""
    if style_bgr is None:
        style_bgr = make_xixia_style_image()

    # 1. 颜色迁移
    result = _reinhard_transfer(content_bgr, style_bgr)

    # 2. 纹理注入：保留内容图自身纹理，并叠加风格图纹理
    content_tex = _extract_texture(content_bgr, sigma=3.0)
    style_tex = _extract_texture(style_bgr, sigma=3.0)
    if style_tex.shape != content_tex.shape:
        style_tex = cv2.resize(style_tex, (content_tex.shape[1],
                                           content_tex.shape[0]),
                               interpolation=cv2.INTER_LINEAR)
    mixed_tex = content_tex * 0.5 + style_tex * texture_strength
    result = _overlay_texture(result, mixed_tex, 1.0)

    # 3. 对比度恢复，避免迁移后偏灰
    lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # 4. 古旧质感 + 暗角
    result = apply_aged_texture(result, alpha=0.92, beta=4, seed=1)
    result = _add_vignette(result, strength=0.28)
    return result, style_bgr
