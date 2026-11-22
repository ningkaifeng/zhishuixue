# -*- coding: utf-8 -*-
"""
《不做本体论》v1.1：newversion 发布。

v1.1 只改表述层级（5 处「对象层断言」→「动作层描述」）+ 第九节新增辨析段，
正文论证未变。故走 newversion：概念 DOI 24436102 不变，版本 DOI 更新。
不原地改 v1.0 标题——那会造成「记录标题写不占、PDF 里写没有」的名实不符。
"""
import json
import os
import sys
import time
from urllib.parse import quote

import requests

PREV = "24436103"           # v1.0 的 record id
API = "https://zenodo.org/api/deposit/depositions"
TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOKEN:
    sys.exit("缺少 ZENODO_TOKEN")

H_AUTH = {"Authorization": "Bearer " + TOKEN}
H_JSON = {**H_AUTH, "Content-Type": "application/json"}
BIN = {**H_AUTH, "Content-Type": "application/octet-stream"}

HERE = os.path.dirname(os.path.abspath(__file__))

VERSION = "1.1"
TITLE = ("不做本体论：治水学为什么不占「这一格」（Not Doing Ontology: "
         "Why Dynamic Sustenance Theory Does Not Enter the Ontological Tier）")

FILES = [
    "DST-No-Ontology-Why-Not-Enter-Ontological-Tier-v1.1.pdf",
    "DST-No-Ontology-Why-Not-Enter-Ontological-Tier-v1.1.docx",
]

NOTE = """**读法声明：「不做本体论」是一个动作，不是一句断言。** 它说的是治水学**选择不做**这件事，而不是「治水学没有本体论」；把后者当作结论，就等于又坐回了本体论的位置。本文 §2／第九节专门处理这个区别，并列出三种不可说的话。

**v1.1 修订（2026-11-22）**：标题与正文共 5 处由「对象层断言」改为「动作层描述」。一是中文标题「治水学为什么没有『这一格』」→「治水学为什么不占『这一格』」；二是英文标题「Has No Ontological Tier」→「Does Not Enter the Ontological Tier」；三是英文摘要「needs no ontological tier」→「does not enter the ontological tier」；四是英文 §0.4「the sustenance domain has none」→「does not occupy one」；五是中英引用格式随标题同步。原因是：「没有」的主语是世界，它断言「世界中缺少这一层」，这是本体论断言，需要本体论支撑，故自败；「不做／不占」的主语是治水学，描述「我们没有做、没有占这个动作」，不需要本体论支撑，故成立。另在第九节开头新增中英各一段辨析。表二「不能写」列的 DST has no ontology／治水学没有本体论 保留不动——那里正是在教这个错。

"""

BODY = """【核心论证】通常所谓「本体论—认识论—方法论」三段式，实为四格：第一格是隐藏的原问题「世界是什么」。治水学的原问题是「系统如何在流变中存续」；原问题一变，第一格随之更换——被「划边界」这个动作占据，而不是被「边界」这个对象占据。这一区分是关键：对象需要本体论（它是什么、是否真的存在），动作不需要（有人划、划得成就成立）。而「划边界」由承压者确认，是程序而非实体，因而堵住了「那么边界是什么」的反噬。

【与他者的区分】本文进一步区分治水学与过程哲学、关系本体论（后者仍在问「本质」，只是把答案从实体换成关系或过程）；并说明其与 Luhmann 的系统／环境区分共享装置，差别在边界确认权的归属——系统自产 vs 承压者确认。

【结论】治水学不生产本体论主张，它以边界为切口。这是方法论克减（methodological abstention），其代价是放弃普遍性，换取可判定性。文末给出三类阅读触发条件与失效条件（§9）。

【English】This paper argues why Dynamic Sustenance Theory (DST) does not enter the ontological tier, and why this abstention is not a theoretical void but a structural necessity derived from its founding question. What is usually called the triad "ontology–epistemology–methodology" is in fact a quartet: its first cell is a hidden founding question, "what is the world?" DST's founding question is "how does a system sustain itself in flux?" When the founding question changes, the first cell changes with it — it is occupied by the act of drawing a boundary, not by the object "boundary." An object requires ontology (what is it? does it really exist?), whereas an act does not (if someone draws it and it can be drawn, the act holds). Since boundary-drawing is confirmed by the burden-bearing party, it is a procedure rather than an entity, and thus forecloses the rejoinder "then what is a boundary?" The paper distinguishes DST from process philosophy and relational ontology (which still ask for essence, merely replacing the answer), and specifies what it shares with Luhmann's system/environment distinction and where it differs (who holds the authority to confirm the boundary). Conclusion: DST produces no ontological claims; it uses the boundary as a cut. Bilingual edition: English text first, Chinese text follows."""

DESC = NOTE + BODY

KEYWORDS = [
    "不做本体论", "方法论克减", "边界", "存续域", "问题域", "问答逻辑",
    "no-ontology", "methodological abstention", "boundary", "sustenance domain",
    "Luhmann", "Dynamic Sustenance Theory", "治水学",
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
print("   v1.0 record:", prev.get("id"), "| DOI:", prev.get("doi"),
      "| version:", prev["metadata"].get("version"))

if prev["metadata"].get("version") == VERSION:
    print("   ⚠ 已为 v" + VERSION + "，跳过")
    print("   DOI:", prev.get("doi"), "| concept:", prev.get("conceptdoi"))
    sys.exit(0)

print("② 新建版本（newversion）…")
r = call("POST", f"{API}/{PREV}/actions/newversion", headers=H_JSON, data="{}")
if r.status_code not in (200, 201, 202):
    print(r.status_code, r.text[:300]); sys.exit(2)
new = r.json()
did = new["id"]
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

print("④ bucket PUT 上传 v1.1…")
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
