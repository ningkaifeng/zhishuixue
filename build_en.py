#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
治水学 · 英文站生成器（English gateway v2.0）
------------------------------------------------------------
用法：  python3 build_en.py
输入：  papers.yml（论文 / person 唯一数据源）
        en.yml    （英文站文案：首屏 / 六个区块 / 机器层 / 联系）
输出：  en/index.html（单页门牌）
------------------------------------------------------------
v2.0 首屏秩序重做（2026-11-08）：
  · 首屏只留四样：品牌小字 / 一句话定位 H1 / 副标题 / 三个入口 + 身份与证据链
  · H1 不再用理论名词，改用「它做什么」
  · 三层不变量改用术语母表的官方译名（Force-Rule Coordination 等）
  · 新增 Machine-readable layer 深色区块（指向 ontology / schema / HF 五配置）
  · 论文区：首屏精选 3 篇，其余 2 篇折叠为一行清单
  · 与中文站 build.py 完全解耦，互不覆盖
"""
import json
import os
import html

ROOT = os.path.dirname(os.path.abspath(__file__))
EN_DIR = os.path.join(ROOT, "en")


def load_yml(name):
    import yaml
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def esc(s):
    return html.escape(s or "")


def doi_url(doi):
    return "https://doi.org/" + doi


CSS = """
:root{--ink:#15181c;--muted:#5f6b7a;--accent:#1a4d8f;--accent2:#2f7fd1;
--line:#e3e7ec;--bg:#fbfcfd;--dark:#111820;--dark2:#1a232e;}
*{box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
color:var(--ink);background:var(--bg);line-height:1.72;-webkit-font-smoothing:antialiased;}
.wrap{max-width:780px;margin:0 auto;padding:0 22px;}

/* ---------- nav ---------- */
nav{position:sticky;top:0;z-index:50;background:rgba(251,252,253,0.93);backdrop-filter:saturate(180%) blur(8px);
border-bottom:1px solid var(--line);}
nav .inner{max-width:780px;margin:0 auto;padding:11px 22px;display:flex;align-items:center;gap:18px;}
.brand{font-size:0.82em;font-weight:600;letter-spacing:0.02em;color:var(--muted);white-space:nowrap;}
nav .links{margin-left:auto;display:flex;gap:20px;align-items:center;}
nav .links a{font-size:0.85em;color:var(--ink);text-decoration:none;opacity:0.82;}
nav .links a:hover{opacity:1;color:var(--accent);}
.lang{font-size:0.82em;border:1px solid var(--line);border-radius:999px;padding:3px 11px;color:var(--muted);text-decoration:none;}
details.menu{display:none;margin-left:auto;}
details.menu summary{list-style:none;cursor:pointer;font-size:1.3em;color:var(--ink);padding:0 4px;}
details.menu summary::-webkit-details-marker{display:none;}

/* ---------- hero ---------- */
header{max-width:780px;margin:0 auto;padding:78px 22px 40px;}
h1{font-size:2.62em;line-height:1.22;letter-spacing:-0.022em;margin:0 0 22px;font-weight:700;}
.sub{font-size:1.16em;color:#3b4652;margin:0 0 34px;max-width:640px;}
.ctas{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:44px;}
.cta{display:inline-block;padding:11px 22px;border-radius:7px;font-size:0.95em;text-decoration:none;
border:1px solid var(--accent);color:var(--accent);transition:.15s;}
.cta.primary{background:var(--accent);color:#fff;}
.cta:hover{transform:translateY(-1px);box-shadow:0 3px 12px rgba(26,77,143,.18);}
.identity{font-size:0.94em;color:#3b4652;margin:0 0 6px;}
.trust{font-size:0.83em;color:#8a94a2;margin:0;letter-spacing:0.01em;}

/* ---------- sections ---------- */
section{max-width:780px;margin:0 auto;padding:44px 22px;border-top:1px solid var(--line);}
h2{font-size:1.42em;margin:0 0 20px;letter-spacing:-0.01em;}
p{margin:13px 0;}
.lead{color:#39434f;}

/* 对照表 */
.cmp{width:100%;border-collapse:collapse;margin:22px 0 20px;font-size:0.95em;}
.cmp th{text-align:left;padding:9px 12px;font-size:0.86em;font-weight:600;color:var(--muted);
border-bottom:1px solid var(--line);letter-spacing:0.02em;}
.cmp th:first-child{width:48%;}
.cmp td{padding:10px 12px;border-bottom:1px solid #f0f2f5;vertical-align:top;}
.cmp td:first-child{color:#96a0ad;}
.cmp td:last-child{color:var(--ink);font-weight:500;}
.closer{margin-top:22px;padding-left:15px;border-left:3px solid var(--accent2);color:#3b4652;font-size:1.02em;}

/* 不变量 */
.inv{margin:20px 0;}
.inv .item{padding:15px 0;border-bottom:1px solid #eef1f4;}
.inv .item:last-child{border-bottom:none;}
.inv .n{font-weight:650;color:var(--accent);font-size:1.02em;}
.inv .d{color:#48535f;margin-top:4px;}

/* papers */
.pub{margin-bottom:18px;padding:17px 19px;background:#fff;border:1px solid var(--line);border-radius:9px;}
.pub h3{margin:0 0 5px;font-size:1.04em;line-height:1.5;font-weight:600;}
.pub h3 a{color:var(--accent);text-decoration:none;}
.pub h3 a:hover{text-decoration:underline;}
.pub .meta{font-size:0.79em;color:#8a94a2;margin:0 0 7px;}
.pub .blurb{font-size:0.92em;color:#48535f;margin:0;}
.more{margin-top:16px;font-size:0.9em;color:var(--muted);}
.more a{color:var(--accent);text-decoration:none;}

/* machine layer（深色） */
.machine{background:var(--dark);color:#dfe6ee;border-top:none;max-width:none;padding:0;}
.machine .inner{max-width:780px;margin:0 auto;padding:52px 22px;}
.machine h2{color:#fff;}
.machine .note{color:#9fb0c2;font-size:0.95em;max-width:620px;}
.machine .items{margin-top:26px;}
.machine .row{display:block;padding:15px 0;border-bottom:1px solid #232f3c;text-decoration:none;color:inherit;}
.machine .row:last-child{border-bottom:none;}
.machine .row:hover .v{color:#6fb3f2;}
.machine .k{font-size:0.76em;color:#7e8fa2;letter-spacing:0.06em;text-transform:uppercase;}
.machine .v{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:0.92em;color:#8fc7ff;margin-top:3px;word-break:break-all;}
.machine .d{font-size:0.85em;color:#9fb0c2;margin-top:4px;}

/* footprint（一行式） */
.fp{list-style:none;padding:0;margin:18px 0 0;}
.fp li{font-size:0.92em;color:#48535f;padding:7px 0;border-bottom:1px solid #f0f2f5;}
.fp li:last-child{border-bottom:none;}

/* contact */
.contact .mail{font-size:1.12em;}
.contact a{color:var(--accent);text-decoration:none;}
.contact .note{color:var(--muted);font-size:0.92em;}

footer{max-width:780px;margin:0 auto;padding:30px 22px 56px;color:#98a2af;font-size:0.8em;}

@media (max-width:680px){
  header{padding:52px 20px 30px;}
  h1{font-size:1.86em;}
  .sub{font-size:1.05em;}
  nav .links{display:none;}
  details.menu{display:block;}
  details.menu .panel{position:absolute;right:16px;top:46px;background:#fff;border:1px solid var(--line);
    border-radius:10px;box-shadow:0 8px 26px rgba(20,32,48,.12);padding:10px 6px;min-width:190px;}
  details.menu .panel a{display:block;padding:9px 14px;font-size:0.9em;color:var(--ink);text-decoration:none;border-radius:6px;}
  details.menu .panel a:hover{background:#f2f6fa;}
  section{padding:36px 20px;}
  .machine .inner{padding:40px 20px;}
  .cmp td:first-child{width:auto;}
}
"""


def render(en, person, works, base_url):
    s = en["site"]
    nav = en["nav"]
    h = en["hero"]
    cm = en["core_move"]
    inv = en["invariants"]
    pb = en["publications"]
    mc = en["machine"]
    fp = en["footprint"]
    ct = en["contact"]

    L = []
    L.append("<!DOCTYPE html>")
    L.append('<html lang="en">')
    L.append("<head>")
    L.append('<meta charset="utf-8">')
    L.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    L.append(f"<title>{esc(s['title'])}</title>")
    L.append(f'<meta name="description" content="{esc(s["description"])}">')
    L.append(f'<link rel="canonical" href="{base_url}en/">')
    L.append(f'<link rel="alternate" hreflang="zh-CN" href="{base_url}">')

    ld = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "mainEntity": {
            "@type": "Person",
            "name": person.get("alternate_name") or "Ning Kaifeng",
            "alternateName": person.get("name", ""),
            "jobTitle": "Independent Researcher",
            "identifier": {"@type": "PropertyValue", "propertyID": "ORCID",
                           "value": person.get("orcid", "")},
            "email": person.get("email_primary", ""),
            "sameAs": [person.get("orcid_url") or ("https://orcid.org/" + person.get("orcid", "")),
                       person.get("academia", ""), person.get("openalex", ""),
                       person.get("github", ""), person.get("huggingface", "")],
            "knowsAbout": ["Dynamic Sustenance Theory",
                           "Structural grammar for complex systems",
                           "AI governance",
                           "Decision analysis"],
        },
    }
    L.append('<script type="application/ld+json">')
    L.append(json.dumps(ld, ensure_ascii=False))
    L.append("</script>")
    L.append(f"<style>{CSS}</style>")
    L.append("</head>")
    L.append("<body>")

    # ---------- nav ----------
    L.append("<nav><div class='inner'>")
    L.append(f'<span class="brand">{esc(nav["brand"])}</span>')
    L.append('<span class="links">')
    for it in nav["items"]:
        L.append(f'<a href="{esc(it["href"])}">{esc(it["label"])}</a>')
    L.append(f'<a class="lang" href="{base_url}">{esc(nav["lang_switch_label"])}</a>')
    L.append("</span>")
    L.append("<details class='menu'><summary>&#9776;</summary><div class='panel'>")
    for it in nav["items"]:
        L.append(f'<a href="{esc(it["href"])}">{esc(it["label"])}</a>')
    L.append(f'<a href="{base_url}">{esc(nav["lang_switch_label"])}</a>')
    L.append("</div></details>")
    L.append("</div></nav>")

    # ---------- hero ----------
    L.append("<header>")
    L.append(f"<h1>{esc(h['h1'])}</h1>")
    L.append(f'<p class="sub">{esc(h["subhead"])}</p>')
    L.append('<div class="ctas">')
    for c in h["ctas"]:
        cls = "cta primary" if c.get("primary") else "cta"
        L.append(f'<a class="{cls}" href="{esc(c["href"])}">{esc(c["label"])}</a>')
    L.append("</div>")
    L.append(f'<p class="identity">{esc(h["identity"])}</p>')
    L.append(f'<p class="trust">{esc(h["trust"])}</p>')
    L.append("</header>")

    # ---------- core move ----------
    L.append('<section id="core">')
    L.append(f"<h2>{esc(cm['heading'])}</h2>")
    for line in cm["intro"]:
        L.append(f'<p class="lead">{esc(line)}</p>')
    t = cm["table"]
    L.append('<table class="cmp"><thead><tr>'
             f'<th>{esc(t["left_label"])}</th><th>{esc(t["right_label"])}</th>'
             "</tr></thead><tbody>")
    for row in t["rows"]:
        L.append(f"<tr><td>{esc(row[0])}</td><td>{esc(row[1])}</td></tr>")
    L.append("</tbody></table>")
    L.append(f'<p class="closer">{esc(cm["closer"])}</p>')
    L.append("</section>")

    # ---------- invariants ----------
    L.append("<section>")
    L.append(f"<h2>{esc(inv['heading'])}</h2>")
    if inv.get("note"):
        L.append(f'<p style="color:#5f6b7a;font-size:0.94em;">{esc(inv["note"])}</p>')
    L.append('<div class="inv">')
    for it in inv["items"]:
        L.append(f'<div class="item"><div class="n">{esc(it["name"])}</div>'
                 f'<div class="d">{esc(it["desc"])}</div></div>')
    L.append("</div>")
    L.append(f'<p class="closer">{esc(inv["closer"])}</p>')
    L.append("</section>")

    # ---------- papers ----------
    L.append('<section id="papers">')
    L.append(f"<h2>{esc(pb['heading'])}</h2>")
    L.append(f'<p style="color:#5f6b7a;font-size:0.93em;">{esc(pb["note"])}</p>')
    for f in pb["featured"]:
        w = works.get(f["id"])
        if not w:
            continue
        cm_ = w.get("card_meta", "").replace("治水学论纲·英文扩展篇", "DST English Extension Series")
        L.append('<article class="pub">')
        L.append(f'<h3><a href="{doi_url(w["doi"])}">{esc(w["title"])}</a></h3>')
        L.append(f'<div class="meta">{esc(cm_)} · DOI: {esc(w["doi"])}</div>')
        L.append(f'<p class="blurb">{esc(f["blurb"])}</p>')
        L.append("</article>")
    if pb.get("others"):
        L.append('<p class="more">Also in the series: ')
        parts = []
        for oid in pb["others"]:
            w = works.get(oid)
            if w:
                parts.append(f'<a href="{doi_url(w["doi"])}">{esc(w["title"])}</a>')
        L.append(" · ".join(parts))
        L.append("</p>")
    L.append("</section>")

    # ---------- machine layer ----------
    L.append('<section id="machine" class="machine"><div class="inner">')
    L.append(f"<h2>{esc(mc['heading'])}</h2>")
    L.append(f'<p class="note">{esc(mc["note"])}</p>')
    L.append('<div class="items">')
    for it in mc["items"]:
        L.append(f'<a class="row" href="{esc(it["href"])}">'
                 f'<div class="k">{esc(it["label"])}</div>'
                 f'<div class="v">{esc(it["value"])}</div>'
                 f'<div class="d">{esc(it["desc"])}</div></a>')
    L.append("</div></div></section>")

    # ---------- footprint ----------
    L.append("<section>")
    L.append(f"<h2>{esc(fp['heading'])}</h2>")
    L.append('<ul class="fp">')
    for line in fp["lines"]:
        L.append(f"<li>{esc(line)}</li>")
    L.append("</ul>")
    L.append("</section>")

    # ---------- contact ----------
    L.append('<section id="contact" class="contact">')
    L.append(f"<h2>{esc(ct['heading'])}</h2>")
    L.append(f'<p class="mail"><a href="mailto:{esc(ct["email"])}">{esc(ct["email"])}</a></p>')
    L.append(f'<p class="note">{esc(ct["note"])}</p>')
    L.append("</section>")

    L.append(f"<footer>{esc(en['footer']['license'])}</footer>")
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L) + "\n"


def main():
    papers = load_yml("papers.yml")
    en = load_yml("en.yml")

    person = papers.get("person", {})
    base_url = papers.get("site", {}).get("base_url", "https://zhishuixue.com/")
    works = {w["id"]: w for w in papers.get("works", [])}

    ids = [f["id"] for f in en["publications"]["featured"]] + list(en["publications"].get("others") or [])
    missing = [i for i in ids if i not in works or works[i].get("lang") != "en"]
    if missing:
        print("  ! 警告：以下 id 未找到或不是英文作品：", missing)

    html_content = render(en, person, works, base_url)
    os.makedirs(EN_DIR, exist_ok=True)
    out = os.path.join(EN_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  OK en/index.html  ({len(html_content)} chars, {len(ids)} English papers)")


if __name__ == "__main__":
    main()
