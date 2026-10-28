# -*- coding: utf-8 -*-
"""交流论坛：帖子发布、浏览与回复，支持附带图片。"""
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QListWidget, QListWidgetItem, QTextEdit, QDialog, QLineEdit,
    QFileDialog, QMessageBox, QScrollArea,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from .. import config
from ..database import (
    add_post, list_posts, get_post, add_reply, list_replies,
    count_posts, ensure_seed_user,
)
from ..derivatives import ensure_showcase_images
from ..image_io import load_image
from ..paint_label import bgr_to_qimage


def _seed_posts():
    """首次启动时填充示例帖子（含 AI 生成图片）。"""
    if count_posts() > 0:
        return
    uid = ensure_seed_user()
    showcase = ensure_showcase_images()
    seeds = [
        ("【新品】西夏纹样衍生文创产品上线",
         "用风格迁移提取的西夏纹样，平铺/裁剪合成到丝巾方巾、明信片、手机壳、"
         "书签与帆布袋上，形成可展示、可导出的文创产品图。欢迎在「文创工坊」里"
         "上传自己的图片试试。",
         showcase.get("scarf", "")),
        ("西夏壁画的矿物颜料色系拆解",
         "西夏壁画以赭石、朱砂红、棕褐、米色为主色，配以土黄与石绿点缀。"
         "本系统的风格迁移正是围绕这套色系做色彩匹配与纹理注入。",
         showcase.get("postcard", "")),
        ("关于壁画修补的一点心得",
         "Telea 修补适合填补块状破损，但无法恢复人物五官等语义细节。"
         "若追求更高还原度，可进一步引入图生图模型做语义补全。",
         showcase.get("phone", "")),
    ]
    ids = []
    for title, content, img in seeds:
        ids.append(add_post(uid, title, content, img))
    if ids:
        add_reply(ids[0], uid, "支持！已经在工坊里生成了自己的明信片，质感很赞。")
        add_reply(ids[1], uid, "赭石色确实最有西夏的味道，收藏了。")


class PostDialog(QDialog):
    """发布新帖对话框。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("发布新帖")
        self.setFixedSize(520, 460)
        self._image_path = ""
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(10)

        lay.addWidget(QLabel("标题"))
        self.title_edit = QLineEdit()
        lay.addWidget(self.title_edit)

        lay.addWidget(QLabel("内容"))
        self.content_edit = QTextEdit()
        lay.addWidget(self.content_edit, 1)

        img_row = QHBoxLayout()
        self.img_btn = QPushButton("附加图片（可选）")
        self.img_btn.clicked.connect(self._on_pick_image)
        img_row.addWidget(self.img_btn)
        self.img_lab = QLabel("未附加")
        self.img_lab.setObjectName("HintLabel")
        img_row.addWidget(self.img_lab)
        img_row.addStretch(1)
        lay.addLayout(img_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel = QPushButton("取消")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        ok = QPushButton("发布")
        ok.setObjectName("PrimaryButton")
        ok.clicked.connect(self._on_submit)
        btn_row.addWidget(ok)
        lay.addLayout(btn_row)

    def _on_pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", config.IMAGE_FILTER)
        if path:
            self._image_path = path
            self.img_lab.setText(os.path.basename(path))

    def _on_submit(self):
        if not self.title_edit.text().strip() or \
                not self.content_edit.toPlainText().strip():
            QMessageBox.warning(self, "提示", "标题和内容不能为空。")
            return
        self.accept()

    def values(self):
        return (self.title_edit.text().strip(),
                self.content_edit.toPlainText().strip(),
                self._image_path)


class ForumPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._posts = []
        self._current = None
        _seed_posts()
        self._build()
        self._reload_posts()

    # ---------- 界面 ----------
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        head = QHBoxLayout()
        title = QLabel("交流论坛")
        title.setObjectName("PageTitle")
        head.addWidget(title)
        head.addStretch(1)
        self.new_btn = QPushButton("发布新帖")
        self.new_btn.setObjectName("PrimaryButton")
        self.new_btn.clicked.connect(self._on_new_post)
        head.addWidget(self.new_btn)
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
        lab = QLabel("帖子列表")
        lab.setObjectName("SectionLabel")
        lay.addWidget(lab)
        self.post_list = QListWidget()
        self.post_list.itemClicked.connect(self._on_post_clicked)
        lay.addWidget(self.post_list, 1)
        return panel

    def _build_detail_panel(self):
        panel = QFrame()
        panel.setObjectName("Panel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        self.detail_title = QLabel("请选择左侧帖子查看")
        self.detail_title.setObjectName("SectionLabel")
        self.detail_title.setWordWrap(True)
        lay.addWidget(self.detail_title)

        self.detail_meta = QLabel("")
        self.detail_meta.setObjectName("HintLabel")
        lay.addWidget(self.detail_meta)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(0, 0, 0, 0)
        inner_lay.setSpacing(10)
        self.detail_img = QLabel()
        self.detail_img.setAlignment(Qt.AlignCenter)
        inner_lay.addWidget(self.detail_img)
        self.detail_content = QLabel("")
        self.detail_content.setObjectName("HintLabel")
        self.detail_content.setWordWrap(True)
        self.detail_content.setAlignment(Qt.AlignTop)
        inner_lay.addWidget(self.detail_content)
        inner_lay.addStretch(1)
        scroll.setWidget(inner)
        lay.addWidget(scroll, 1)

        rep_lab = QLabel("回复")
        rep_lab.setObjectName("SectionLabel")
        lay.addWidget(rep_lab)
        self.reply_list = QListWidget()
        self.reply_list.setFixedHeight(120)
        lay.addWidget(self.reply_list)

        reply_row = QHBoxLayout()
        self.reply_edit = QLineEdit()
        self.reply_edit.setPlaceholderText("写下你的回复…")
        self.reply_edit.returnPressed.connect(self._on_reply)
        reply_row.addWidget(self.reply_edit, 1)
        self.reply_btn = QPushButton("回复")
        self.reply_btn.setObjectName("PrimaryButton")
        self.reply_btn.clicked.connect(self._on_reply)
        reply_row.addWidget(self.reply_btn)
        lay.addLayout(reply_row)

        return panel

    # ---------- 数据 ----------
    def _reload_posts(self):
        self._posts = list_posts()
        self.post_list.clear()
        for p in self._posts:
            item = QListWidgetItem(p["title"])
            item.setData(Qt.UserRole, p["id"])
            item.setToolTip(f"{p['username']} · {p['created_at'][:16]}")
            self.post_list.addItem(item)

    def _on_post_clicked(self, item):
        pid = item.data(Qt.UserRole)
        post = get_post(pid)
        if not post:
            return
        self._current = post
        self.detail_title.setText(post["title"])
        self.detail_meta.setText(
            f"{post['username']} · {post['created_at'][:16]}")
        self.detail_content.setText(post["content"])

        img_path = post.get("image_path") or ""
        if img_path and os.path.exists(img_path):
            bgr = load_image(img_path)
            if bgr is not None:
                qimg = bgr_to_qimage(bgr)
                pm = QPixmap.fromImage(qimg)
                if pm.width() > 420:
                    pm = pm.scaledToWidth(420, Qt.SmoothTransformation)
                self.detail_img.setPixmap(pm)
                self.detail_img.setVisible(True)
            else:
                self.detail_img.setVisible(False)
        else:
            self.detail_img.setVisible(False)

        self._reload_replies(pid)

    def _reload_replies(self, pid):
        self.reply_list.clear()
        for r in list_replies(pid):
            item = QListWidgetItem(
                f"{r['username']}：{r['content']}")
            item.setToolTip(r["created_at"][:16])
            self.reply_list.addItem(item)

    # ---------- 交互 ----------
    def _on_new_post(self):
        dlg = PostDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        title, content, img = dlg.values()
        add_post(self.user["id"], title, content, img)
        self._reload_posts()
        self._set_status(f"已发布：{title}")

    def _on_reply(self):
        if self._current is None:
            self._set_status("请先选择帖子", error=True)
            return
        text = self.reply_edit.text().strip()
        if not text:
            return
        add_reply(self._current["id"], self.user["id"], text)
        self.reply_edit.clear()
        self._reload_replies(self._current["id"])

    def _set_status(self, text, error=False):
        # 论坛页没有独立状态栏，用标题下 meta 临时展示
        self.detail_meta.setText(text)
