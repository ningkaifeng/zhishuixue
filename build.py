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
import re
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
.term-rel{font-size:0.85em;color:#1a4d8f;margin:2px 0;}
.term-cases{font-size:0.85em;color:#1a4d8f;margin:2px 0;}
.term-case{color:#1a4d8f;text-decoration:none;border-bottom:1px dotted #ccc;}
.term-case:hover{border-bottom:1px solid #1a4d8f;}"""

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


# ---------------------------- 决策显影库（案例） ----------------------------
CASES_FILE = "cases.yml"
# 自动互链：只链"够独特"的术语，避免 体/相/结构 等短词误链
AUTOLINK_EXTRA = {"三浪", "三元", "疏浚", "方舟", "祭祀", "存续", "洪水", "失配", "破局"}


CASES_HOME = 6          # 主页展示的"最新/精选"案例数
CASES_DIR = os.path.join(ROOT, "data", "cases")   # 扩容用：每篇一个 yml


def load_cases():
    """案例来源：cases.yml（列表） + data/cases/*.yml（每篇一个），自动去重排序。"""
    out = []
    path = os.path.join(ROOT, CASES_FILE)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            out += (yaml.safe_load(f) or {}).get("cases", [])
    if os.path.isdir(CASES_DIR):
        for fn in sorted(os.listdir(CASES_DIR)):
            if not fn.endswith((".yml", ".yaml")):
                continue
            with open(os.path.join(CASES_DIR, fn), encoding="utf-8") as f:
                obj = yaml.safe_load(f) or {}
            if isinstance(obj, dict):
                out += obj.get("cases", [])
            elif isinstance(obj, list):
                out += obj
    seen, uniq = set(), []
    for c in out:
        if c.get("id") and c["id"] not in seen:
            seen.add(c["id"])
            uniq.append(c)
    uniq.sort(key=lambda c: c["id"])
    return uniq


def case_url(base, c):
    return base + "cases/" + c["id"] + ".html"


def _linkable_terms(d):
    out = {}
    for t in d["terms"]:
        n = t["name"]
        if len(n) >= 3 or n in AUTOLINK_EXTRA:
            out[n] = t["anchor"]
    return out


def link_concepts(text, d, base):
    """正文里出现的治水学术语名 -> 自动链接到术语表锚点（长词优先，避免子串误链）"""
    amap = _linkable_terms(d)
    if not amap:
        return text
    names = sorted(amap, key=len, reverse=True)
    pattern = re.compile("|".join(re.escape(n) for n in names))
    return pattern.sub(
        lambda mo: f'<a class="tlink" href="{base}glossary.html#{amap[mo.group(0)]}">{mo.group(0)}</a>',
        text)


CASE_STYLE = """
.case-top{font-size:0.9em;color:#555;margin-bottom:18px;}
.case-meta{font-size:0.85em;color:#888;margin:4px 0;}
.case-abs{font-size:1.02em;background:#eef4fb;border-left:4px solid #2c7be5;padding:14px 18px;border-radius:0 8px 8px 0;}
.case-sec{font-size:1em;color:#222;margin:6px 0 20px;}
.case-note{font-size:0.92em;color:#555;margin:6px 0 20px;background:#f6f6f6;padding:12px 16px;border-radius:8px;}
.tlink{color:inherit;text-decoration:none;border-bottom:1px dotted #ccc;}
.tlink:hover{border-bottom:1px solid #333;}
"""


CASES_INDEX_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>决策显影库（案例总览） | 治水学</title>
<meta name="description" content="治水学·决策显影库：把治水学工具用于真实历史、商业与治理决策的实践判例总览，可按归目、场景、治水学接口检索。">
<link rel="canonical" href="__URL__">
<script type="application/ld+json">
__LD__
</script>
<style>
body{max-width:860px;margin:0 auto;padding:28px 18px;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.7;color:#222;background:#fafafa;}
a{color:#0066cc;text-decoration:none;}
h1{font-size:1.5em;border-bottom:2px solid #1a4d8f;padding-bottom:8px;}
.top{font-size:0.9em;color:#555;}
.intro{color:#555;font-size:0.95em;}
.ctl{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0;}
.ctl input[type=search]{flex:1 1 220px;padding:8px 10px;border:1px solid #ccc;border-radius:8px;font-size:0.95em;}
.ctl select{padding:8px 6px;border:1px solid #ccc;border-radius:8px;font-size:0.9em;background:#fff;}
.ctl button{padding:8px 14px;border:1px solid #ccc;border-radius:8px;background:#fff;font-size:0.9em;}
.stat{color:#888;font-size:0.85em;}
.card{background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:12px 16px;margin-bottom:10px;}
.card .t{font-size:1.02em;color:#1a4d8f;font-weight:500;}
.card .m{font-size:0.82em;color:#888;}
.card .a{font-size:0.9em;color:#333;margin:6px 0;}
.card .k{font-size:0.82em;color:#555;}
.cl{border-bottom:1px dotted #ccc;}
.pager{display:flex;align-items:center;gap:12px;justify-content:center;margin:18px 0;}
.pager button{padding:8px 14px;border:1px solid #ccc;border-radius:8px;background:#fff;}
.pager span{font-size:0.9em;color:#555;}
.foot{font-size:0.82em;color:#888;text-align:center;}
</style>
</head>
<body>
<p class="top"><a href="/">← 治水学主页</a> ｜ <a href="/glossary.html">核心术语表</a> ｜ <a href="/graph.html">概念图谱</a></p>
<h1>决策显影库（案例总览）</h1>
<p class="intro">把治水学工具用于真实的历史、商业与治理决策，共 <b id="cnt">__TOTAL__</b> 篇判例；每篇标注所用「治水学接口」与「杠杆落点」。<br>机器可读索引：<a href="/cases-index.json">cases-index.json</a>（供 AI 与检索使用）</p>
<div class="ctl">
  <input id="q" type="search" placeholder="搜索：篇名 / 摘要 / 接口 / 杠杆 / 概念">
  <select id="fc"><option value="">全部归目</option></select>
  <select id="fs"><option value="">全部场景</option></select>
  <select id="fi"><option value="">全部接口</option></select>
  <button id="clr" type="button">清空</button>
</div>
<p class="stat" id="stat"></p>
<div id="list"></div>
<div class="pager">
  <button id="prev" type="button">← 上一页</button>
  <span id="pinfo"></span>
  <button id="next" type="button">下一页 →</button>
</div>
<p class="foot">共 <span id="cnt2">__TOTAL__</span> 篇 · 数据源 cases-index.json</p>
<script>
var PAGE = 24, DATA = [], page = 1;
function esc(s){return (s||'').replace(/[&<>"]/g, function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function fill(sel, key){
  var set = {};
  DATA.forEach(function(c){ if(c[key]) set[c[key]] = 1; });
  var el = document.getElementById(sel);
  Object.keys(set).sort().forEach(function(v){
    var o = document.createElement('option'); o.value = v;
    o.textContent = v + '（' + DATA.filter(function(c){return c[key]===v;}).length + '）';
    el.appendChild(o);
  });
}
function render(){
  var q = document.getElementById('q').value.trim().toLowerCase();
  var fc = document.getElementById('fc').value, fs = document.getElementById('fs').value, fi = document.getElementById('fi').value;
  var out = DATA.filter(function(c){
    if(fc && c.category !== fc) return false;
    if(fs && c.scene !== fs) return false;
    if(fi && c.interface !== fi) return false;
    if(q){
      var hay = [c.num,c.title,c.category,c.scene,c.interface,c.lever,c.abstract,(c.concepts||[]).map(function(o){return o.name;}).join(' ')].join(' ').toLowerCase();
      if(hay.indexOf(q) < 0) return false;
    }
    return true;
  });
  document.getElementById('stat').textContent = '匹配 ' + out.length + ' 篇';
  var pages = Math.max(1, Math.ceil(out.length / PAGE));
  if(page > pages) page = pages;
  var slice = out.slice((page-1)*PAGE, page*PAGE);
  document.getElementById('list').innerHTML = slice.map(function(c){
    var con = (c.concepts||[]).map(function(o){return '<a class="cl" href="/glossary.html#'+o.anchor+'">'+esc(o.name)+'</a>';}).join('、');
    return '<div class="card"><a class="t" href="'+esc(c.url)+'">'+esc(c.num)+'｜'+esc(c.title)+'</a>'
      + '<div class="m">'+esc(c.category)+' · '+esc(c.scene)+' · '+esc(c.date)+'</div>'
      + '<p class="a">'+esc(c.abstract)+'</p>'
      + '<div class="k"><b>接口：</b>'+esc(c.interface)+' ｜ <b>杠杆：</b>'+esc(c.lever)+(con?(' ｜ <b>关联概念：</b>'+con):'')+'</div></div>';
  }).join('');
  document.getElementById('pinfo').textContent = page + ' / ' + pages;
  document.getElementById('cnt').textContent = DATA.length;
  document.getElementById('cnt2').textContent = DATA.length;
}
function init(){
  fill('fc','category'); fill('fs','scene'); fill('fi','interface');
  ['q','fc','fs','fi'].forEach(function(id){
    document.getElementById(id).addEventListener('input', function(){ page = 1; render(); });
  });
  document.getElementById('clr').addEventListener('click', function(){
    document.getElementById('q').value = ''; document.getElementById('fc').value = '';
    document.getElementById('fs').value = ''; document.getElementById('fi').value = ''; page = 1; render();
  });
  document.getElementById('prev').addEventListener('click', function(){ if(page > 1){ page--; render(); } });
  document.getElementById('next').addEventListener('click', function(){ page++; render(); });
  render();
}
fetch('cases-index.json').then(function(r){return r.json();}).then(function(d){ DATA = d.cases || []; init(); })
  .catch(function(){ document.getElementById('list').innerHTML = '<p>案例数据加载失败；请直接访问 <a href="/cases-index.json">cases-index.json</a>。</p>'; });
</script>
</body>
</html>
"""


def render_cases_json(d):
    base = d["site"]["base_url"]
    amap = {t["name"]: t["anchor"] for t in d["terms"]}
    items = []
    for c in load_cases():
        items.append({
            "id": c["id"], "num": c["num"], "title": c["title"],
            "category": c.get("category", ""), "scene": c.get("scene", ""),
            "interface": c.get("interface", ""), "lever": c.get("lever", ""),
            "date": c.get("date", ""),
            "concepts": [{"name": n, "anchor": amap.get(n, "")} for n in c.get("concepts", [])],
            "abstract": c.get("abstract", ""),
            "source": c.get("source", ""),
            "url": case_url(base, c),
        })
    return json.dumps({"count": len(items), "cases": items}, ensure_ascii=False, indent=1) + "\n"


def render_terms_json(d):
    """terms.json —— 治水学术语本体：机器可直接取用/调用（含中英名、层级、上下位、相关判例、可引用锚点）"""
    base = d["site"]["base_url"]
    terms = d["terms"]
    byterm = cases_by_term(d)
    g = d.get("glossary", {})
    g_title = g.get("title", "治水学概念层级表（术语母表）")
    g_ver = g.get("version_label", "v1.0")
    g_date = g.get("date", "")
    author = d["person"]["name"]
    g_cited = f"{author}．{g_title}{g_ver}．{g_date}．{base}terms.json"
    subs, parts = {}, {}
    for t in terms:
        if t.get("broader"):
            subs.setdefault(t["broader"], []).append(t["name"])
        if t.get("part_of"):
            parts.setdefault(t["part_of"], []).append(t["name"])
    items = []
    for t in terms:
        items.append({
            "id": t["code"],
            "name": t["name"],
            "en": t["en"],
            "anchor": t["anchor"],
            "url": base + "glossary.html#" + t["anchor"],
            "definition": t["desc"],
            "layer": t.get("level", ""),
            "layerName": t["cat"].split("·")[-1].strip() if t.get("cat") else "",
            "tier": t.get("tier", ""),
            "broader": t.get("broader") or None,
            "partOf": t.get("part_of") or None,
            "hyponyms": subs.get(t["name"], []),
            "members": parts.get(t["name"], []),
            "cases": [{"id": c["id"], "title": c["title"], "url": case_url(base, c)}
                      for c in byterm.get(t["name"], [])],
            "citeKey": "dst-term-" + t["anchor"],
            "citedAs": f'{author}．「{t["name"]}」．{g_title}{g_ver}（{g_date}）．{base}glossary.html#{t["anchor"]}',
            "doi": doi_url(t["doi"]),
        })
    layers, seen = [], {}
    for t in terms:
        k = t.get("cat", "")
        if k not in seen:
            seen[k] = len(layers)
            layers.append({"id": t.get("level", ""), "name": k.split("·")[-1].strip(), "count": 0})
        layers[seen[k]]["count"] += 1
    obj = {
        "schema": "dst-terms/1.0",
        "name": "治水学核心术语本体（DST Core Terminology Ontology）",
        "source": base + "glossary.html",
        "masterDoi": d["site"]["master_doi"],
        "license": g.get("license", "CC BY 4.0"),
        "maintainer": {"name": d["person"]["name"],
                       "orcid": "https://orcid.org/" + d["person"]["orcid"]},
        "glossary": {
            "title": g_title,
            "titleEn": g.get("title_en", ""),
            "version": g.get("version", "1.0"),
            "versionLabel": g_ver,
            "date": g_date,
            "license": g.get("license", "CC BY 4.0"),
            "definitionAnchor": g.get("definition_anchor", ""),
            "translationAnchor": g.get("translation_anchor", ""),
            "basis": g.get("basis", ""),
            "citedAs": g_cited,
            "bibtexKey": g.get("citation_key", "dstterms"),
        },
        "count": len(items),
        "layers": layers,
        "usage": ("每个术语含中英文名、层级（layer）与级别（tier）、上位（broader）/"
                  "下位（hyponyms）、归属（partOf）/成员（members）、相关判例（cases）、"
                  "可引用锚点（url）、规范引用串（citedAs）与引用键（citeKey）、出处 DOI。"
                  "机器可据此直接取用治水学概念骨架，无需解析网页。引用整表用 glossary.citedAs，"
                  "引用单条术语用该条目的 citedAs。"),
        "terms": items,
    }
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


# 判例「治水学接口」→ 治水历刻度（用于案例自动挂载；术语按「（」前的主词匹配）
PHASE_BY_TERM = {
    "结构判断": "P0",
    "信号层": "P1",
    "分层异步": "P4",
    "响应缺口": "P5",
    "响应错位": "P15",
    "响应钝化": "P16",
    "响应锁定": "P17",
    "疏浚": "P10",
    "方舟": "P11",
    "祭祀": "P12",
    "破局": "P13",
}


def _iface_cell(interface):
    """把索引库的接口串映射到刻度 id：特判『对方』语境的响应缺口。"""
    t = (interface or "").split("（")[0].strip()
    if t == "响应缺口" and "对方" in (interface or ""):
        return "P14"
    return PHASE_BY_TERM.get(t, "")


def render_phases_json(d):
    """phases.json —— 治水历（定位刻度：物候/宜/忌 + 案例自动挂载）"""
    base = d["site"]["base_url"]
    ph = d.get("phases", {})
    amap = {t["name"]: t["anchor"] for t in d["terms"]}
    cases = load_cases()
    mount = {}
    for c in cases:
        pid = _iface_cell(c.get("interface"))
        if pid:
            mount.setdefault(pid, []).append(
                {"id": c["id"], "title": c["title"], "url": case_url(base, c)})
    lines = []
    lidx = {}
    for ln in ph.get("lines", []):
        item = {"id": ln["id"], "name": ln["name"], "note": ln.get("note", ""), "cells": []}
        lines.append(item)
        lidx[item["id"]] = item
    defs = {t["name"]: t for t in d["terms"]}

    def _match_term(s):
        """按『整串 → 去掉 · 后缀 → 去掉（）后缀 → 去掉半角空格』逐级尝试匹配母表术语名。"""
        for cand in (s.strip(), s.split("·")[0].strip(), s.split("（")[0].strip(),
                     s.split("（")[0].replace("（", "").strip()):
            if cand in defs:
                return cand
        return ""

    for cel in ph.get("cells", []):
        c2 = dict(cel)
        c2["mountedCases"] = mount.get(cel["id"], [])
        _hit = _match_term(cel.get("term", ""))
        c2["termAnchor"] = amap.get(_hit, "")
        c2["termDefined"] = bool(_hit)
        c2["termLinked"] = _hit
        lidx[cel["line"]]["cells"].append(c2)
    cells_n = sum(len(l["cells"]) for l in lines)
    mounted_n = sum(len(l["cells"][i]["mountedCases"]) for l in lines for i in range(len(l["cells"])))
    obj = {
        "schema": "dst-phases/1.0",
        "title": ph.get("title", "治水历"),
        "titleEn": ph.get("title_en", ""),
        "version": ph.get("version", "1.0"),
        "versionLabel": ph.get("version_label", "v1.0"),
        "date": ph.get("date", ""),
        "license": ph.get("license", "CC BY 4.0"),
        "source": base + "glossary.html",
        "definitionAnchor": ph.get("definition_anchor", ""),
        "maintainer": {"name": d["person"]["name"],
                       "orcid": "https://orcid.org/" + d["person"]["orcid"]},
        "idea": ph.get("idea", ""),
        "usage": ph.get("usage", ""),
        "principle": "只给坐标，不给答案；案例天天变，历不变——案例按接口自动挂载，刻度本身不随案例增减。",
        "taboos": ph.get("taboos", []),
        "counts": {"cells": cells_n, "mountedCases": mounted_n, "totalCases": len(cases)},
        "howToUse": ph.get("how_to_use", [
            "立界：先问『在哪个系统里、我在不在界内』，并请承压位置的主体确认。",
            "沿三刀走：辨势（三股力各在不在动）→ 定性（脱节走到哪一段）→ 定策（加哪股力）。",
            "输出坐标、不给答案：只说落在哪一格、宜什么、忌什么；博弈类另加一镜『观隙』。",
        ]),
        "lines": lines,
    }
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def render_cases_index(d):
    base = d["site"]["base_url"]
    url = base + "cases.html"
    n = len(load_cases())
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": url,
        "name": "决策显影库（案例总览）",
        "description": "治水学·决策显影库：把治水学工具用于真实历史、商业与治理决策的实践判例总览，可按归目、场景、治水学接口检索。",
        "url": url,
        "inLanguage": "zh-CN",
        "isPartOf": {"@type": "CreativeWorkSeries", "name": "治水学·决策显影库", "url": url},
        "about": {"@id": base + "glossary.html"},
    }
    return (CASES_INDEX_TPL
            .replace("__URL__", url)
            .replace("__LD__", j(ld))
            .replace("__TOTAL__", str(n)))


def case_card(c):
    return (
        f'<details style="{S["card"]}">\n'
        f'  <summary style="{S["card_summary"]}">\n'
        f'    <span style="{S["card_a"]}">{c["card_title"]}</span>\n'
        f'    <span style="{S["card_meta"]}">{c["card_meta"]}</span>\n'
        f'  </summary>\n'
        f'  <p style="{S["card_abs"]}"><b>摘要：</b>{c["abstract"]}</p>\n'
        f'  <p style="{S["card_cite"]}"><b>接口：</b>{c["interface"]} ｜ <b>杠杆：</b>{c["lever"]}</p>\n'
        f'  <p style="{S["card_cite"]}"><a href="cases/{c["id"]}.html" style="color:#0066cc;text-decoration:none;">查看完整判例 →</a></p>\n'
        f'</details>'
    )


def render_case_page(c, d):
    base = d["site"]["base_url"]
    url = case_url(base, c)
    amap = {t["name"]: t["anchor"] for t in d["terms"]}
    about = [{"@type": "DefinedTerm", "@id": base + "glossary.html#" + amap[nm], "name": nm}
             for nm in c.get("concepts", []) if nm in amap]
    ld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "@id": url,
        "name": c["card_title"],
        "headline": c["title"],
        "author": {"@id": base + "#person"},
        "identifier": c["id"],
        "url": url,
        "description": c["abstract"],
        "abstract": c["abstract"],
        "datePublished": c.get("date"),
        "inLanguage": "zh-CN",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "keywords": c.get("keywords", []),
        "isPartOf": {"@type": "CreativeWorkSeries", "name": "治水学·决策显影库", "url": base + "cases/"},
    }
    if about:
        ld["about"] = about
    if c.get("planet_url"):
        ld["sameAs"] = [c["planet_url"]]

    L = ["<!DOCTYPE html>", '<html lang="zh-CN">', "<head>", '<meta charset="UTF-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
         f'<title>{c["card_title"]} | 治水学·决策显影库</title>',
         f'<meta name="description" content="{c["abstract"]}">',
         f'<link rel="canonical" href="{url}">',
         '<script type="application/ld+json">', j(ld), "</script>",
         "<style>", GLOSSARY_STYLE, CASE_STYLE, "</style>", "</head>", "<body>",
         f'<p class="case-top"><a href="{base}">← 治水学主页</a> ｜ <a href="{base}glossary.html">核心术语表</a> ｜ <a href="{base}graph.html">概念图谱</a></p>',
         f'<h1>{c["num"]}｜{c["title"]}</h1>',
         f'<p class="case-meta">{c["category"]} ｜ {c["scene"]} ｜ 记录日期：{c.get("date","")} ｜ 许可：{c.get("license","")}</p>',
         f'<p class="case-abs">{c["abstract"]}</p>']
    for el in c.get("elements", []):
        L.append(f'<h2>{el["k"]}</h2>')
        L.append('<div class="case-sec">' + link_concepts(el["v"].strip(), d, base).replace("\n", "<br>") + "</div>")
    if about:
        links = "、".join(f'<a class="tlink" href="{base}glossary.html#{amap[nm]}">{nm}</a>'
                          for nm in c.get("concepts", []) if nm in amap)
        L.append("<h2>关联概念</h2>")
        L.append('<div class="case-sec">' + links + "</div>")
    if c.get("source_note"):
        L.append("<h2>信源备注</h2>")
        L.append('<div class="case-note">' + c["source_note"].strip().replace("\n", "<br>") + "</div>")
    if c.get("recorder_note"):
        L.append("<h2>记录人备注</h2>")
        L.append('<div class="case-note">' + link_concepts(c["recorder_note"].strip(), d, base).replace("\n", "<br>") + "</div>")
    if c.get("planet_url"):
        L.append(f'<p class="case-meta">知识星球原文：<a href="{c["planet_url"]}">{c["planet_url"]}</a></p>')
    L.append(f'<p class="case-meta">本判例收录于「治水学·决策显影库」 ｜ 官网存档：{url}</p>')
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L) + "\n"


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
    _cases = load_cases()
    if _cases:
        _feat = [c for c in _cases if c.get("featured")]
        _label = "精选案例" if _feat else "最新案例"
        _feat = _feat or _cases[-CASES_HOME:]
        L.append(f'<h2 style="{S["h2"]}">决策显影库（实践案例）</h2>')
        L.append(f'<p style="margin-top:0; color:#555;">把治水学工具用于真实的历史、商业与治理决策。现有 <b>{len(_cases)}</b> 篇判例；每篇标注所用「治水学接口」与「杠杆落点」。以下为{_label}：</p>')
        L.append(f'<div style="{S["ul"]}">')
        for _c in _feat:
            L.append(case_card(_c))
        L.append("</div>")
        L.append(f'<p style="margin-top:12px;"><a href="cases.html" style="color:#0066cc;text-decoration:none;font-weight:500;">查看全部 {len(_cases)} 篇案例（可搜索、按归目/场景/接口筛选）→</a></p>')
    L.append(f'<hr style="{S["foot_hr"]}">')
    L.append(f'<p style="{S["foot"]}">{site["footer"]}</p>')
    L.append("</div>")
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L) + "\n"


# ---------------------------- glossary ----------------------------
def cases_by_term(d):
    """术语名 -> 相关案例列表（概念↔案例反向索引）"""
    by_term = {}
    for c in load_cases():
        for n in c.get("concepts", []):
            by_term.setdefault(n, []).append(c)
    return by_term


def render_glossary_html(d):
    base = d["site"]["base_url"]
    gurl = base + "glossary.html"
    terms = d["terms"]
    _g = d.get("glossary", {})
    _g_title = _g.get("title", "治水学概念层级表（术语母表）")
    _g_ver = _g.get("version_label", "v1.0")
    _g_date = _g.get("date", "")
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
    L.append(f'<p class="intro">《{_g_title}》{_g_ver} ｜ {_g_date} ｜ 按 A–L 层级组织；🔴核心 / 🟡支柱 / ⚪延伸。概念图谱见 <a href="{base}graph.html">graph.html</a>｜机器可读术语本体见 <a href="{base}terms.json">terms.json</a>。</p>')
    _byterm = cases_by_term(d)
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
        _rc = _byterm.get(t["name"])
        if _rc:
            _links = "、".join(f'<a class="term-case" href="cases/{x["id"]}.html">{x["num"]}｜{x["title"]}</a>' for x in _rc)
            L.append(f'<p class="term-cases">相关案例：{_links}</p>')
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L) + "\n"


def render_glossary_md(d):
    base = d["site"]["base_url"]
    terms = d["terms"]
    _byterm = cases_by_term(d)
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
    _g = d.get("glossary", {})
    L.append(f'> 母表：《{_g.get("title", "治水学概念层级表（术语母表）")}》{_g.get("version_label", "v1.0")} ｜ {_g.get("date", "")}'
             + (f' ｜ 定义锚点：{_g["definition_anchor"]}｜英译锚点：{_g["translation_anchor"]}' if _g.get("definition_anchor") else ""))
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
            _rc = _byterm.get(t["name"])
            if _rc:
                _s = "、".join(f'{x["num"]}｜{x["title"]}（{base}cases/{x["id"]}.html）' for x in _rc)
                L.append(f'- **相关案例**：{_s}')
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
    g = d.get("glossary", {})
    _g_title = g.get("title", "治水学概念层级表（术语母表）")
    _g_ver = g.get("version_label", "v1.0")
    _g_date = g.get("date", "")
    _author = d["person"]["name"]
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
    _cs = load_cases()
    if _cs:
        _bycat = {}
        for _c in _cs:
            _bycat.setdefault(_c["category"], []).append(_c)
        _cat_stat = "、".join(f'{_cat} {len(_bycat[_cat])} 篇' for _cat in sorted(_bycat))
        L.append("## 决策显影库（实践案例）")
        L.append(f'共 {len(_cs)} 篇判例（{_cat_stat}），把治水学工具用于真实的历史、商业与治理决策；每篇标注所用治水学接口与杠杆落点。')
        L.append("")
        L.append(f'- 案例机器可读索引（JSON，全部案例的结构化字段）：{base}cases-index.json')
        L.append(f'- 案例总览（人读，可搜索/筛选）：{base}cases.html')
        L.append(f'- 逐篇页面：{base}cases/<编号>.html（例：{base}cases/B-0009.html）')
        if len(_cs) <= 30:
            L.append("")
            for _cat in sorted(_bycat):
                L.append(f'### {_cat}（{len(_bycat[_cat])}）')
                for _c in _bycat[_cat]:
                    L.append(f'- {_c["num"]}｜{_c["title"]}（{_c["scene"]}）｜接口：{_c["interface"]}｜杠杆：{_c["lever"]}')
                    L.append(f'  {case_url(base, _c)}')
        L.append("")
    L.append("## 引用规范（如何引用治水学）")
    L.append("引用治水学分四类，各有唯一口径；引用时**务必带上版本号 / 编号 / 锚点**，以保证精度。")
    L.append(f'- **论文**：按 Zenodo DOI 版本化引用（每篇一个 DOI）。母本 DOI：{doi_url(d["site"]["master_doi"])}')
    L.append(f'- **术语母表（整表）**：{_author}．{_g_title}{_g_ver}．{_g_date}．{base}terms.json'
             + (f'（定义锚点：{g["definition_anchor"]}；英译锚点：{g["translation_anchor"]}）' if g.get("definition_anchor") else ''))
    L.append(f'- **单条术语**：在术语母表版次后附锚点 —— 例：{_author}．「疏浚」．{_g_title}{_g_ver}（{_g_date}）．{base}glossary.html#dredging')
    L.append(f'- **判例**：带判例编号 + 逐篇页 —— 例：{_author}．决策显影库判例 B-0009「隔岸观火」．{base}cases/B-0009.html')
    _cs0 = load_cases()
    if _cs0:
        L.append(f'- **判例库（整库）**：{_author}．决策显影库（治水学实践判例库）．2026．{base}cases.html')
    _ph = d.get("phases", {})
    if _ph:
        L.append(f'- **治水历（定位刻度）**：{_author}．{_ph.get("title", "治水历")}'
                 f'{_ph.get("version_label", "v1.0")}．{_ph.get("date", "")}．{base}phases.json')
    L.append(f'- 机器可读引用条目（BibTeX）：{base}citations.bib')
    L.append(f'- 单条术语的规范引用串已内置于 terms.json 的 `citedAs` 字段与 `glossary.citedAs`。')
    L.append("")
    L.append("## 治水历（定位刻度：怎么给一个局面定位）")
    _p = d.get("phases", {})
    if _p:
        L.append(_p.get("idea", ""))
        L.append("")
        _cells = _p.get("cells", [])
        L.append(f'共 {len(_cells)} 格、{len(_p.get("lines", []))} 条刻度线。{_p.get("usage", "")}。')
        L.append("**只给坐标，不给答案**；案例按接口自动挂载，刻度本身不随案例增减。")
        L.append("")
        for _ln in _p.get("lines", []):
            L.append(f'### {_ln["name"]}（{_ln.get("note", "")}）')
            for _c in [x for x in _cells if x["line"] == _ln["id"]]:
                L.append(f'- **{_c["folk"]}**（{_c["term"]}）：物候——{_c["phenomena"]}；'
                         f'宜——{_c["good"]}；忌——{_c["avoid"]}')
            L.append("")
        L.append("禁忌（贯穿全历）：")
        for _t in _p.get("taboos", []):
            L.append(f'- {_t}')
        L.append("")
        L.append(f'- 机器可读（含每格自动挂载的判例）：{base}phases.json')
        L.append("")
    L.append("## 核心术语表与概念本体")
    L.append("- 每个术语条目附「相关案例」链接：可沿术语表直达案例（概念↔案例双向）。")
    L.append(f"- **术语本体（JSON，机器可直接取用/调用）**：{base}terms.json —— 含中英名、层级、级别、上位/下位、归属/成员、相关判例、可引用锚点与出处 DOI")
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

    _byterm = cases_by_term(d)

    def node(t, depth):
        pad = "&nbsp;" * (depth * 5)
        _n = len(_byterm.get(t["name"], []))
        _mark = f' <span class="lv">◆{_n}案例</span>' if _n else ''
        s = f'<div class="node">{pad}<a class="tlink" href="{base}glossary.html#{t["anchor"]}">{t["name"]}</a> <span class="term-en">{t["en"]}</span> <span class="lv">{t.get("level","")}·{t.get("tier","")}</span>{_mark}</div>'
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
    base = d["site"]["base_url"]
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
    # —— 术语母表（人读母表；机器镜像 = terms.json）——
    g = d.get("glossary", {})
    if g:
        L.append("")
        L.append(f'@{g.get("bib_type", "misc")}{{{g.get("citation_key", "dstterms")},')
        L.append(f'  title={{{g.get("title", "治水学概念层级表（术语母表）")}}},')
        L.append('  author={宁凯峰},')
        L.append(f'  year={{{(g.get("date") or "2026")[:4]}}},')
        L.append(f'  version={{{g.get("version_label", "v1.0")}}},')
        L.append(f'  note={{共 98 条治水学核心术语的层×级双维定位与上位/归属关系；'
                 f'定义锚点：{g.get("definition_anchor", "")}；'
                 f'英译锚点：{g.get("translation_anchor", "")}。'
                 f'机器可读镜像：{base}terms.json}},')
        L.append(f'  url={{{base}glossary.html}},')
        L.append(f'  urldate={{{g.get("date", "")}}},')
        L.append('  language={chinese}')
        L.append("}")
    # —— 决策显影库（实践判例库）——
    _cs = load_cases()
    if _cs:
        L.append("")
        L.append('@misc{ning2026dstcases,')
        L.append('  title={决策显影库（治水学实践判例库）},')
        L.append('  author={宁凯峰},')
        L.append('  year={2026},')
        L.append(f'  note={{共 {len(_cs)} 篇实践判例，每篇标注治水学接口与杠杆落点；'
                 f'机器可读索引：{base}cases-index.json}},')
        L.append(f'  url={{{base}cases.html}},')
        L.append('  language={chinese}')
        L.append("}")
    return "\n".join(L) + "\n"


# ---------------------------- sitemap.xml ----------------------------
def render_sitemap(d):
    base = d["site"]["base_url"]
    _cs = load_cases()
    dates = [w["date"] for w in d["works"] if w.get("date")] + [_c["date"] for _c in _cs if _c.get("date")]
    lastmod = max(dates) if dates else "2026-01-01"
    pages = [
        (base, "1.0", "weekly"),
        (base + "glossary.html", "0.8", "monthly"),
        (base + "glossary.md", "0.6", "monthly"),
        (base + "graph.html", "0.7", "monthly"),
        (base + "cases.html", "0.7", "weekly"),
        (base + "terms.json", "0.6", "monthly"),
        (base + "phases.json", "0.7", "monthly"),
    ]
    for _c in _cs:
        pages.append((case_url(base, _c), "0.6", "monthly"))
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
        "cases.html": render_cases_index(d),
        "cases-index.json": render_cases_json(d),
        "terms.json": render_terms_json(d),
        "phases.json": render_phases_json(d),
    }
    for name, content in outputs.items():
        with open(os.path.join(DIST, name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK dist/{name}  ({len(content)} bytes)")
    _cases = load_cases()
    if _cases:
        os.makedirs(os.path.join(DIST, "cases"), exist_ok=True)
        for _c in _cases:
            content = render_case_page(_c, d)
            with open(os.path.join(DIST, "cases", _c["id"] + ".html"), "w", encoding="utf-8") as f:
                f.write(content)
            print(f'  OK cases/{_c["id"]}.html  ({len(content)} bytes)')
    print(f"\n生成完成：{len(d['works'])} 篇作品、{len(d['terms'])} 个术语、{len(_cases)} 篇判例 -> dist/")


if __name__ == "__main__":
    main()
