# -*- coding: utf-8 -*-
"""
发布《不做本体论：治水学为什么没有「这一格」》到 Zenodo（新建独立记录）。

沙箱 IP 被 Zenodo 限流，故在 GitHub Actions 中执行（ZENODO_TOKEN 存 repo secret）。

流程：POST /depositions 新建 → bucket PUT 传文件 → PUT metadata → POST publish
要点：bucket PUT 只接受 Content-Type: application/octet-stream；
      重复运行前先查是否已发布同名记录，避免产生第二个 DOI。
"""
import json
import os
import sys
import time
from urllib.parse import quote

import requests

API = "https://zenodo.org/api/deposit/depositions"
TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOKEN:
    sys.exit("缺少环境变量 ZENODO_TOKEN")

H_AUTH = {"Authorization": "Bearer " + TOKEN}
H_JSON = {**H_AUTH, "Content-Type": "application/json"}
BIN = {**H_AUTH, "Content-Type": "application/octet-stream"}

HERE = os.path.dirname(os.path.abspath(__file__))

TITLE_MARK = "不做本体论"
TITLE = ("不做本体论：治水学为什么没有「这一格」（Not Doing Ontology: "
         "Why Dynamic Sustenance Theory Has No Ontological Tier）")

FILES = [
    "DST-No-Ontology-Why-No-Ontological-Tier-v1.0.pdf",
    "DST-No-Ontology-Why-No-Ontological-Tier-v1.0.docx",
]

DESC = """本文论证治水学（Dynamic Sustenance Theory, DST）为何不需要本体论这一层，并说明这一「不做」不是理论空缺，而是由原问题派生出的结构必然。中英双语版，英文在前、中文在后，两版内容一致。

【核心论证】通常所谓「本体论—认识论—方法论」三段式，实为四格：第一格是隐藏的原问题「世界是什么」。治水学的原问题是「系统如何在流变中存续」；原问题一变，第一格随之更换——被「划边界」这个动作占据，而不是被「边界」这个对象占据。

这一区分是关键：对象需要本体论（它是什么、是否真的存在），动作不需要（有人划、划得成就成立）。而「划边界」由承压者确认，是程序而非实体，因而堵住了「那么边界是什么」的反噬。

【与他者的区分】本文进一步区分治水学与过程哲学、关系本体论（后者仍在问「本质」，只是把答案从实体换成关系或过程）；并说明其与 Luhmann 的系统／环境区分共享装置，差别在边界确认权的归属——系统自产 vs 承压者确认。

【表述的自我限定】文中专设一节指出：不可以把结论说成「治水学没有本体论」，也不可以把它读成「动态本体论」。「不做本体论」是一个方法论克减（methodological abstention）的表述，不是一个存在论断言；一旦把它当断言，就又回到了本体论的位置上。

【结论】治水学不生产本体论主张，它以边界为切口。这是方法论克减，其代价是放弃普遍性，换取可判定性。文末给出三类阅读触发条件与失效条件（§9 失效条件与可证伪性）。

【English】This paper argues why Dynamic Sustenance Theory (DST) needs no ontological tier, and why this abstention is not a theoretical void but a structural necessity derived from its founding question. What is usually called the triad "ontology–epistemology–methodology" is in fact a quartet: its first cell is a hidden founding question, "what is the world?" DST's founding question is "how does a system sustain itself in flux?" When the founding question changes, the first cell changes with it — it is occupied by the act of drawing a boundary, not by the object "boundary." An object requires ontology (what is it? does it really exist?), whereas an act does not (if someone draws it and it can be drawn, the act holds). Since boundary-drawing is confirmed by the burden-bearing party, it is a procedure rather than an entity, and thus forecloses the rejoinder "then what is a boundary?" The paper distinguishes DST from process philosophy and relational ontology (which still ask for essence, merely replacing the answer), and specifies what it shares with Luhmann's system/environment distinction and where it differs (who holds the authority to confirm the boundary). Conclusion: DST produces no ontological claims; it uses the boundary as a cut. This is methodological abstention, whose cost is universality and whose gain is decidability. Bilingual edition: English text first, Chinese text follows."""

KEYWORDS = [
    "不做本体论", "方法论克减", "边界", "存续域", "问题域", "问答逻辑",
    "no-ontology", "methodological abstention", "boundary", "sustenance domain",
    "Luhmann", "Dynamic Sustenance Theory", "治水学",
]

RELATED = [
    {"relation": "references", "identifier": "10.5281/zenodo.23981177",
     "resource_type": "publication-preprint"},   # 存在与存续：元分界宣言
    {"relation": "references", "identifier": "10.5281/zenodo.23056450",
     "resource_type": "publication-preprint"},   # 存续域认识论
    {"relation": "references", "identifier": "10.5281/zenodo.20372186",
     "resource_type": "publication-preprint"},   # 治水学母本
]

META = {
    "title": TITLE,
    "description": DESC,
    "version": "1.0",
    "publication_date": "2026-11-22",
    "upload_type": "publication",
    "publication_type": "preprint",
    "language": "zho",
    "license": "cc-by-4.0",
    "creators": [{
        "name": "Ning, Kaifeng",
        "affiliation": "Independent Researcher",
        "orcid": "0009-0001-4414-6058",
    }],
    "keywords": KEYWORDS,
    "related_identifiers": RELATED,
}


def call(method, url, **kw):
    for i in range(5):
        try:
            r = requests.request(method, url, timeout=120, **kw)
            if r.status_code < 500:
                return r
            print("   5xx，重试", r.status_code)
        except Exception as e:
            print("   网络异常，重试:", str(e)[:80])
        time.sleep(5)
    raise SystemExit("请求失败: " + url)


print("① 查重：是否已发布同名记录…")
r = call("GET", API, headers=H_AUTH, params={"size": 100, "sort": "mostrecent"})
if r.status_code == 200:
    data = r.json()
    hits = data.get("hits", {}).get("hits") if isinstance(data, dict) else data
    for h in hits or []:
        md = h.get("metadata", {}) or {}
        if TITLE_MARK in (md.get("title") or ""):
            print("   ⚠ 已存在记录，跳过发布")
            print("   DOI:", h.get("doi"))
            rid = h.get("id")
            rv = call("GET", f"{API}/{rid}", headers=H_AUTH)
            if rv.status_code == 200:
                rec = rv.json()
                mdv = rec.get("metadata", {})
                print("   [核验] state:", rec.get("state"), "| submitted:", rec.get("submitted"))
                print("   [核验] title:", mdv.get("title"))
                print("   [核验] pub_date:", mdv.get("publication_date"),
                      "| type:", mdv.get("upload_type"), "/", mdv.get("publication_type"))
                fl = rec.get("files") or []
                print("   [核验] 文件数:", len(fl))
                for f in fl:
                    print("      -", f.get("filename"), f.get("filesize"), "B")
                print("   [核验] related:",
                      [(x.get("relation"), x.get("identifier")) for x in (mdv.get("related_identifiers") or [])])
            sys.exit(0)
    print("   未发现已发布同名记录")
else:
    print("   查重接口返回", r.status_code, "（继续）")

print("② 新建 deposition…")
r = call("POST", API, headers=H_JSON, data=json.dumps({"metadata": META}, ensure_ascii=False))
if r.status_code not in (200, 201):
    print(r.status_code, r.text[:400])
    sys.exit(2)
dep = r.json()
did = dep["id"]
bucket = dep["links"]["bucket"]
print("   draft id:", did)

print("③ bucket PUT 上传文件…")
for name in FILES:
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        sys.exit("缺失文件: " + name)
    with open(path, "rb") as fh:
        content = fh.read()
    r = call("PUT", f"{bucket}/{quote(name)}", headers=BIN, data=content)
    print(f"   {name} → {r.status_code} ({len(content)} B)")
    if r.status_code >= 400:
        print(r.text[:400])
        sys.exit(2)

print("④ 更新元数据…")
r = call("PUT", f"{API}/{did}", data=json.dumps({"metadata": META}, ensure_ascii=False), headers=H_JSON)
if r.status_code >= 400:
    print(r.status_code, r.text[:600])
    sys.exit(2)
print("   元数据 OK")

print("⑤ 发布…")
r = call("POST", f"{API}/{did}/actions/publish", headers=H_JSON, data="{}")
if r.status_code not in (200, 202):
    print(r.status_code, r.text[:400])
    sys.exit(2)
rec = r.json()
print("✅ 发布成功")
print("   version DOI:", rec.get("doi"))
print("   concept DOI:", rec.get("conceptdoi"))
print("   record id:", rec.get("id"))
print("   record_html:", rec.get("links", {}).get("record_html"))
