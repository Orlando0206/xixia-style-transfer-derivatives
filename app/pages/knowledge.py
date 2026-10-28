# -*- coding: utf-8 -*-
"""西夏知库：本地西夏文化知识问答 + Coze 智能体嵌入。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QListWidget, QListWidgetItem, QLineEdit, QInputDialog, QMessageBox,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from .. import config

# 本地西夏文化知识库：键为问句，值为回答
FAQ = [
    ("西夏是什么？", "西夏（1038—1227）是党项族首领李元昊建立于中国西北的政权，"
     "定都兴庆府（今宁夏银川），与宋、辽、金并立，创造了独特的文字、法律与艺术。"),
    ("西夏文字有什么特点？", "西夏文是西夏仿照汉字创制的方块文字，笔画繁复、"
     "结构方正，共约六千余字，被后世称为「天书」。1909 年黑水城文献出土后逐步被破译。"),
    ("西夏壁画的色彩来源是什么？", "西夏壁画多用矿物颜料，典型色系为赭石、朱砂红、"
     "棕褐与米色，配合土黄、石绿点缀，历经千年仍保留沉稳厚重的质感。"),
    ("黑水城遗址是什么？", "黑水城（今内蒙古额济纳旗）是西夏黑水镇燕军司驻地，"
     "20 世纪初出土大量西夏文、汉文文献与绘画，是研究西夏文明的核心考古遗址。"),
    ("西夏王陵有什么特色？", "西夏王陵位于银川西郊，被称为「东方金字塔」，"
     "现存 9 座帝陵与 250 余座陪葬墓，陵台呈圆锥形，融合党项与中原葬制。"),
    ("西夏的佛教艺术如何？", "西夏崇佛，敦煌莫高窟与榆林窟保存有大量西夏时期壁画，"
     "供养人像、飞天与经变画兼具党项民族服饰与中原画风。"),
    ("西夏服饰有什么特点？", "西夏服饰保留游牧民族的窄袖袍服，配以毡冠、"
     "绣花腰带与靴子，纹样常见卷草、云纹、动物纹等，色彩以赭红、褐、青为主。"),
    ("什么是风格迁移？", "风格迁移是一种图像处理技术，把一张「风格图」的色彩与纹理"
     "迁移到「内容图」上，使输出既保留内容结构又呈现目标风格。"),
    ("本系统的风格迁移如何实现？", "本系统采用 Reinhard 色彩迁移匹配西夏壁画的"
     "色调分布，并叠加高频纹理、斑驳颗粒与暗角，模拟古壁画的矿物颜料质感，纯离线秒级完成。"),
    ("文创衍生包含哪些产品？", "系统可将纹样合成到丝巾方巾、明信片、手机壳、"
     "书签与帆布袋等载体上，用于西夏文化的文创产品开发与展示。"),
    ("西夏文化为何值得数字化？", "西夏文献与壁画具有极高的艺术与历史价值，"
     "但传播形式较静态。通过风格迁移与文创生成，可降低大众参与门槛，推动非遗活化传播。"),
    ("智能问答助手是什么？", "智能问答助手接入扣子（Coze）平台，可喂入西夏文化知识库，"
     "以对话方式解答用户关于西夏历史、文字、艺术等的问题。"),
]


class KnowledgePage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._web = None
        self._build()

    # ---------- 界面 ----------
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        head = QHBoxLayout()
        title = QLabel("西夏知库")
        title.setObjectName("PageTitle")
        head.addWidget(title)
        head.addStretch(1)
        hint = QLabel("本地文化知识 + 智能问答助手")
        hint.setObjectName("HintLabel")
        head.addWidget(hint)
        root.addLayout(head)

        body = QHBoxLayout()
        body.setSpacing(16)
        body.addWidget(self._build_faq_panel())
        body.addWidget(self._build_agent_panel(), 1)
        root.addLayout(body, 1)

    def _build_faq_panel(self):
        panel = QFrame()
        panel.setObjectName("Panel")
        panel.setFixedWidth(340)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        lab = QLabel("文化知识库")
        lab.setObjectName("SectionLabel")
        lay.addWidget(lab)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索：如「西夏文字」")
        self.search_edit.textChanged.connect(self._on_search)
        lay.addWidget(self.search_edit)

        self.faq_list = QListWidget()
        self.faq_list.itemClicked.connect(self._on_faq_clicked)
        lay.addWidget(self.faq_list, 1)

        self.answer_lab = QLabel("点击左侧问题查看答案。")
        self.answer_lab.setObjectName("HintLabel")
        self.answer_lab.setWordWrap(True)
        self.answer_lab.setAlignment(Qt.AlignTop)
        lay.addWidget(self.answer_lab, 1)

        self._reload_faq()
        return panel

    def _build_agent_panel(self):
        panel = QFrame()
        panel.setObjectName("Panel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        lab = QLabel("智能问答助手（Coze）")
        lab.setObjectName("SectionLabel")
        lay.addWidget(lab)

        self.agent_area = QWidget()
        agent_lay = QVBoxLayout(self.agent_area)
        agent_lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.agent_area, 1)

        self._build_agent_content()

        row = QHBoxLayout()
        self.open_btn = QPushButton("在浏览器打开")
        self.open_btn.clicked.connect(self._open_in_browser)
        row.addWidget(self.open_btn)

        self.set_btn = QPushButton("设置智能体链接")
        self.set_btn.clicked.connect(self._on_set_url)
        row.addWidget(self.set_btn)
        row.addStretch(1)
        lay.addLayout(row)

        self.url_hint = QLabel("")
        self.url_hint.setObjectName("HintLabel")
        self.url_hint.setWordWrap(True)
        lay.addWidget(self.url_hint)

        return panel

    def _build_agent_content(self):
        # 清空旧内容
        while self.agent_area.layout().count():
            item = self.agent_area.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        url = config.coze_url()
        if url:
            self._try_embed_web(url)
        else:
            self._show_placeholder("尚未配置 Coze 智能体链接。\n\n"
                                   "到 coze.cn 创建智能体、喂入西夏文化知识库并发布，"
                                   "然后点击下方「设置智能体链接」填入发布链接。")

    def _try_embed_web(self, url):
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
        except Exception:  # noqa: BLE001
            self._show_placeholder("当前环境未安装 WebEngine 组件，"
                                   "请点击下方「在浏览器打开」使用智能体。")
            return
        from PySide6.QtWebEngineWidgets import QWebEngineView
        self._web = QWebEngineView()
        self._web.setUrl(QUrl(url))
        self.agent_area.layout().addWidget(self._web)

    def _show_placeholder(self, text):
        lab = QLabel(text)
        lab.setObjectName("HintLabel")
        lab.setWordWrap(True)
        lab.setAlignment(Qt.AlignCenter)
        self.agent_area.layout().addWidget(lab)

    # ---------- FAQ 逻辑 ----------
    def _reload_faq(self, keyword=""):
        self.faq_list.clear()
        kw = (keyword or "").strip()
        for q, a in FAQ:
            if kw and kw not in q and kw not in a:
                continue
            item = QListWidgetItem(q)
            item.setData(Qt.UserRole, a)
            self.faq_list.addItem(item)

    def _on_search(self, text):
        self._reload_faq(text)

    def _on_faq_clicked(self, item):
        self.answer_lab.setText(item.data(Qt.UserRole))

    # ---------- Coze 逻辑 ----------
    def _open_in_browser(self):
        url = config.coze_url()
        if not url:
            QMessageBox.information(
                self, "提示", "尚未配置智能体链接，请先「设置智能体链接」。")
            return
        QDesktopServices.openUrl(QUrl(url))

    def _on_set_url(self):
        cur = config.coze_url()
        url, ok = QInputDialog.getText(
            self, "设置智能体链接", "粘贴扣子（Coze）智能体发布链接：",
            text=cur)
        if not ok:
            return
        config.set_coze_url(url.strip())
        self.url_hint.setText(
            "链接已保存" if url.strip() else "已清空链接")
        self._build_agent_content()
        self.open_btn.setEnabled(bool(url.strip()))
