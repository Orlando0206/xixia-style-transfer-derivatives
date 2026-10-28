const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.author = "林奕淞";
pres.title = "基于风格迁移的西夏文化衍生品开发系统 · 答辩";

// ============================================================
// SLIDE DIMENSIONS
// ============================================================
pres.layout = "LAYOUT_16x9";
const SLIDE_W = 10;
const SLIDE_H = 5.625;
const MARGIN = 0.45;
const CONTENT_X = MARGIN;
const CONTENT_Y = MARGIN;
const CONTENT_W = SLIDE_W - 2 * MARGIN; // 9.1
const CONTENT_H = SLIDE_H - 2 * MARGIN; // 4.725

// ============================================================
// PALETTE — 西夏壁画矿物色系
// ============================================================
const INK = "2E2118";       // 深褐墨（深色页底/正文标题）
const PAPER = "F5EDDD";     // 宣纸米色（内容页底）
const CARD = "FBF6EA";      // 卡片浅米
const CARD2 = "F0E6CE";     // 卡片暖金
const BORDER = "DCCBA8";    // 赭石浅边框
const CINNABAR = "A63A2A";  // 朱砂红（主强调）
const CINNABAR_D = "8C2F22";// 深朱砂
const OCHRE = "B8862F";     // 赭石金（次强调）
const GOLD = "C9A05C";      // 浅金
const BROWN = "7A5C3E";     // 棕褐（辅助文）
const GREEN = "4F6B5C";     // 石绿（点缀）
const MUTED = "8C7A63";     // 灰褐（脚注）
const CREAM = "F2E8D5";     // 深色底上的米色文字

const SERIF = "SimSun";
const SANS = "Microsoft YaHei";

// ============================================================
// CONTAINER SYSTEM
// ============================================================
function parseImageDimensions(path) {
  const match = path.match(/_(\d+)x(\d+)\.(png|jpg|jpeg|gif|webp)$/i);
  if (match) return { width: parseInt(match[1]), height: parseInt(match[2]) };
  return null;
}
function calculateScaledImageOpts(opts) {
  const { path, w: targetW, h: targetH, x = 0, y = 0, ...rest } = opts;
  if (!path || !targetW || !targetH) return opts;
  const dims = parseImageDimensions(path);
  if (!dims) return opts;
  const imgAspect = dims.width / dims.height;
  const targetAspect = targetW / targetH;
  let scaledW, scaledH, offsetX = 0, offsetY = 0;
  if (imgAspect > targetAspect) {
    scaledW = targetW; scaledH = targetW / imgAspect; offsetY = (targetH - scaledH) / 2;
  } else {
    scaledH = targetH; scaledW = targetH * imgAspect; offsetX = (targetW - scaledW) / 2;
  }
  return { path, x: x + offsetX, y: y + offsetY, w: scaledW, h: scaledH, ...rest };
}
function createVirtualNode(type, data, parentX = 0, parentY = 0) {
  const opts = data.opts || {};
  const node = { type, data, absX: parentX + (opts.x || 0), absY: parentY + (opts.y || 0), w: opts.w || 0, h: opts.h || 0, children: [] };
  node.addShape = function (shapeType, opts = {}) { const c = createVirtualNode("shape", { shapeType, opts }, node.absX, node.absY); node.children.push(c); return c; };
  node.addText = function (text, opts = {}) { const c = createVirtualNode("text", { text, opts: { fit: "shrink", ...opts } }, node.absX, node.absY); node.children.push(c); return c; };
  node.addImage = function (opts = {}) { const c = createVirtualNode("image", { opts: calculateScaledImageOpts(opts) }, node.absX, node.absY); node.children.push(c); return c; };
  node.addTable = function (tableData, opts = {}) { const c = createVirtualNode("table", { tableData, opts }, node.absX, node.absY); node.children.push(c); return c; };
  return node;
}
function flattenNode(node, realSlide, pres) {
  const absOpts = { ...node.data.opts, x: node.absX, y: node.absY };
  if (node.type === "shape") realSlide.addShape(node.data.shapeType, absOpts);
  else if (node.type === "text") realSlide.addText(node.data.text, absOpts);
  else if (node.type === "image") realSlide.addImage(absOpts);
  else if (node.type === "table") realSlide.addTable(node.data.tableData, absOpts);
  node.children.forEach((c) => flattenNode(c, realSlide, pres));
}
const originalAddSlide = pres.addSlide.bind(pres);
pres.addSlide = function (options) {
  const realSlide = originalAddSlide(options);
  const virtualSlide = {
    children: [], _realSlide: realSlide,
    set background(val) { realSlide.background = val; },
    get background() { return realSlide.background; },
    addShape: function (t, o = {}) { const n = createVirtualNode("shape", { shapeType: t, opts: o }, 0, 0); this.children.push(n); return n; },
    addText: function (t, o = {}) { const n = createVirtualNode("text", { text: t, opts: { fit: "shrink", ...o } }, 0, 0); this.children.push(n); return n; },
    addImage: function (o = {}) { const n = createVirtualNode("image", { opts: calculateScaledImageOpts(o) }, 0, 0); this.children.push(n); return n; },
    addTable: function (d, o = {}) { const n = createVirtualNode("table", { tableData: d, opts: o }, 0, 0); this.children.push(n); return n; },
    addChart: function (t, d, o = {}) { realSlide.addChart(t, d, o); },
    addNotes: function (t) { realSlide.addNotes(t); },
    render: function () { this.children.forEach((c) => flattenNode(c, realSlide, pres)); },
  };
  return virtualSlide;
};

// ============================================================
// SHARED HELPERS
// ============================================================
function addHeader(slide, tag, title) {
  slide.addShape(pres.shapes.RECTANGLE, { x: CONTENT_X, y: 0.5, w: 0.07, h: 0.52, fill: { color: CINNABAR } });
  slide.addText(tag, { x: CONTENT_X + 0.17, y: 0.42, w: 6.5, h: 0.26, fontFace: SANS, fontSize: 10.5, color: OCHRE, bold: true, charSpacing: 1, margin: 0 });
  slide.addText(title, { x: CONTENT_X + 0.17, y: 0.66, w: 8.8, h: 0.5, fontFace: SERIF, fontSize: 23, color: INK, bold: true, charSpacing: 1.5, margin: 0 });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.0, y: 0.52, w: 0.14, h: 0.14, fill: { color: CINNABAR } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.2, y: 0.52, w: 0.14, h: 0.14, fill: { color: GOLD } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 9.4, y: 0.52, w: 0.14, h: 0.14, fill: { color: GREEN } });
}
function addFooter(slide, pageNum) {
  slide.addText("基于风格迁移的西夏文化衍生品开发系统 · 宁夏大学", { x: CONTENT_X, y: 5.3, w: 5.5, h: 0.22, fontFace: SANS, fontSize: 8, color: MUTED, margin: 0 });
  slide.addText(`${pageNum} / 15`, { x: 8.6, y: 5.3, w: 0.95, h: 0.22, fontFace: SANS, fontSize: 8, color: MUTED, align: "right", margin: 0 });
}

// ============================================================
// SLIDE 1 — 封面
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0.28, y: 0.28, w: 9.44, h: 5.06, fill: { type: "none" }, line: { color: GOLD, width: 1.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.38, y: 0.38, w: 9.24, h: 4.86, fill: { type: "none" }, line: { color: BROWN, width: 0.75 } });
  s.addText("宁夏大学 · 大学生创新创业训练计划项目", { x: 1.5, y: 0.78, w: 7, h: 0.32, fontFace: SANS, fontSize: 12, color: GOLD, align: "center", charSpacing: 2 });
  s.addText([
    { text: "基于风格迁移的", options: { breakLine: true } },
    { text: "西夏文化衍生品开发系统", options: {} },
  ], { x: 0.8, y: 1.5, w: 8.4, h: 1.75, fontFace: SERIF, fontSize: 40, bold: true, color: CREAM, align: "center", valign: "middle", charSpacing: 2.5 });
  s.addText("—— 「塞上密卷」 一眼千年 · 西夏遗韵 ——", { x: 1.5, y: 3.4, w: 7, h: 0.4, fontFace: SERIF, fontSize: 16, color: GOLD, align: "center", charSpacing: 1 });
  s.addShape(pres.shapes.RECTANGLE, { x: 4.82, y: 4.02, w: 0.12, h: 0.12, fill: { color: CINNABAR }, rotate: 45 });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.06, y: 4.02, w: 0.12, h: 0.12, fill: { color: GOLD }, rotate: 45 });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.3, y: 4.02, w: 0.12, h: 0.12, fill: { color: CINNABAR }, rotate: 45 });
  s.addText("汇报人：林奕淞        指导教师：马子睿        信息工程学院", { x: 1.5, y: 4.42, w: 7, h: 0.32, fontFace: SANS, fontSize: 12.5, color: CREAM, align: "center" });
  s.addText("2026 年 10 月", { x: 1.5, y: 4.78, w: 7, h: 0.28, fontFace: SANS, fontSize: 10.5, color: GOLD, align: "center" });
  s.addNotes("各位老师好，我是林奕淞。今天汇报的项目是《基于风格迁移的西夏文化衍生品开发系统》，软件名为「塞上密卷」。下面用五分钟时间，从项目简介、社会可行性、技术可行性、经济可行性和未来计划五个方面进行汇报。");
  s.render();
}

// ============================================================
// SLIDE 2 — 目录
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 1.65, w: 0.09, h: 1.5, fill: { color: CINNABAR } });
  s.addText([
    { text: "目 录", options: { breakLine: true } },
  ], { x: 1.15, y: 1.6, w: 2.8, h: 0.95, fontFace: SERIF, fontSize: 44, bold: true, color: INK, charSpacing: 2.5, margin: 0 });
  s.addText("CONTENTS", { x: 1.17, y: 2.62, w: 2.8, h: 0.35, fontFace: SANS, fontSize: 12, color: OCHRE, charSpacing: 3, margin: 0 });
  const items = [
    ["01", "项目简介", "功能架构 · 软件展示 · 衍生品 · 创新点"],
    ["02", "社会可行性分析", "谷子经济 · 文旅数据 · 线性回归预测"],
    ["03", "技术可行性分析", "技术栈 · 分层架构 · 算法与软著基础"],
    ["04", "经济可行性分析", "经费预算 · 成本控制"],
    ["05", "未来计划", "八周甘特图 · 阶段目标"],
  ];
  items.forEach((it, i) => {
    const y = 0.82 + i * 0.88;
    s.addText([
      { text: it[0] + "   ", options: { fontFace: SERIF, fontSize: 19, bold: true, color: CINNABAR } },
      { text: it[1], options: { fontFace: SERIF, fontSize: 17, bold: true, color: INK } },
      { text: "    " + it[2], options: { fontFace: SANS, fontSize: 10, color: MUTED } },
    ], { x: 4.35, y, w: 5.1, h: 0.74, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, valign: "middle", indent: 0.18 });
  });
  s.addNotes("本次汇报分为五个部分：第一部分项目简介，介绍系统功能、软件与衍生品展示和创新点；第二部分社会可行性，基于谷子经济和宁夏近五年文旅数据建模分析；第三部分技术可行性；第四部分经济可行性；最后是未来计划。");
  s.render();
}

// ============================================================
// SLIDE 3 — 项目简介 · 背景与痛点
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "01 · 项目简介", "项目背景：当西夏文化遇见「谷子经济」");
  s.addText("数字与体验经济深度融合，传统旅游难以满足现代需求；国家文化数字化战略推动优秀传统文化创造性转化、创新性发展。", { x: CONTENT_X, y: 1.28, w: CONTENT_W, h: 0.42, fontFace: SANS, fontSize: 11.5, color: BROWN });
  // 需求端
  s.addText([
    { text: "需求端", options: { fontFace: SANS, fontSize: 11, bold: true, color: CREAM, breakLine: true } },
  ], { x: CONTENT_X, y: 1.82, w: 2.85, h: 0.34, fill: { color: CINNABAR }, align: "center", valign: "middle" });
  s.addText([
    { text: "76%", options: { fontFace: SERIF, fontSize: 40, bold: true, color: CINNABAR, breakLine: true } },
    { text: "Z世代游客渴望「文化+科技」沉浸体验", options: { fontFace: SANS, fontSize: 10.5, color: INK, breakLine: true } },
    { text: "数据来源：文旅部 2023", options: { fontFace: SANS, fontSize: 8.5, color: MUTED } },
  ], { x: CONTENT_X, y: 2.16, w: 2.85, h: 1.98, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, align: "center", valign: "middle" });
  // 供给端
  s.addText([
    { text: "供给端 · 文旅行业三大痛点", options: { fontFace: SANS, fontSize: 11, bold: true, color: CREAM } },
  ], { x: 3.5, y: 1.82, w: 6.05, h: 0.34, fill: { color: BROWN }, align: "center", valign: "middle" });
  const pains = [
    ["< 18%", "非遗商业化转化率低", "文化资源难以变现"],
    ["60%", "西北景区收入集中于 5-10 月", "收入季节性强"],
    ["< 40%", "35 岁以下游客占比不足", "年轻客群流失"],
  ];
  pains.forEach((p, i) => {
    const x = 3.5 + i * 2.08;
    s.addText([
      { text: p[0], options: { fontFace: SERIF, fontSize: 26, bold: true, color: CINNABAR_D, breakLine: true } },
      { text: p[1], options: { fontFace: SANS, fontSize: 9.5, bold: true, color: INK, breakLine: true } },
      { text: p[2], options: { fontFace: SANS, fontSize: 8.5, color: MUTED } },
    ], { x, y: 2.16, w: 1.93, h: 1.98, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, align: "center", valign: "middle" });
  });
  s.addText([
    { text: "⇒ 破局思路：", options: { fontFace: SANS, fontSize: 12, bold: true, color: CINNABAR } },
    { text: "以「生态、价值、时空」三维赋能，打造高效沉浸的西夏文化新型旅游与文创体验", options: { fontFace: SANS, fontSize: 12, color: INK } },
  ], { x: CONTENT_X, y: 4.32, w: CONTENT_W, h: 0.55, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, valign: "middle", indent: 0.2 });
  addFooter(s, 3);
  s.addNotes("先看项目背景。需求端，文旅部数据显示76%的Z世代游客渴望文化加科技的沉浸体验；而供给端存在三大痛点：非遗商业化转化率不足18%、西北景区六成收入集中在5到10月、35岁以下年轻客群不足四成。我们的思路是以生态、价值、时空三维赋能，打造新型西夏文化体验。");
  s.render();
}

// ============================================================
// SLIDE 4 — 项目简介 · 系统功能与运行流程
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "01 · 项目简介", "系统功能：一站式西夏文化创作平台");
  const mods = [
    ["创作工作台", "一键西夏风格迁移\n壁画智能修补"],
    ["文创工坊", "纹样上传与应用\n五类文创产品生成"],
    ["西夏知库", "本地文化知识库\nCoze 智能体答疑"],
    ["交流论坛", "发帖 · 浏览 · 回复\n作品展示与讨论"],
    ["我的记录", "处理结果归档\n历史随时回看"],
  ];
  mods.forEach((m, i) => {
    const x = CONTENT_X + i * 1.84;
    s.addText([
      { text: m[0], options: { fontFace: SERIF, fontSize: 13, bold: true, color: CINNABAR, breakLine: true } },
      { text: m[1], options: { fontFace: SANS, fontSize: 9, color: BROWN } },
    ], { x, y: 1.22, w: 1.74, h: 1.32, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, align: "center", valign: "middle" });
  });
  s.addText("系统运行流程：登录 → 侧边栏导航 → 各功能页 → 本地归档", { x: CONTENT_X, y: 2.66, w: CONTENT_W, h: 0.28, fontFace: SANS, fontSize: 10, bold: true, color: BROWN, margin: 0 });
  s.addImage({ path: "ppt_assets/system_flow_1979x1179.png", x: 2.62, y: 2.98, w: 4.76, h: 2.24 });
  addFooter(s, 4);
  s.addNotes("系统名为塞上密卷，采用侧边栏导航组织五大功能页：创作工作台提供一键西夏风格迁移和壁画修补；文创工坊生成五类文创产品；西夏知库结合Coze智能体答疑；交流论坛承载作品分享；我的记录负责结果归档。下方是系统的整体使用流程，从登录到本地归档形成闭环。");
  s.render();
}

// ============================================================
// SLIDE 5 — 项目简介 · 软件展示
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "01 · 项目简介", "软件展示：深色古卷风 · 塞上密卷 v2.0");
  s.addImage({ path: "ppt_assets/exe_icon_206x56.png", x: 7.72, y: 0.44, w: 1.55, h: 0.42 });
  s.addImage({ path: "ppt_assets/ui_login_926x1182.png", x: 0.6, y: 1.24, w: 2.85, h: 3.52 });
  s.addText("登录 / 注册界面 —— QSS 定制深色古卷审美", { x: 0.6, y: 4.8, w: 2.85, h: 0.26, fontFace: SANS, fontSize: 9, color: MUTED, align: "center", margin: 0 });
  s.addImage({ path: "ppt_assets/ui_main_2562x1696.png", x: 3.72, y: 1.24, w: 5.6, h: 3.52 });
  s.addText("创作工作台 —— 上传图片 · 一键迁移 · 原图/结果对比 · 下载归档", { x: 3.72, y: 4.8, w: 5.6, h: 0.26, fontFace: SANS, fontSize: 9, color: MUTED, align: "center", margin: 0 });
  addFooter(s, 5);
  s.addNotes("这是软件的真实运行界面。整体采用QSS定制的深色古卷风格，契合西夏文化审美；左侧是登录注册界面，右侧是创作工作台，上传图片后一键即可完成风格迁移，支持原图与结果一键切换对比、结果下载。软件可打包为独立exe，双击即用。");
  s.render();
}

// ============================================================
// SLIDE 6 — 项目简介 · 核心效果展示
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "01 · 项目简介", "核心效果：迁移 · 修补 · 修复");
  s.addImage({ path: "ppt_assets/style_transfer_1387x728.png", x: 1.32, y: 1.2, w: 3.4, h: 1.74 });
  s.addImage({ path: "ppt_assets/mural_inpaint_1354x715.png", x: 5.28, y: 1.2, w: 3.4, h: 1.74 });
  s.addText("风格迁移：头像 → 西夏壁画风", { x: 1.32, y: 2.98, w: 3.4, h: 0.24, fontFace: SANS, fontSize: 9, color: MUTED, align: "center", margin: 0 });
  s.addText("壁画修补：真实破损 → Telea 修复", { x: 5.28, y: 2.98, w: 3.4, h: 0.24, fontFace: SANS, fontSize: 9, color: MUTED, align: "center", margin: 0 });
  s.addImage({ path: "ppt_assets/painting_restore_1715x774.png", x: 3.05, y: 3.3, w: 3.9, h: 1.62 });
  s.addText("古画修复：破损修补 + 西夏暖色调上色", { x: 3.05, y: 4.96, w: 3.9, h: 0.24, fontFace: SANS, fontSize: 9, color: MUTED, align: "center", margin: 0 });
  addFooter(s, 6);
  s.addNotes("核心效果方面：左上是头像的西夏风格迁移对比，迁移后呈现壁画特有的赭石、朱砂红色调与斑驳质感；右上是西夏女供养人像的真实破损修补；下方是古画修复链路，先修补破损，再叠加西夏暖色调上色，让褪色古画重现温度。");
  s.render();
}

// ============================================================
// SLIDE 7 — 项目简介 · 衍生品展示
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "01 · 项目简介", "衍生品展示：西夏纹样文创矩阵");
  s.addImage({ path: "ppt_assets/costume_pattern_910x872.png", x: 0.5, y: 1.14, w: 3.7, h: 3.54 });
  s.addText("西夏服饰纹样数字化设计", { x: 0.5, y: 4.74, w: 3.7, h: 0.26, fontFace: SANS, fontSize: 9.5, bold: true, color: BROWN, align: "center", margin: 0 });
  const prods = [
    ["ppt_assets/product_bag_832x568.png", "帆布包"],
    ["ppt_assets/product_tshirt_830x474.png", "T 恤"],
    ["ppt_assets/product_pouch_832x462.png", "束口袋"],
    ["ppt_assets/product_postcard_806x522.png", "明信片"],
  ];
  prods.forEach((p, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 4.42 + col * 2.62, y = 1.14 + row * 1.86;
    s.addImage({ path: p[0], x, y, w: 2.5, h: 1.52 });
    s.addText(p[1], { x, y: y + 1.54, w: 2.5, h: 0.26, fontFace: SANS, fontSize: 9.5, bold: true, color: BROWN, align: "center", margin: 0 });
  });
  addFooter(s, 7);
  s.addNotes("在衍生品方面，系统将迁移后的纹样合成到多种载体：左侧是西夏服饰纹样的数字化设计，标注了窄袖圆领袍、皮毛边衣等典型形制；右侧是帆布包、T恤、束口袋、明信片四类文创产品设计规范，形成完整的西夏纹样文创矩阵。");
  s.render();
}

// ============================================================
// SLIDE 8 — 项目简介 · 创新点
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "01 · 项目简介", "创新点：紧扣西夏文化");
  s.addText([
    { text: "以「西夏文化」为默认风格源 —— ", options: { fontFace: SERIF, fontSize: 13, bold: true, color: INK } },
    { text: "赭石 · 朱砂红 · 棕褐 · 米色", options: { fontFace: SERIF, fontSize: 13, bold: true, color: CINNABAR } },
    { text: " 矿物颜料色调与纹理特征内建于系统", options: { fontFace: SERIF, fontSize: 13, bold: true, color: INK } },
  ], { x: CONTENT_X, y: 1.22, w: CONTENT_W, h: 0.52, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, align: "center", valign: "middle" });
  const inns = [
    ["壹", "文化专属风格", "西夏壁画矿物色调与纹理封装为内建风格，区别于通用艺术风格工具"],
    ["贰", "完整创作链路", "「风格迁移 → 纹样提取 → 文创衍生」一体化闭环，缩短再设计周期"],
    ["叁", "知识服务 + 社区", "Coze 智能体与交流论坛加持，单机工具升级为创作平台"],
    ["肆", "零门槛交互", "多页导航整合各功能，普通用户一键上手，纯 CPU 离线运行"],
  ];
  inns.forEach((n, i) => {
    const x = CONTENT_X + i * 2.3;
    s.addText(n[0], { x: x + 0.78, y: 2.02, w: 0.6, h: 0.6, shape: pres.shapes.OVAL, fill: { color: CINNABAR }, fontFace: SERIF, fontSize: 17, bold: true, color: CREAM, align: "center", valign: "middle" });
    s.addText([
      { text: n[1], options: { fontFace: SERIF, fontSize: 13.5, bold: true, color: INK, breakLine: true } },
      { text: "\n" + n[2], options: { fontFace: SANS, fontSize: 9.5, color: BROWN } },
    ], { x, y: 2.76, w: 2.16, h: 1.9, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, align: "center", valign: "top", paraSpaceAfter: 6 });
  });
  s.addText("项目特色：技术整合性 · 文化沉浸体验 · 模块化架构 · 轻量部署", { x: CONTENT_X, y: 4.82, w: CONTENT_W, h: 0.3, fontFace: SANS, fontSize: 10.5, color: OCHRE, bold: true, align: "center", margin: 0 });
  addFooter(s, 8);
  s.addNotes("项目的核心创新紧扣西夏文化：第一，以西夏壁画矿物颜料色调作为系统内建风格源，而非通用艺术风格；第二，打通风格迁移、纹样提取到文创衍生的完整创作链路；第三，融合智能体知识服务与交流社区；第四，多页导航一体化交互，零门槛上手，纯CPU离线运行。");
  s.render();
}

// ============================================================
// SLIDE 9 — 社会可行性 · 市场背景
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "02 · 社会可行性分析", "谷子经济盛行，文旅消费快速上升");
  s.addText([
    { text: "「谷子」经济正当其时", options: { fontFace: SERIF, fontSize: 13.5, bold: true, color: CINNABAR, breakLine: true } },
    { text: "\n「谷子」（Goods 音译）消费持续走热，年轻群体愿意为文化 IP 周边买单；西夏纹样衍生品天然契合谷子消费场景，受众基础坚实。", options: { fontFace: SANS, fontSize: 10, color: INK, breakLine: true } },
    { text: "\n政策加持：2022 年中办、国办印发《关于推进实施国家文化数字化战略的意见》，明确推动传统文化创造性转化。", options: { fontFace: SANS, fontSize: 10, color: BROWN } },
  ], { x: CONTENT_X, y: 1.22, w: 4.3, h: 1.98, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, valign: "top", paraSpaceAfter: 4 });
  s.addTable([
    [{ text: "年份", options: { fill: { color: CINNABAR }, color: CREAM, bold: true } },
     { text: "接待国内游客（万人次）", options: { fill: { color: CINNABAR }, color: CREAM, bold: true } },
     { text: "国内旅游收入（亿元）", options: { fill: { color: CINNABAR }, color: CREAM, bold: true } }],
    ["2020", "3429.54", "199.06"],
    ["2021", "3622.51", "286.38"],
    ["2022", "3882.48", "304.28"],
    ["2023", "7004.11", "651.45"],
    ["2024", "8124.96", "766.45"],
  ], {
    x: CONTENT_X, y: 3.36, w: 4.3, colW: [0.9, 1.8, 1.6],
    fontFace: SANS, fontSize: 9.5, color: INK, align: "center", valign: "middle",
    border: { pt: 0.75, color: BORDER }, fill: { color: CARD }, rowH: 0.28,
  });
  s.addText([
    { text: "24.06%", options: { fontFace: SERIF, fontSize: 30, bold: true, color: CINNABAR, breakLine: true } },
    { text: "国内游客量 年均复合增长率（2020–2024）", options: { fontFace: SANS, fontSize: 10, color: INK } },
  ], { x: 5.05, y: 1.22, w: 4.5, h: 1.14, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, align: "center", valign: "middle" });
  s.addText([
    { text: "40.08%", options: { fontFace: SERIF, fontSize: 30, bold: true, color: OCHRE, breakLine: true } },
    { text: "国内旅游收入 年均复合增长率（2020–2024）", options: { fontFace: SANS, fontSize: 10, color: INK } },
  ], { x: 5.05, y: 2.5, w: 4.5, h: 1.14, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, align: "center", valign: "middle" });
  s.addText([
    { text: "结论：", options: { fontFace: SANS, fontSize: 11, bold: true, color: CINNABAR } },
    { text: "文旅消费处于快速上升通道，「文化 + 科技」衍生品具备明确的社会需求与市场增量。", options: { fontFace: SANS, fontSize: 11, color: INK } },
  ], { x: 5.05, y: 3.8, w: 4.5, h: 0.9, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, valign: "middle", indent: 0.15 });
  addFooter(s, 9);
  s.addNotes("社会可行性方面：谷子经济持续盛行，年轻人愿意为文化IP买单，西夏纹样衍生品正好契合这一场景；政策上国家文化数字化战略明确支持。数据上，宁夏近五年国内游客量年均复合增长率24.06%，旅游收入增速更高达40.08%，文旅消费处于快速上升通道，社会需求明确。");
  s.render();
}

// ============================================================
// SLIDE 10 — 社会可行性 · 线性回归预测
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "02 · 社会可行性分析", "线性回归建模：预测未来三年走势");
  s.addText([
    { text: "回归模型", options: { fontFace: SANS, fontSize: 11, bold: true, color: CREAM } },
  ], { x: CONTENT_X, y: 1.24, w: 4.1, h: 0.34, fill: { color: BROWN }, align: "center", valign: "middle" });
  s.addText([
    { text: "以 t = 年份 − 2020 为自变量，游客量 y（万人次）为因变量", options: { fontFace: SANS, fontSize: 9.5, color: BROWN, breakLine: true } },
    { text: "\ny = 2658.23 + 1277.24 t", options: { fontFace: SERIF, fontSize: 19, bold: true, color: CINNABAR, breakLine: true } },
    { text: "拟合优度 R² = 0.851", options: { fontFace: SANS, fontSize: 11, bold: true, color: OCHRE, breakLine: true } },
    { text: "\n趋势外推（2025–2027）", options: { fontFace: SANS, fontSize: 10.5, bold: true, color: INK, breakLine: true } },
    { text: "游客量：9044.5 万 → 10321.7 万 → 11598.9 万人次", options: { fontFace: SANS, fontSize: 9.5, color: INK, breakLine: true } },
    { text: "旅游收入：891.5 亿 → 1041.5 亿 → 1191.4 亿元", options: { fontFace: SANS, fontSize: 9.5, color: INK, breakLine: true } },
    { text: "\n2025 收入三情景：保守 909.3 · 中性 927.2 · 乐观 945.0（亿元）", options: { fontFace: SANS, fontSize: 9.5, color: BROWN } },
  ], { x: CONTENT_X, y: 1.58, w: 4.1, h: 3.44, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, valign: "middle", indent: 0.15, paraSpaceAfter: 3 });
  s.addImage({ path: "ppt_assets/tourism_trend_1422x846.png", x: 4.85, y: 1.24, w: 4.7, h: 2.9 });
  s.addText("宁夏国内旅游人次趋势与预测（线性回归，R² = 0.851）", { x: 4.85, y: 4.18, w: 4.7, h: 0.26, fontFace: SANS, fontSize: 9, color: MUTED, align: "center", margin: 0 });
  s.addText([
    { text: "洞察：", options: { fontFace: SANS, fontSize: 10.5, bold: true, color: CINNABAR } },
    { text: "模型拟合良好，2027 年游客量有望突破 1.15 亿人次 —— 市场增量明确（预测需落地后以真实数据验证）。", options: { fontFace: SANS, fontSize: 10.5, color: INK } },
  ], { x: 4.85, y: 4.48, w: 4.7, h: 0.56, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, valign: "middle", indent: 0.12 });
  addFooter(s, 10);
  s.addNotes("进一步用数据说话：以年份为自变量、游客量为因变量建立一元线性回归，拟合方程为 y 等于 2658.23 加 1277.24t，R方达到0.851。外推预测2025到2027年游客量将从9044万人次增长到1.16亿人次，旅游收入从891亿元增长到1191亿元，并设定保守、中性、乐观三种情景。市场增量明确。");
  s.render();
}

// ============================================================
// SLIDE 11 — 技术可行性 · 技术栈与架构
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "03 · 技术可行性分析", "技术可行性：成熟技术栈 + 分层架构");
  const chips = ["Python 3.10", "PySide6 · QSS", "OpenCV", "NumPy", "SQLite", "Coze 智能体"];
  chips.forEach((c, i) => {
    s.addText(c, { x: CONTENT_X + i * 1.53, y: 1.22, w: 1.44, h: 0.44, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, fontFace: SANS, fontSize: 10.5, bold: true, color: INK, align: "center", valign: "middle" });
  });
  s.addImage({ path: "ppt_assets/system_arch_1979x1340.png", x: 0.5, y: 1.82, w: 4.85, h: 3.3 });
  const layers = [
    ["表现层", "登录 / 五大功能页 · 侧边栏导航"],
    ["业务逻辑层", "迁移调度 · 修补 · 文创合成 · 问答 · 论坛"],
    ["算法层", "Reinhard 色彩迁移 · Telea 修复 · 纹样合成"],
    ["数据层", "SQLite 数据库 + 本地文件系统"],
  ];
  layers.forEach((l, i) => {
    const y = 1.82 + i * 0.78;
    s.addText([
      { text: l[0] + "  ", options: { fontFace: SERIF, fontSize: 12, bold: true, color: CINNABAR } },
      { text: l[1], options: { fontFace: SANS, fontSize: 9.5, color: INK } },
    ], { x: 5.55, y, w: 4.0, h: 0.68, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, valign: "middle", indent: 0.12 });
  });
  s.addText([
    { text: "性能指标：", options: { fontFace: SANS, fontSize: 10, bold: true, color: CINNABAR } },
    { text: "风格迁移 < 5s · 壁画修补 < 10s · 文创生成 < 5s", options: { fontFace: SANS, fontSize: 10, color: INK } },
  ], { x: 5.55, y: 4.96, w: 4.0, h: 0.42, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, valign: "middle", indent: 0.12 });
  addFooter(s, 11);
  s.addNotes("技术可行性：系统基于Python 3.10与PySide6构建桌面端，OpenCV与NumPy完成图像处理，SQLite零配置持久化，Coze平台提供智能问答——全部为成熟开源技术。架构上分为表现层、业务逻辑层、算法层、数据层四层，模块解耦、易于维护。性能上风格迁移5秒内、壁画修补10秒内可完成。");
  s.render();
}

// ============================================================
// SLIDE 12 — 技术可行性 · 核心算法与前期基础
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "03 · 技术可行性分析", "核心算法可靠，前期成果扎实");
  s.addText([
    { text: "前期基础 · 已获软件著作权  ", options: { fontFace: SANS, fontSize: 12.5, bold: true, color: CREAM } },
    { text: "《基于图像处理的西夏壁画渲染系统》", options: { fontFace: SERIF, fontSize: 12.5, bold: true, color: GOLD } },
    { text: "  —— 团队已跑通图像处理渲染链路，技术风险可控", options: { fontFace: SANS, fontSize: 10, color: CREAM } },
  ], { x: CONTENT_X, y: 1.22, w: CONTENT_W, h: 0.62, fill: { color: CINNABAR_D }, align: "center", valign: "middle" });
  const algos = [
    ["Reinhard 色彩迁移", "LAB 空间逐通道匹配均值与标准差，输出壁画色调"],
    ["纹理注入", "高频纹理分量按权重叠加，模拟笔触与颗粒感"],
    ["Telea 壁画修补", "快速行进法由外向内传播，补全破损区域"],
    ["CLAHE 古旧化", "自适应均衡恢复对比度，噪点暗角增强斑驳感"],
  ];
  algos.forEach((a, i) => {
    const x = CONTENT_X + i * 2.3;
    s.addText([
      { text: a[0], options: { fontFace: SERIF, fontSize: 11.5, bold: true, color: CINNABAR, breakLine: true } },
      { text: "\n" + a[1], options: { fontFace: SANS, fontSize: 9, color: BROWN } },
    ], { x, y: 2.0, w: 2.16, h: 1.28, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, align: "center", valign: "middle", paraSpaceAfter: 4 });
  });
  s.addText("智能问答工作流（Coze 平台）", { x: CONTENT_X, y: 3.44, w: 4.3, h: 0.26, fontFace: SANS, fontSize: 10.5, bold: true, color: BROWN, margin: 0 });
  s.addImage({ path: "ppt_assets/coze_workflow_2371x816.png", x: CONTENT_X, y: 3.72, w: 4.3, h: 1.4 });
  s.addText([
    { text: "意图识别 → 路由选择 → 知识库检索", options: { fontFace: SANS, fontSize: 10.5, bold: true, color: INK, breakLine: true } },
    { text: "\n喂入西夏历史、文字、壁画、服饰知识库；文化相关问题由大模型结合知识库作答并联网搜索兜底，无关问题友好引导 —— 有效降低大模型调用成本。", options: { fontFace: SANS, fontSize: 9.5, color: BROWN } },
  ], { x: 5.0, y: 3.44, w: 4.55, h: 1.68, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, valign: "middle", indent: 0.12, paraSpaceAfter: 4 });
  addFooter(s, 12);
  s.addNotes("算法层面，四个核心算法均已实现并验证：Reinhard色彩迁移输出壁画色调、纹理注入模拟笔触颗粒、Telea快速行进法修补破损、CLAHE恢复对比度并做古旧化。更重要的是，团队前期已获得《基于图像处理的西夏壁画渲染系统》软件著作权，技术链路完整跑通。下方是Coze智能体工作流，通过意图识别和知识库检索降低调用成本。");
  s.render();
}

// ============================================================
// SLIDE 13 — 经济可行性 · 经费预算
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "04 · 经济可行性分析", "经济可行性：总预算一万元，轻量可控");
  s.addChart(pres.charts.DOUGHNUT, [{
    name: "经费预算",
    labels: ["设备与材料 ¥5900", "调研与实践 ¥2600", "基础运营 ¥1000", "应急备用 ¥500"],
    values: [5900, 2600, 1000, 500],
  }], {
    x: 0.45, y: 1.3, w: 3.75, h: 3.55,
    chartColors: [CINNABAR, OCHRE, BROWN, GREEN],
    chartArea: { fill: { color: PAPER } },
    showLegend: true, legendPos: "b", legendColor: INK, legendFontSize: 9.5, legendFontFace: SANS,
    showPercent: true, dataLabelColor: CREAM, dataLabelFontSize: 9.5,
    holeSize: 55,
  });
  s.addText([
    { text: "总预算  ", options: { fontFace: SANS, fontSize: 13, bold: true, color: INK } },
    { text: "¥10,000", options: { fontFace: SERIF, fontSize: 26, bold: true, color: CINNABAR } },
    { text: "  元", options: { fontFace: SANS, fontSize: 12, color: INK } },
  ], { x: 4.5, y: 1.3, w: 5.05, h: 0.7, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, align: "center", valign: "middle" });
  const rows = [
    ["设备与材料费", "¥5,900", "开发工具与耗材 · 服务器租赁与 API 调用 · NVIDIA T4 GPU 云 · 软件维护"],
    ["调研和实践费", "¥2,600", "文献资料与数据库 · 试点调研与推广 · 实地考察与数据采集"],
    ["基础运营费", "¥1,000", "日常系统运转、维护与优化"],
    ["应急备用金", "¥500", "设备紧急维护 · 临时调研补充"],
  ];
  rows.forEach((r, i) => {
    const y = 2.18 + i * 0.68;
    s.addText([
      { text: r[0] + "  ", options: { fontFace: SERIF, fontSize: 11.5, bold: true, color: INK } },
      { text: r[1], options: { fontFace: SERIF, fontSize: 11.5, bold: true, color: CINNABAR } },
      { text: "\n" + r[2], options: { fontFace: SANS, fontSize: 8.5, color: MUTED } },
    ], { x: 4.5, y, w: 5.05, h: 0.6, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, valign: "middle", indent: 0.12, paraSpaceAfter: 2 });
  });
  s.addText([
    { text: "成本控制：", options: { fontFace: SANS, fontSize: 10, bold: true, color: CINNABAR } },
    { text: "纯 CPU 离线运行、开源技术栈为主，无持续算力与授权成本，边际成本低。", options: { fontFace: SANS, fontSize: 10, color: INK } },
  ], { x: 4.5, y: 4.94, w: 5.05, h: 0.4, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, valign: "middle", indent: 0.12 });
  addFooter(s, 13);
  s.addNotes("经济可行性：项目总预算一万元。其中设备与材料费5900元，占大头，主要用于开发工具、服务器与API调用、T4 GPU云资源租赁；调研与实践费2600元；基础运营1000元；应急备用500元。由于系统采用开源技术栈、纯CPU离线运行，后续没有持续的算力与授权成本，经济上完全可行。");
  s.render();
}

// ============================================================
// SLIDE 14 — 未来计划 · 甘特图
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: PAPER };
  addHeader(s, "05 · 未来计划", "未来计划：八周五阶段推进");
  s.addImage({ path: "ppt_assets/gantt_1779x940.png", x: 0.45, y: 1.26, w: 6.35, h: 3.36 });
  const phases = [
    ["第 1–2 周", "需求调研与原型设计"],
    ["第 3–5 周", "风格迁移与修补算法开发"],
    ["第 4–6 周", "文创工坊与衍生合成"],
    ["第 5–6 周", "西夏知库与交流论坛"],
    ["第 7–8 周", "系统集成 · 测试 · 文档撰写"],
  ];
  phases.forEach((p, i) => {
    const y = 1.26 + i * 0.68;
    s.addText([
      { text: p[0] + "  ", options: { fontFace: SERIF, fontSize: 11, bold: true, color: CINNABAR } },
      { text: p[1], options: { fontFace: SANS, fontSize: 9.5, color: INK } },
    ], { x: 7.05, y, w: 2.5, h: 0.6, fill: { color: CARD }, line: { color: BORDER, width: 0.75 }, valign: "middle", indent: 0.1 });
  });
  s.addText([
    { text: "阶段目标：", options: { fontFace: SANS, fontSize: 10.5, bold: true, color: CINNABAR } },
    { text: "形成可运行、可演示、可交付的桌面软件系统，完成结题并申请相关论文。", options: { fontFace: SANS, fontSize: 10.5, color: INK } },
  ], { x: CONTENT_X, y: 4.78, w: CONTENT_W, h: 0.42, fill: { color: CARD2 }, line: { color: GOLD, width: 0.75 }, valign: "middle", indent: 0.15 });
  addFooter(s, 14);
  s.addNotes("最后是未来计划。项目总体周期8周，分五个阶段推进：前两周需求调研与原型设计，第3到5周完成核心算法开发，第4到6周完成文创工坊，第5到6周完成知库与论坛，最后两周系统集成、测试与文档撰写。目标是形成可运行、可演示、可交付的桌面软件，完成结题并申请相关论文。");
  s.render();
}

// ============================================================
// SLIDE 15 — 结尾
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: INK };
  s.addShape(pres.shapes.RECTANGLE, { x: 0.28, y: 0.28, w: 9.44, h: 5.06, fill: { type: "none" }, line: { color: GOLD, width: 1.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.38, y: 0.38, w: 9.24, h: 4.86, fill: { type: "none" }, line: { color: BROWN, width: 0.75 } });
  s.addText("谢谢聆听 · 恳请批评指正", { x: 1.5, y: 2.0, w: 7, h: 0.95, fontFace: SERIF, fontSize: 36, bold: true, color: CREAM, align: "center", valign: "middle", charSpacing: 2.5 });
  s.addShape(pres.shapes.RECTANGLE, { x: 4.82, y: 3.14, w: 0.12, h: 0.12, fill: { color: CINNABAR }, rotate: 45 });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.06, y: 3.14, w: 0.12, h: 0.12, fill: { color: GOLD }, rotate: 45 });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.3, y: 3.14, w: 0.12, h: 0.12, fill: { color: CINNABAR }, rotate: 45 });
  s.addText("基于风格迁移的西夏文化衍生品开发系统 ·「塞上密卷」", { x: 1.5, y: 3.5, w: 7, h: 0.36, fontFace: SERIF, fontSize: 14, color: GOLD, align: "center", charSpacing: 1 });
  s.addText("汇报人：林奕淞    指导教师：马子睿", { x: 1.5, y: 3.95, w: 7, h: 0.3, fontFace: SANS, fontSize: 11, color: CREAM, align: "center" });
  s.addNotes("以上就是本项目的全部汇报内容。我们相信，塞上密卷能够让沉睡的西夏文化在数字时代焕发新生。恳请各位老师批评指正，谢谢！");
  s.render();
}

// ============================================================
pres.writeFile({ fileName: "塞上密卷_答辩PPT.pptx" }).then(() => console.log("DONE"));
