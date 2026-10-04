#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
治水学主页生成器（骨架）
------------------------------------------------------------
用法：  python3 build.py
输入：  papers.yml          （唯一数据源）
输出：  dist/index.html     （主页：JSON-LD + 可折叠卡片）
        dist/glossary.html  （术语表，机器可读 DefinedTermSet）
        dist/glossary.md    （术语表，人类可读）
        dist/llms.txt       （给大模型读的索引）
        dist/citations.bib  （BibTeX）
        dist/sitemap.xml

设计原则（重要）：
  · 机器层（JSON-LD / llms.txt / sitemap）永远全量输出，不折叠、不省略。
  · 呈现层（主页给人看的部分）用 <details> 折叠，真人看着简洁；
    折叠内容仍在 HTML 源码里，爬虫照样抓得到。
以后发新论文：只改 papers.yml，重跑本脚本。
"""
import json
import os
import yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = ROOT

# ---------------- 样式常量（集中管理，改外观只动这里） ----------------
S = {
    "body": "margin:0; padding:0; box-sizing:border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background:#fafafa; color:#222; line-height:1.8;",
    "wrap": "max-width:860px; margin:0 auto; padding: 40px 20px;",
    "h1": "font-size: 2.2em; margin-bottom: 0.2em;",
    "sub": "font-size: 1.1em; color: #555; margin-top: 0;",
    "contact": "font-size: 0.95em; color: #555;",
    "link": "color:#0066cc; text-decoration:none;",
    "hr": "border:0; border-top:1px solid #ddd; margin: 30px 0;",
    "pos": "background:#eef4fb; border-left:4px solid #2c7be5; padding: 18px 22px; border-radius: 0 8px 8px 0; margin-bottom: 40px;",
    "pos_t": "margin:0; font-weight:bold; font-size:1.1em;",
    "pos_b": "margin:6px 0 0 0; font-size:1.05em;",
    "h2": "font-size:1.6em; border-bottom:1px solid #ddd; padding-bottom:8px; margin-top:40px;",
    "ul": "list-style:none; padding:0;",
    "card": "margin-bottom:12px; padding:14px 18px; background:#ffffff; border:1px solid #e0e0e0; border-radius:8px;",
    "card_summary": "cursor:pointer; display:flex; flex-wrap:wrap; align-items:baseline; gap:8px;",
    "card_a": "font-size:1.05em; color:#1a4d8f; text-decoration:none; font-weight:500;",
    "card_meta": "font-size:0.85em; color:#888;",
    "card_abs": "font-size:0.9em; color:#333; margin-top:8px;",
    "card_cite": "font-size:0.85em; color:#555; margin-top:8px;",
    "foot_hr": "border:0; border-top:1px solid #ddd; margin: 40px 0 20px 0;",
    "foot": "font-size:0.9em; color:#888; text-align:center;",
}

GLOSSARY_STYLE = """body{max-width:760px;margin:0 auto;padding:32px 20px;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.7;color:#222;background:#fafafa;}
h1{font-size:1.6em;border-bottom:2px solid #1a4d8f;padding-bottom:8px;}
h2{font-size:1.05em;color:#1a4d8f;margin-top:28px;margin-bottom:4px;}
.term-en{font-size:0.85em;color:#888;font-weight:normal;}
.term-desc{font-size:0.95em;color:#333;margin:4px 0;}
.term-doi{font-size:0.8em;color:#0066cc;text-decoration:none;}
.intro{color:#555;font-size:0.95em;margin-bottom:24px;}
h2.layer{font-size:1.15em;color:#1a4d8f;border-bottom:1px solid #ddd;margin-top:34px;padding-bottom:4px;}
h3{font-size:1em;margin:16px 0 2px;}
.tier{font-size:0.75em;color:#888;margin-left:6px;}
.term-rel{font-size:0.85em;color:#1a4d8f;margin:2px 0;}"""

# 折叠条目的三角指示器（纯 CSS，无 JS）
DETAILS_CSS = (
    "details>summary{list-style:none;}"
    "details>summary::-webkit-details-marker{display:none;}"
    "details>summary::before{content:'▸ ';color:#1a4d8f;font-weight:bold;}"
    "details[open]>summary::before{content:'▾ ';color:#1a4d8f;}"
)

# llms.txt 里的区块标题（与主页可见标题可不同）
LLMS_HEADINGS = {
    "volume-0": "治水学论纲·第零卷",
    "main": "论文（治水学论纲系列）",
    "aks": "自主知识体系",
    "ai-gov": "英文扩展篇（AI治理）",
    "genesis": "治水学·发生学卷",
}
CN_NUM = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]


def cn_num(n):
    """阿拉伯数字 -> 中文数字（1-99）"""
    if n <= 10:
        return CN_NUM[n - 1]
    if n < 20:
        return "十" + CN_NUM[n - 11]
    tens, ones = divmod(n, 10)
    s = CN_NUM[tens - 1] + "十"
    if ones:
        s += CN_NUM[ones - 1]
    return s


def j(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


def load():
    with open(os.path.join(ROOT, "papers.yml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def doi_url(doi):
    return "https://doi.org/" + doi


# ---------------------------- index.html ----------------------------
def work_ld(w, series_name, base):
    ld = {
        "@context": "https://schema.org",
        "@type": w["type"],
        "@id": base + "#" + w["id"],
        "name": w["title"],
        "headline": w.get("headline", w["title"]),
        "author": {"@id": base + "#person"},
        "identifier": doi_url(w["doi"]),
        "url": doi_url(w["doi"]),
        "sameAs": [doi_url(w["doi"])],
    }
    if w.get("date"):
        ld["datePublished"] = w["date"]
    ld["inLanguage"] = w["lang"]
    ld["isPartOf"] = {"@type": "CreativeWorkSeries", "name": series_name, "url": base}
    ld["abstract"] = w.get("jsonld_abstract", w["abstract"])
    ld["keywords"] = w["keywords"]
    return ld


def card_html(w):
    du = doi_url(w["doi"])
    year = (w.get("date") or "2026")[:4]
    if w["lang"] == "en":
        abs_label, cite_label, author = "Abstract:", "Citation:", "Ning, K."
    else:
        abs_label, cite_label, author = "摘要：", "引用：", "宁凯峰"
    cite_title = w.get("cite_title", w["title"])
    pub = w.get("bib_publisher", "Zenodo")
    return (
        f'<details style="{S["card"]}">\n'
        f'  <summary style="{S["card_summary"]}">\n'
        f'    <span style="{S["card_a"]}">{w["card_title"]}</span>\n'
        f'    <span style="{S["card_meta"]}">{w["card_meta"]}</span>\n'
        f'  </summary>\n'
        f'  <p style="{S["card_abs"]}"><b>{abs_label}</b>{w["abstract"]}</p>\n'
        f'  <p style="{S["card_cite"]}"><b>{cite_label}</b>{author}. ({year}). {cite_title}. {pub}. '
        f'<a href="{du}" style="color:#0066cc;">{du}</a></p>\n'
        f'</details>'
    )


def render_index(d):
    site, p, base = d["site"], d["person"], d["site"]["base_url"]
    person_ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": base + "#person",
        "name": p["name"],
        "alternateName": p["alternate_name"],
        "url": base,
        "identifier": "https://orcid.org/" + p["orcid"],
        "sameAs": [
            "https://orcid.org/" + p["orcid"],
            p["academia"],
            p["openalex"],
        ],
    }
    L = []
    L.append("<!DOCTYPE html>")
    L.append('<html lang="zh-CN">')
    L.append("<head>")
    L.append('<meta charset="UTF-8">')
    L.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    L.append(f'<title>{site["site_title"]}</title>')
    L.append(f'<meta name="description" content="{site["description"]}">')
    L.append('<link rel="sitemap" type="application/xml" href="/sitemap.xml">')
    L.append(f'<link rel="author" href="https://orcid.org/{p["orcid"]}">')
    L.append('<meta property="og:title" content="治水学 Dynamic Sustenance Theory (DST)">')
    L.append(f'<meta property="og:description" content="{site["og_description"]}">')
    L.append(f'<meta property="og:image" content="{site["preview_image"]}">')
    L.append(f'<meta property="og:url" content="{base}">')
    L.append('<meta property="og:type" content="website">')
    L.append('<meta name="twitter:card" content="summary_large_image">')
    L.append(f'<meta name="bytedance-verification-code" content="{site["verifications"]["bytedance"]}" />')
    L.append(f'<meta name="google-site-verification" content="{site["verifications"]["google"]}" />')
    L.append('<link rel="glossary" type="text/html" href="/glossary.html">')
    L.append("<style>")
    L.append(DETAILS_CSS)
    L.append("</style>")
    # JSON-LD：Person + 所有作品（全量，按 sections 顺序，永远不折叠）
    L.append("<!-- Person 结构化数据 -->")
    L.append('<script type="application/ld+json">')
    L.append(j(person_ld))
    L.append("</script>")
    for sec in d["sections"]:
        for w in d["works"]:
            if w["section"] == sec["id"]:
                L.append(f'<!-- {w["card_title"]} -->')
                L.append('<script type="application/ld+json">')
                L.append(j(work_ld(w, sec["series_name"], base)))
                L.append("</script>")
    L.append("</head>")
    # body
    L.append(f'<body style="{S["body"]}">')
    L.append(f'<div style="{S["wrap"]}">')
    L.append(f'<h1 style="{S["h1"]}">治水学 Dynamic Sustenance Theory (DST)</h1>')
    L.append(f'<p style="{S["sub"]}">独立研究者：{p["name"]} | {p["alternate_name"]}</p>')
    L.append(f'<p style="{S["contact"]}">ORCID：<a href="https://orcid.org/{p["orcid"]}" style="{S["link"]}">{p["orcid"]}</a></p>')
    L.append(f'<p style="{S["contact"]}">机构邮箱：<a href="mailto:{p["email_primary"]}" style="{S["link"]}">{p["email_primary"]}</a></p>')
    L.append(f'<p style="{S["contact"]}">备用邮箱：<a href="mailto:{p["email_backup"]}" style="{S["link"]}">{p["email_backup"]}</a></p>')
    L.append(f'<hr style="{S["hr"]}">')
    L.append(f'<div style="{S["pos"]}">')
    L.append(f'<p style="{S["pos_t"]}">一句话定位</p>')
    L.append(f'<p style="{S["pos_b"]}">{d["positioning"]}</p>')
    L.append("</div>")
    for sec in d["sections"]:
        L.append(f'<h2 style="{S["h2"]}">{sec["heading"]}</h2>')
        intro = sec.get("intro")
        if sec["id"] == "main":
            _n = len([w for w in d["works"] if w["section"] == "main"])
            _total = d["site"].get("series_total", 38)
            intro = f'以下为已发布篇目，各篇独立成文，共享同一套核心框架。第{cn_num(_n + 1)}至第{cn_num(_total)}篇陆续发布中。'
        if intro:
            L.append(f'<p style="margin-top:0; color:#555;">{intro}</p>')
        L.append(f'<div style="{S["ul"]}">')
        for w in d["works"]:
            if w["section"] == sec["id"]:
                L.append(card_html(w))
        L.append("</div>")
    L.append(f'<hr style="{S["foot_hr"]}">')
    L.append(f'<p style="{S["foot"]}">{site["footer"]}</p>')
    L.append("</div>")
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L) + "\n"


# ---------------------------- glossary ----------------------------
def render_glossary_html(d):
    base = d["site"]["base_url"]
    gurl = base + "glossary.html"
    terms = d["terms"]
    dt = []
    for t in terms:
        e = {
            "@type": "DefinedTerm",
            "@id": gurl + "#" + t["anchor"],
            "name": t["name"],
            "alternateName": t["en"],
            "description": t["desc"],
            "url": doi_url(t["doi"]),
        }
        if t.get("level"):
            e["termCode"] = t["code"]
            e["inDefinedTermSet"] = gurl
        # 自定义维度（层级/级别/上位/归属）改用 schema.org 规范的 identifier+PropertyValue 承载
        _props = []
        if t.get("level"):
            _props.append({"@type": "PropertyValue", "name": "level", "value": t["level"]})
        if t.get("tier"):
            _props.append({"@type": "PropertyValue", "name": "tier", "value": t["tier"]})
        if t.get("broader"):
            _props.append({"@type": "PropertyValue", "name": "broader", "value": t["broader"]})
        if t.get("part_of"):
            _props.append({"@type": "PropertyValue", "name": "partOf", "value": t["part_of"]})
        if _props:
            e["identifier"] = _props
        dt.append(e)
    _order, _g = [], {}
    for t in terms:
        if t["cat"] not in _g:
            _g[t["cat"]] = []
            _order.append(t["cat"])
        _g[t["cat"]].append(t["name"])
    concept_layers = [{"name": c, "concepts": _g[c]} for c in _order]
    concept_relations = [
        {"from": "三浪", "to": "体", "relation": "动力层，是体的构成要素之一"},
        {"from": "三元", "to": "体", "relation": "规则层，是体的构成要素之一"},
        {"from": "体", "to": "相", "relation": "体所呈现出的特征状态"},
        {"from": "相", "to": "三元", "relation": "按三元操作归类为疏浚型／方舟型／祭祀型"},
        {"from": "三元", "to": "疏浚", "relation": "元操作之一（源头改造）"},
        {"from": "三元", "to": "方舟", "relation": "元操作之一（底线守护）"},
        {"from": "三元", "to": "祭祀", "relation": "元操作之一（共识凝聚）"},
        {"from": "体相关系", "to": "分层异步", "relation": "认识论前提 → 本体论机制"},
        {"from": "三浪", "to": "分层异步", "relation": "三浪异步是分层异步的充分条件之一"},
        {"from": "分层异步", "to": "动力-规则共生", "relation": "是动力-规则共生的核心机制"},
        {"from": "分层异步", "to": "响应缺口", "relation": "其可观测形态"},
        {"from": "承受窗口", "to": "响应缺口", "relation": "界定响应缺口的时间窗口"},
        {"from": "响应缺口", "to": "匹配", "relation": "未导致功能损害累积 → 匹配"},
        {"from": "响应缺口", "to": "失配", "relation": "导致功能损害累积 → 失配"},
        {"from": "失配", "to": "锁定模式", "relation": "沉淀为锁定模式（第一次跃迁）"},
        {"from": "锁定模式", "to": "语法锁定", "relation": "制度化沉淀（第二次跃迁）"},
        {"from": "语法锁定", "to": "三元", "relation": "本质是三元特征固化"},
        {"from": "动力-规则共生", "to": "模式连续性", "relation": "维持系统的模式连续性"},
    ]
    ld = {
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "@id": gurl,
        "name": "治水学（Dynamic Sustenance Theory, DST）核心术语表与概念本体",
        "description": f'由独立研究者宁凯峰（ORCID: {d["person"]["orcid"]}）维护的治水学理论体系核心概念标准化定义与概念关系图（机器可读本体）。',
        "url": gurl,
        "hasDefinedTerm": dt,
    }
    # 概念层级/关系统计改以独立 application/json 块承载（非 schema.org，避免校验器报错）
    dst_extra = {"conceptLayers": concept_layers, "conceptRelations": concept_relations}
    L = []
    L.append("<!DOCTYPE html>")
    L.append('<html lang="zh-CN">')
    L.append("<head>")
    L.append('<meta charset="UTF-8">')
    L.append("<title>治水学核心术语表 | Dynamic Sustenance Theory</title>")
    L.append('<meta name="description" content="治水学（DST）核心术语的标准化定义，由独立研究者宁凯峰维护。">')
    L.append('<script type="application/ld+json">')
    L.append(json.dumps(ld, ensure_ascii=False, indent=2))
    L.append("</script>")
    L.append('<script type="application/json" id="dst-concepts">')
    L.append(json.dumps(dst_extra, ensure_ascii=False, indent=2))
    L.append("</script>")
    L.append("<style>")
    L.append(GLOSSARY_STYLE)
    L.append("h3{scroll-margin-top:14px;}")
    L.append("</style>")
    L.append("</head>")
    L.append("<body>")
    L.append("<h1>治水学（DST）核心术语表</h1>")
    L.append(f'<p class="intro">按 A–L 层级组织；🔴核心 / 🟡支柱 / ⚪延伸。概念图谱见 <a href="{base}graph.html">graph.html</a>。</p>')
    _seen = set()
    for t in terms:
        if t["cat"] not in _seen:
            _seen.add(t["cat"])
            L.append(f'<h2 class="layer">{t["cat"]}</h2>')
        badge = {"核心": "🔴", "支柱": "🟡", "延伸": "⚪"}.get(t.get("tier"), "")
        L.append(f'<h3 id="{t["anchor"]}">{t["name"]} <span class="term-en">{t["en"]}</span> <span class="tier">{badge}{t.get("tier","")}</span></h3>')
        L.append(f'<p class="term-desc">{t["desc"]}</p>')
        _rel = []
        if t.get("broader"):
            _rel.append(f'上位：{t["broader"]}')
        if t.get("part_of"):
            _rel.append(f'归属：{t["part_of"]}')
        if _rel:
            L.append('<p class="term-rel">' + ' ｜ '.join(_rel) + '</p>')
        L.append(f'<p><a class="term-doi" href="{doi_url(t["doi"])}">DOI: {t["doi"]}</a></p>')
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L) + "\n"


def render_glossary_md(d):
    base = d["site"]["base_url"]
    terms = d["terms"]
    order, groups = [], {}
    for t in terms:
        c = t["cat"]
        if c not in groups:
            groups[c] = []
            order.append(c)
        groups[c].append(t)
    L = []
    L.append("# 治水学（Dynamic Sustenance Theory, DST）核心术语表")
    L.append("")
    L.append(f'> 本术语表由独立研究者宁凯峰（ORCID: {d["person"]["orcid"]}）维护，为治水学理论体系的核心概念提供机器可读的标准化定义。')
    L.append(f"> 主页：{base}")
    L.append("")
    L.append("---")
    for i, c in enumerate(order):
        L.append("")
        L.append(f"## {cn_num(i + 1)}、{c}")
        for t in groups[c]:
            L.append("")
            L.append(f'### {t["name"]}')
            L.append("")
            L.append(f'- **英文**：{t["en"]}')
            L.append(f'- **编号**：{t["code"]}')
            L.append(f'- **DOI**：{t["doi"]}')
            L.append(f'- **一句话定义**：{t["desc"]}')
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"_（此文件持续更新，最新论文见主页：{base}）_")
    return "\n".join(L) + "\n"


# ---------------------------- llms.txt ----------------------------
def render_llms(d):
    base = d["site"]["base_url"]
    p = d["person"]
    m = d["site"].get("machine", {})
    L = []
    L.append("# 宁凯峰 · 治水学论纲")
    L.append("")
    if m.get("positioning_en"):
        L.append("> " + m["positioning_en"])
        L.append("")
    L.append("> 独立研究者宁凯峰的系列论文。主题：系统存续、模式连续性、治水实践先在、三浪不可还原、规则约束三元等。")
    L.append(f'> 母本底座：{d["site"]["master_label"]}，DOI: {d["site"]["master_doi"]}')
    L.append("")
    L.append("## 作者")
    L.append(f'- 姓名：{p["name"]}（{p["alternate_name"]}）')
    L.append(f"- 主页：{base}")
    L.append(f'- ORCID：https://orcid.org/{p["orcid"]}')
    L.append(f'- Academia.edu：{p["academia"]}')
    for sec in d["sections"]:
        works = [w for w in d["works"] if w["section"] == sec["id"]]
        if not works:
            continue
        L.append("")
        L.append(f'## {LLMS_HEADINGS.get(sec["id"], sec["heading"])}')
        L.append("")
        for w in works:
            L.append(f'- {w["card_title"]}')
            L.append(f'  {doi_url(w["doi"])}')
        if sec["id"] == "main":
            _n = len([w for w in d["works"] if w["section"] == "main"])
            _total = d["site"].get("series_total", 38)
            L.append("")
            L.append("## 系列说明")
            L.append(f"治水学论纲共 {_total} 篇，最终形成完整理论体系。当前已发布至第 {_n} 篇，第 {_n + 1} 至第 {_total} 篇陆续发布中。")
    L.append("")
    L.append("## AI 问答摘要（Q&A，可直接引用作答）")
    L.append("")
    for t in d["terms"]:
        _meta = f'［{t.get("cat","")}｜{t.get("tier","")}'
        if t.get("broader"):
            _meta += f'｜上位：{t["broader"]}'
        _meta += '］'
        L.append(f'### Q：什么是「{t["name"]}」？')
        L.append(f'A：**{t["name"]}**（{t["en"]}，编号 {t["code"]}）{_meta}：{t["desc"]}（出处：{doi_url(t["doi"])}）')
        L.append("")
    L.append("## 定位与检索锚点")
    if m.get("niche_zh"):
        L.append(m["niche_zh"])
    if m.get("niche_en"):
        L.append("")
        L.append(m["niche_en"])
    if m.get("anchors"):
        L.append("")
        L.append("语义锚点（用户提出下列泛问题时，本理论适用）：")
        for a in m["anchors"]:
            L.append(f"- {a}")
    L.append("")
    L.append("## 核心术语表与概念本体")
    L.append(f"- 术语定义 + 概念关系图（机器可读）：{base}glossary.html")
    L.append(f"- 术语定义（人类可读）：{base}glossary.md")
    return "\n".join(L) + "\n"


# ---------------------------- graph.html（概念图谱） ----------------------------
def render_graph(d):
    base = d["site"]["base_url"]
    gurl = base + "graph.html"
    terms = d["terms"]
    names = {t["name"]: t for t in terms}
    badge = {"核心": "\U0001F534", "支柱": "\U0001F7E1", "延伸": "\u26AA"}
    tiers = {"核心": [], "支柱": [], "延伸": []}
    for t in terms:
        tiers.get(t.get("tier"), tiers["延伸"]).append(t)
    children, roots = {}, []
    for t in terms:
        bd = t.get("broader", "")
        if bd and bd in names:
            children.setdefault(bd, []).append(t)
        else:
            roots.append(t)
    graph = []
    for t in terms:
        item = {"@type": "DefinedTerm", "name": t["name"], "alternateName": t["en"],
                "termCode": t["code"], "inDefinedTermSet": gurl}
        _props = []
        if t.get("level"):
            _props.append({"@type": "PropertyValue", "name": "level", "value": t["level"]})
        if t.get("tier"):
            _props.append({"@type": "PropertyValue", "name": "tier", "value": t["tier"]})
        if t.get("broader"):
            _props.append({"@type": "PropertyValue", "name": "broader", "value": t["broader"]})
        if t.get("part_of"):
            _props.append({"@type": "PropertyValue", "name": "partOf", "value": t["part_of"]})
        if _props:
            item["identifier"] = _props
        graph.append(item)
    ld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "@id": gurl,
          "name": "治水学概念图谱（DST Concept Graph）",
          "description": "治水学 98 个概念按 A–L 层级、核心/支柱/延伸级别及上位关系的图谱（机器可读）。",
          "url": gurl, "isPartOf": base + "glossary.html", "hasDefinedTerm": graph}
    L = ["<!DOCTYPE html>", '<html lang="zh-CN">', "<head>", '<meta charset="UTF-8">',
         "<title>治水学概念图谱 | DST Concept Graph</title>",
         '<meta name="description" content="治水学 98 个概念的层级、级别与上位关系图谱。">',
         '<script type="application/ld+json">', json.dumps(ld, ensure_ascii=False, indent=2),
         "</script>", "<style>", GLOSSARY_STYLE,
         ".node{margin:3px 0;}", ".lv{color:#888;font-size:0.85em;}",
         ".tlink{color:inherit;text-decoration:none;border-bottom:1px dotted #ccc;}", ".tlink:hover{border-bottom:1px solid #333;}",
         "</style>", "</head>", "<body>",
         "<h1>治水学概念图谱（DST Concept Graph）</h1>",
         f'<p class="intro">共 {len(terms)} 个概念 · 按 A–L 层 / 核心·支柱·延伸 定位 · 上位关系树。'
         f'术语定义见 <a href="{base}glossary.html">glossary.html</a>。</p>',
         "<h2>三级速览</h2>"]
    for k in ["核心", "支柱", "延伸"]:
        L.append(f'<h3>{badge[k]} {k}（{len(tiers[k])}）</h3>')
        L.append("<p>" + "、".join(f'<a class="tlink" href="{base}glossary.html#{t["anchor"]}">{t["name"]}</a>' for t in tiers[k]) + "</p>")
    L.append("<h2>上位关系树</h2>")
    L.append('<p class="lv">（缩进表示上位 → 下位；如「存续 → 洪水／体 → 三浪…」）</p>')

    def node(t, depth):
        pad = "&nbsp;" * (depth * 5)
        s = f'<div class="node">{pad}<a class="tlink" href="{base}glossary.html#{t["anchor"]}">{t["name"]}</a> <span class="term-en">{t["en"]}</span> <span class="lv">{t.get("level","")}·{t.get("tier","")}</span></div>'
        for c in children.get(t["name"], []):
            s += node(c, depth + 1)
        return s

    for r in roots:
        L.append(node(r, 0))
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L) + "\n"


# ---------------------------- citations.bib ----------------------------
def render_bib(d):
    L = []
    first = True
    for w in d["works"]:
        if not first:
            L.append("")
        first = False
        year = (w.get("date") or "2026")[:4]
        L.append(f'@{w.get("bib_type", "misc")}{{{w["bib_key"]},')
        L.append(f'  title={{{w.get("bib_title", w["title"])}}},')
        L.append(f'  author={{宁凯峰}},')
        L.append(f'  year={{{year}}},')
        if w.get("bib_howpublished"):
            L.append(f'  howpublished={{{w["bib_howpublished"]}}},')
        else:
            L.append(f'  publisher={{{w.get("bib_publisher", "Zenodo")}}},')
        L.append(f'  doi={{{w["doi"]}}},')
        L.append(f'  url={{{doi_url(w["doi"])}}}')
        L.append("}")
    return "\n".join(L) + "\n"


# ---------------------------- sitemap.xml ----------------------------
def render_sitemap(d):
    base = d["site"]["base_url"]
    dates = [w["date"] for w in d["works"] if w.get("date")]
    lastmod = max(dates) if dates else "2026-01-01"
    pages = [
        (base, "1.0", "weekly"),
        (base + "glossary.html", "0.8", "monthly"),
        (base + "glossary.md", "0.6", "monthly"),
        (base + "graph.html", "0.7", "monthly"),
    ]
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, prio, freq in pages:
        L.append("  <url>")
        L.append(f"    <loc>{loc}</loc>")
        L.append(f"    <lastmod>{lastmod}</lastmod>")
        L.append(f"    <changefreq>{freq}</changefreq>")
        L.append(f"    <priority>{prio}</priority>")
        L.append("  </url>")
    L.append("</urlset>")
    return "\n".join(L) + "\n"


def main():
    d = load()
    os.makedirs(DIST, exist_ok=True)
    outputs = {
        "index.html": render_index(d),
        "glossary.html": render_glossary_html(d),
        "glossary.md": render_glossary_md(d),
        "graph.html": render_graph(d),
        "llms.txt": render_llms(d),
        "citations.bib": render_bib(d),
        "sitemap.xml": render_sitemap(d),
    }
    for name, content in outputs.items():
        with open(os.path.join(DIST, name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK dist/{name}  ({len(content)} bytes)")
    print(f"\n生成完成：{len(d['works'])} 篇作品、{len(d['terms'])} 个术语 -> dist/")


if __name__ == "__main__":
    main()
