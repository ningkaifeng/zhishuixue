#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
治水学 · 英文站生成器（双子站 · 英文门牌）
------------------------------------------------------------
用法：  python3 build_en.py
输入：  papers.yml（论文 / person / 术语 唯一数据源，复用）
        en.yml    （英文站特有文案：About / 定位语 / 页面标题）
输出：  en/index.html（英文站首页，一页门牌）
------------------------------------------------------------
设计原则：
  · 与中文站 build.py 完全解耦，互不调用、互不覆盖。
  · 英文站只做"门牌"：身份定位 + 一句定位语 + 英文论文 + 联系入口。
  · 不含中文站日更的案例库/术语全量——那些留给未来按需加。
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
:root{--ink:#1a1a1a;--muted:#666;--accent:#1a4d8f;--line:#e0e0e0;--bg:#fafafa;}
*{box-sizing:border-box;}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.75;}
.wrap{max-width:820px;margin:0 auto;padding:48px 20px 64px;}
header{border-bottom:2px solid var(--accent);padding-bottom:24px;margin-bottom:8px;}
h1{font-size:2.0em;margin:0 0 4px;letter-spacing:-0.01em;}
.byline{font-size:1.0em;color:#555;margin:6px 0 0;}
.tagline{margin:26px 0 0;padding:18px 20px;background:#eef4fb;border-left:4px solid var(--accent);border-radius:0 8px 8px 0;font-size:1.15em;font-weight:500;}
h2{font-size:1.4em;border-bottom:1px solid var(--line);padding-bottom:6px;margin-top:40px;}
p{margin:12px 0;}
.pub{margin-bottom:16px;padding:16px 18px;background:#fff;border:1px solid var(--line);border-radius:8px;}
.pub h3{margin:0;font-size:1.05em;line-height:1.5;}
.pub h3 a{color:var(--accent);text-decoration:none;}
.pub .meta{font-size:0.82em;color:#888;margin:4px 0 8px;}
.pub .abs{font-size:0.92em;color:#333;}
.contact a{color:var(--accent);text-decoration:none;word-break:break-all;}
.contact .row{margin:6px 0;}
.contact .k{display:inline-block;min-width:110px;color:var(--muted);}
.back{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);}
.back a{color:var(--accent);text-decoration:none;font-weight:500;}
.foot{margin-top:20px;font-size:0.82em;color:#999;text-align:center;}
"""


def render(en, person, pubs, base_url):
    s = en["site"]
    h = en["hero"]
    a = en["about"]
    p = en["publications"]
    c = en["contact"]

    L = []
    L.append("<!DOCTYPE html>")
    L.append('<html lang="en">')
    L.append("<head>")
    L.append("<meta charset=\"utf-8\">")
    L.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
    L.append(f"<title>{esc(s['title'])}</title>")
    L.append(f"<meta name=\"description\" content=\"{esc(s['description'])}\">")
    L.append(f"<link rel=\"canonical\" href=\"{base_url}en/\">")
    # 简单 Person JSON-LD（学术身份，供 Google Scholar / 搜索引擎识别）
    ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": person.get("alternate_name") or h["name"],
        "alternateName": person.get("name"),
        "jobTitle": "Independent Researcher",
        "affiliation": {"@type": "Organization", "name": "Independent Researcher"},
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "ORCID",
            "value": person.get("orcid", ""),
        },
        "email": person.get("email_primary", ""),
        "sameAs": [
            person.get("orcid_url") or ("https://orcid.org/" + person.get("orcid", "")),
            person.get("academia", ""),
            person.get("openalex", ""),
        ],
        "knowsAbout": "Dynamic Sustenance Theory",
    }
    L.append('<script type="application/ld+json">')
    L.append(json.dumps(ld, ensure_ascii=False))
    L.append('</script>')
    L.append(f"<style>{CSS}</style>")
    L.append("</head>")
    L.append("<body>")
    L.append('<div class="wrap">')

    # Header
    L.append("<header>")
    L.append(f"<h1>{esc(h['topic'])}</h1>")
    L.append(f"<p class=\"byline\">{esc(h['name'])} · {esc(h['byline'])}</p>")
    L.append("</header>")
    L.append(f"<p class=\"tagline\">{esc(h['tagline'])}</p>")

    # About
    L.append(f"<h2>{esc(a['heading'])}</h2>")
    L.append(f"<p>{esc(a['lead'])}</p>")
    # 核心命题：冒号前为引子、冒号后加粗（"Its ontological ground is ...: <strong>定义</strong>"）
    _cc = a["core_claim"]
    if ": " in _cc:
        _pre, _post = _cc.split(": ", 1)
        L.append(f"<p>{esc(_pre)}: <strong>{esc(_post)}</strong></p>")
    else:
        L.append(f"<p><strong>{esc(_cc)}</strong></p>")
    L.append(f"<p>{esc(a['core_mechanism'])}</p>")
    L.append(f"<p>{esc(a['gap'])}</p>")

    # Publications
    L.append(f"<h2>{esc(p['heading'])}</h2>")
    L.append(f"<p style=\"color:#666;font-size:0.95em;\">{esc(p['note'])}</p>")
    for w in pubs:
        L.append('<div class="pub">')
        L.append(f"<h3><a href=\"{doi_url(w['doi'])}\">{esc(w['title'])}</a></h3>")
        # card_meta 含中文系列名，英文站替换为英文，避免中文露出
        _cm = w.get("card_meta", "").replace("治水学论纲·英文扩展篇", "DST English Extension Series")
        meta = _cm + " · DOI: " + w.get("doi", "")
        L.append(f"<div class=\"meta\">{esc(meta)}</div>")
        if w.get("abstract"):
            L.append(f"<div class=\"abs\">{esc(w['abstract'])}</div>")
        L.append("</div>")

    # Contact
    L.append(f"<h2>{esc(c['heading'])}</h2>")
    L.append('<div class="contact">')
    L.append(f"<div class=\"row\"><span class=\"k\">{esc(c['orcid_label'])}</span><a href=\"https://orcid.org/{esc(person['orcid'])}\">{esc(person['orcid'])}</a></div>")
    L.append(f"<div class=\"row\"><span class=\"k\">{esc(c['email_label'])}</span><a href=\"mailto:{esc(person['email_primary'])}\">{esc(person['email_primary'])}</a></div>")
    L.append(f"<div class=\"row\"><span class=\"k\">{esc(c['academia_label'])}</span><a href=\"{esc(person['academia'])}\">{esc(person['academia'])}</a></div>")
    L.append(f"<div class=\"row\"><span class=\"k\">{esc(c['openalex_label'])}</span><a href=\"{esc(person['openalex'])}\">{esc(person['openalex'])}</a></div>")
    L.append("</div>")

    # Back
    L.append(f"<div class=\"back\"><a href=\"{base_url}\">&larr; {esc(en['back']['label'])}</a></div>")
    L.append(f"<div class=\"foot\">{esc(en['footer']['license'])}</div>")

    L.append("</div>")
    L.append("</body>")
    L.append("</html>")
    return "\n".join(L)


def main():
    papers = load_yml("papers.yml")
    en = load_yml("en.yml")

    person = papers.get("person", {})
    base_url = papers.get("site", {}).get("base_url", "https://zhishuixue.com/")

    works = {w["id"]: w for w in papers.get("works", [])}
    include_ids = en.get("publications", {}).get("include_ids", [])
    pubs = []
    for wid in include_ids:
        w = works.get(wid)
        if w and w.get("lang") == "en":
            pubs.append(w)

    html_content = render(en, person, pubs, base_url)

    os.makedirs(EN_DIR, exist_ok=True)
    out = os.path.join(EN_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  OK en/index.html  ({len(html_content)} bytes, {len(pubs)} English papers)")


if __name__ == "__main__":
    main()
