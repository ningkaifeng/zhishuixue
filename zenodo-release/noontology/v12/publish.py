# -*- coding: utf-8 -*-
"""
《不做本体论》v1.2：newversion 发布。

v1.2 为内容扩充版（v1.1 只是表述修正）：
新增与 Churchman／Ulrich 边界批判（CSH）的比较、与批判实在论的区分、
「不做本体论」与「存续优先是工作假设」两句合一（含工作假设表）、
触发条件由三条扩为四条、补写失效边界与可证伪条件。
概念 DOI 24436102 不变，版本 DOI 更新。
"""
import json
import os
import sys
import time
from urllib.parse import quote

import requests

PREV = "24436465"           # v1.1 的 record id
API = "https://zenodo.org/api/deposit/depositions"
TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOKEN:
    sys.exit("缺少 ZENODO_TOKEN")

H_AUTH = {"Authorization": "Bearer " + TOKEN}
H_JSON = {**H_AUTH, "Content-Type": "application/json"}
BIN = {**H_AUTH, "Content-Type": "application/octet-stream"}

HERE = os.path.dirname(os.path.abspath(__file__))

VERSION = "1.2"
TITLE = ("不做本体论：治水学为什么不占「这一格」（Not Doing Ontology: "
         "Why Dynamic Sustenance Theory Does Not Enter the Ontological Tier）")

FILES = [
    "DST-No-Ontology-v1.2.pdf",
    "DST-No-Ontology-v1.2.docx",
]

NOTE = """**读法声明：「不做本体论」是一个动作，不是一句断言。** 它说的是治水学**选择不做**这件事，而不是「治水学没有本体论」；把后者当作结论，就等于又坐回了本体论的位置。「没有」的主语是世界（断言世界缺一层，属本体论断言，自败）；「不做／不占」的主语是治水学（描述未做未占，不需要本体论支撑，成立）。本文第二节与第九节专门处理这个区别。

**v1.2 新增（2026-11-23，内容扩充版；v1.1 为表述修正版）**：
一、新增第五节「与 Churchman、Ulrich：另一个最近邻」——在方法上最近的是边界批判（boundary critique）与批判系统启发法（CSH，Ulrich 1983）。起手相同（边界先于实质），差异两处：其一，Ulrich 把「批判」留在 boundary critique 里，治水学只留 boundary；其二更根本，CSH 的边界由分析者提出、利益相关者审议，治水学的边界由承压者确认、分析者单方无权定。总结一句：不是「中国的 CSH」，是克减了范围的 CSH——一个克减分支。同节另辨与 Bhaskar 批判实在论之别（后者对「机制的分层实在」作本体论主张，治水学不作，其「结构」是切口不是世界的一层）。
二、新增 §0.7「承压者也是被指认的位置，不是实体」。
三、新增第七节「两句要连起来说，兼论工作假设」——「不做本体论」与「存续优先是工作假设」是同一个动作的两面：不声称「世界是什么」，也不声称「存续是最高价值或第一实在」，只选它作起点；合起来即把「断言」换成「选择」。附工作假设表，逐条明示克减之内的经验约束（在所述条件下均可修订）——不明示，它们就会被别人还原成本体论。
四、阅读触发条件由三条扩为四条；第十节补写失效边界与可证伪条件。

"""

BODY = """【核心论证】通常所谓「本体论—认识论—方法论」三段式，实为四格：第一格是隐藏的原问题「世界是什么」。治水学的原问题是「系统如何在流变中存续」；原问题一变，第一格随之更换——被「划边界」这个动作占据，而不是被「边界」这个对象占据。这一区分是关键：对象需要本体论（它是什么、是否真的存在），动作不需要（有人划、划得成就成立）。而「划边界」由承压者确认，是程序而非实体，因而堵住了「那么边界是什么」的反噬。

【与他者的区分】本文区分治水学与三类最近邻：过程哲学与关系本体论（仍在问「本质」，只是把答案从实体换成关系或过程）；Luhmann 的系统／环境区分（共享装置，差别在边界确认权的归属——系统自产 vs 承压者确认）；Churchman／Ulrich 的边界批判与 CSH（起手相同，差别在「批判」二字与边界由谁定）。

【结论】治水学不生产本体论主张，它以边界为切口。这是方法论克减（methodological abstention），其代价是放弃普遍性，换取可判定性。三层表述面向三类读者，并给出四条阅读触发条件与失效边界。

【English】This paper argues why Dynamic Sustenance Theory (DST) does not enter the ontological tier, and why this abstention is not a theoretical void but a structural necessity derived from its founding question. What is usually called the triad "ontology–epistemology–methodology" is in fact a quartet: its first cell is a hidden founding question, "what is the world?" DST's founding question is "how does a system sustain itself in flux?" When the founding question changes, the first cell changes with it — it is occupied by the act of drawing a boundary, not by the object "boundary." An object requires ontology (what is it? does it really exist?), whereas an act does not (if someone draws it and it can be drawn, the act holds). Since boundary-drawing is confirmed by the burden-bearing party, it is a procedure rather than an entity, and thus forecloses the rejoinder "then what is a boundary?" v1.2 adds a fifth section comparing DST with Churchman and Ulrich's boundary critique / Critical Systems Heuristics (the nearest neighbour in method, not in system theory), and with Bhaskar's critical realism; it also joins "not doing ontology" with "sustenance-first is a working hypothesis" as two faces of one act — replacing assertion with choice — and tabulates the working hypotheses that must be made explicit. Conclusion: DST produces no ontological claims; it uses the boundary as a cut. Bilingual edition: English text first, Chinese text follows."""

DESC = NOTE + BODY

KEYWORDS = [
    "不做本体论", "方法论克减", "边界批判", "边界", "存续域", "问题域", "工作假设",
    "no-ontology", "methodological abstention", "boundary critique", "CSH",
    "Churchman", "Ulrich", "Luhmann", "Dynamic Sustenance Theory", "治水学",
]

RELATED = [
    {"relation": "references", "identifier": "10.5281/zenodo.23981177",
     "resource_type": "publication-preprint"},
    {"relation": "references", "identifier": "10.5281/zenodo.23056450",
     "resource_type": "publication-preprint"},
    {"relation": "references", "identifier": "10.5281/zenodo.20372186",
     "resource_type": "publication-preprint"},
]


def call(method, url, **kw):
    for i in range(5):
        try:
            r = requests.request(method, url, timeout=120, **kw)
            if r.status_code < 500:
                return r
            print("   5xx 重试", r.status_code)
        except Exception as e:
            print("   网络异常:", str(e)[:80])
        time.sleep(5)
    raise SystemExit("请求失败 " + url)


print("① 查重：上一个记录的版本…")
r = call("GET", f"{API}/{PREV}", headers=H_AUTH)
if r.status_code != 200:
    print(r.status_code, r.text[:300]); sys.exit(2)
prev = r.json()
print("   v1.1 record:", prev.get("id"), "| DOI:", prev.get("doi"),
      "| version:", prev["metadata"].get("version"))

if prev["metadata"].get("version") == VERSION:
    print("   ⚠ 已为 v" + VERSION + "，跳过")
    print("   DOI:", prev.get("doi"), "| concept:", prev.get("conceptdoi"))
    sys.exit(0)

print("② 新建版本（newversion）…")
r = call("POST", f"{API}/{PREV}/actions/newversion", headers=H_JSON, data="{}")
if r.status_code not in (200, 201, 202):
    print(r.status_code, r.text[:300]); sys.exit(2)
did = r.json()["id"]
print("   新 draft id:", did)
r = call("GET", f"{API}/{did}", headers=H_AUTH)
draft = r.json()
bucket = draft["links"]["bucket"]
old = draft.get("files") or []
print("   继承旧文件:", len(old), "个")

print("③ 删除继承的旧文件…")
for f in old:
    rr = call("DELETE", f"{API}/{did}/files/{f['id']}", headers=H_AUTH)
    print("   删", f.get("filename"), rr.status_code)

print("④ bucket PUT 上传 v1.2…")
for name in FILES:
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        sys.exit("缺失文件: " + name)
    with open(path, "rb") as fh:
        content = fh.read()
    r = call("PUT", f"{bucket}/{quote(name)}", headers=BIN, data=content)
    print(f"   {name} → {r.status_code} ({len(content)} B)")
    if r.status_code >= 400:
        print(r.text[:400]); sys.exit(2)

print("⑤ 更新元数据…")
META = {
    "title": TITLE,
    "description": DESC,
    "version": VERSION,
    "publication_date": "2026-11-23",
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
r = call("PUT", f"{API}/{did}", data=json.dumps({"metadata": META}, ensure_ascii=False), headers=H_JSON)
if r.status_code >= 400:
    print(r.status_code, r.text[:600]); sys.exit(2)
print("   元数据 OK")

print("⑥ 发布…")
r = call("POST", f"{API}/{did}/actions/publish", headers=H_JSON, data="{}")
if r.status_code not in (200, 202):
    print(r.status_code, r.text[:400]); sys.exit(2)
rec = r.json()
print("✅ 发布成功")
print("   version DOI:", rec.get("doi"))
print("   concept DOI:", rec.get("conceptdoi"), "（不变）")
print("   record id:", rec.get("id"))
print("   title:", rec["metadata"].get("title"))
print("   version:", rec["metadata"].get("version"))
print("   文件数:", len(rec.get("files") or []))
for f in rec.get("files") or []:
    print("      -", f.get("filename"), f.get("filesize"), "B")
