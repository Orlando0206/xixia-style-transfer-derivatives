# -*- coding: utf-8 -*-
"""全局配置：路径与常量。"""
import os
import sys

# 是否处于 PyInstaller 打包后的运行环境
_IS_FROZEN = getattr(sys, "frozen", False)

if _IS_FROZEN:
    # 资源目录（assets）打包在临时解压目录，只读
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    # 数据目录（数据库、输出）放在 exe 所在目录，可写
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), "data")
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")

ASSET_DIR = os.path.join(BASE_DIR, "assets")
DB_PATH = os.path.join(DATA_DIR, "saishang.db")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")
DERIVATIVE_DIR = os.path.join(OUTPUT_DIR, "derivatives")

APP_NAME = "塞上密卷"
APP_VERSION = "v2.0.0"
APP_SLOGAN = "一眼千年 · 西夏遗韵"

# 支持预览/处理的图片格式
IMAGE_FILTER = "图片文件 (*.png *.jpg *.jpeg *.bmp *.webp)"

# 扣子（Coze）智能体发布链接。留空则使用「在浏览器打开」按钮，
# 用户可到 coze.cn 创建并喂入西夏文化知识库后发布，把链接填到这里。
# 运行时可通过「西夏知库」页的「设置智能体链接」按钮修改，保存到 data/coze_url.txt。
COZE_BOT_URL = ""


def coze_url():
    """运行时读取 Coze 智能体链接：优先 data/coze_url.txt，其次配置常量。"""
    try:
        p = os.path.join(DATA_DIR, "coze_url.txt")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                v = f.read().strip()
                if v:
                    return v
    except OSError:
        pass
    return COZE_BOT_URL


def set_coze_url(url):
    """把智能体链接保存到 data/coze_url.txt。"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        p = os.path.join(DATA_DIR, "coze_url.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write((url or "").strip())
        return True
    except OSError:
        return False
