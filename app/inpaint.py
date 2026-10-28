# -*- coding: utf-8 -*-
"""壁画修补：基于 OpenCV 图像修复算法，处理破损、缺失、噪点区域。"""
import cv2
import numpy as np


def build_mask_from_damage(bgr, dark_thresh=60, light_thresh=235):
    """自动检测明显破损（过暗缺失 / 过亮噪斑）生成待修复掩码。"""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(gray)
    mask[gray < dark_thresh] = 255
    mask[gray > light_thresh] = 255
    # 形态学去小噪点，保留成块破损
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def inpaint_image(bgr, mask, radius=4):
    """对 bgr 图像按 mask 进行修复。mask 中 255 表示待修复区域。"""
    if mask is None or int(mask.max()) == 0:
        return bgr.copy(), False
    mask_u8 = mask.astype(np.uint8)
    result = cv2.inpaint(bgr, mask_u8, radius, cv2.INPAINT_TELEA)
    return result, True
