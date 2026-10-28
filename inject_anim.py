# -*- coding: utf-8 -*-
"""向 pptx 注入幻灯片切换（淡入）与元素级联入场动画（fade, withPrevious 级联）。"""
import re
import shutil
import zipfile
from lxml import etree

SRC = "塞上密卷_答辩PPT.pptx"
DST = "塞上密卷_答辩PPT_动画版.pptx"

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

FOOTER_PATTERNS = [
    re.compile(r"基于风格迁移的西夏文化衍生品开发系统 · 宁夏大学"),
    re.compile(r"^\d+ / 15$"),
]


def is_footer_text(text: str) -> bool:
    return any(p.search(text) for p in FOOTER_PATTERNS)


def collect_animatable_ids(slide_xml_bytes):
    """按文档顺序收集可动画元素 id：含文字的 sp、pic、graphicFrame；跳过页脚。"""
    root = etree.fromstring(slide_xml_bytes)
    sp_tree = root.find(".//p:cSld/p:spTree", NS)
    ids = []
    for child in sp_tree:
        tag = etree.QName(child).localname
        cnvpr = child.find(".//p:cNvPr", NS)
        if cnvpr is None:
            continue
        spid = cnvpr.get("id")
        if tag == "sp":
            texts = [t.text or "" for t in child.findall(".//a:t", NS)]
            full = "".join(texts).strip()
            if not full or is_footer_text(full):
                continue
            ids.append(spid)
        elif tag in ("pic", "graphicFrame"):
            ids.append(spid)
    return ids


def build_effect_xml(spid, tid, node_type, delay, dur):
    return (
        f'<p:par><p:cTn id="{tid}" presetID="10" presetClass="entr" presetSubtype="0" '
        f'fill="hold" grpId="0" nodeType="{node_type}">'
        f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>'
        f"<p:childTnLst>"
        f"<p:set><p:cBhvr>"
        f'<p:cTn id="{tid + 1}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
        f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
        f"<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>"
        f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
        f'<p:animEffect transition="in" filter="fade"><p:cBhvr>'
        f'<p:cTn id="{tid + 2}" dur="{dur}"/>'
        f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
        f"</p:cBhvr></p:animEffect>"
        f"</p:childTnLst></p:cTn></p:par>"
    )


def build_timing_xml(ids, base_delay=200, stagger=110, dur=400):
    effects = []
    tid = 10
    for i, spid in enumerate(ids):
        if i == 0:
            effects.append(build_effect_xml(spid, tid, "afterEffect", 0, dur))
        else:
            effects.append(build_effect_xml(spid, tid, "withEffect", i * stagger, dur))
        tid += 3
    effects_xml = "".join(effects)
    return (
        "<p:timing><p:tnLst><p:par>"
        '<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
        '<p:seq concurrent="1" nextAc="seek">'
        '<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        f'<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="{base_delay}"/></p:stCondLst>'
        f"<p:childTnLst>{effects_xml}</p:childTnLst></p:cTn></p:par>"
        "</p:childTnLst></p:cTn></p:par>"
        "</p:childTnLst></p:cTn>"
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        "</p:seq>"
        "</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>"
    )


def inject(xml_bytes):
    ids = collect_animatable_ids(xml_bytes)
    transition = '<p:transition spd="fast"><p:fade/></p:transition>'
    timing = build_timing_xml(ids) if ids else ""
    insert_xml = transition + timing
    text = xml_bytes.decode("utf-8")
    if "</p:clrMapOvr>" in text:
        text = text.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + insert_xml, 1)
    else:
        text = text.replace("</p:sld>", insert_xml + "</p:sld>", 1)
    return text.encode("utf-8"), len(ids)


zin = zipfile.ZipFile(SRC, "r")
items = zin.namelist()
with zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for name in items:
        data = zin.read(name)
        if re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
            data, n = inject(data)
            print(f"{name}: {n} animated elements")
        zout.writestr(name, data)
zin.close()
print("Saved:", DST)
