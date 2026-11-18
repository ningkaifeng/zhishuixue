#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布《通用结构语法 · 工具包 v1.0》到 Zenodo（新建独立 record）。

与 zenodo-release/publish.py 的区别：
  - 那条线是给已有概念 DOI 出新版本（newversion）
  - 这条线是新建一个独立 record，用 isSupplementTo 挂回论文

安全设计：找不到论文 DOI、或标题不匹配，直接退出不发布。
"""
import json, os, sys, time
from urllib.parse import quote
import requests

TOKEN = os.environ["ZENODO_TOKEN"]
API = "https://zenodo.org/api/deposit/depositions"
H_AUTH = {"Authorization": "Bearer " + TOKEN}
H_JSON = {**H_AUTH, "Content-Type": "application/json"}
HERE = os.path.dirname(os.path.abspath(__file__))

ZIP = "Structural-Grammar-Toolkit-v1.0.zip"
ZIP_MIME = "application/zip"
TITLE = ("Structural Grammar Toolkit v1.0: Diagnostic Worksheet, "
         "Prompt Card, and Worked Examples")
PUB_DATE = "2026-11-18"

KEYWORDS = [
    "structural grammar", "complex systems", "governance",
    "diagnostic tool", "toolkit", "AI governance",
    "systems theory", "methodology",
]

DESC = """<p><strong>A companion toolkit to</strong> <em>A General Structural Grammar for the Governance of Complex Systems: A Methodological Framework</em> (Ning 2026).</p>

<p>The paper argues <em>why</em> governance needs a structural grammar. This toolkit shows <em>how</em> to run one. It adds no theoretical claim of its own; everything in it comes from the paper and from the specimen work that followed.</p>

<p><strong>Contents (bilingual, Chinese and English):</strong></p>
<ul>
<li><strong>01 Overview</strong> — a navigation document mapping each section of the paper to the part of the toolkit that operationalises it.</li>
<li><strong>02 Diagnostic Worksheet v2.0</strong> — a fillable form covering the pre-check, the five judgments, the four intervention questions, the self-check, and the four-level validation ladder. Supplied as PDF (for reading) and DOCX (for filling).</li>
<li><strong>03 Prompt Card</strong> — for each judgment: three diagnostic questions and the most common error.</li>
<li><strong>04 Worked Examples</strong> — three completed worksheets on real systems (global AI governance; global plastics governance; AI infrastructure capex), each with annotations explaining why the boxes were filled as they were.</li>
</ul>

<p><strong>One divergence from the paper.</strong> The paper (§3.1) presents a four-state grid; the toolkit uses five states, adding <em>Evasive lock-in</em> (讳锁). This is a granularity difference, not a version conflict: the two-by-two grid is unchanged, one cell has been split into two. The fifth state emerged from practice — Specimen No.03 found a constraint that is formally fully adjustable, but whose use would immediately expose the loss, so that no one moves first. Classified as adjustable, it invites a direct attempt; classified as solidified, it invites waiting for external force. Both prescriptions are wrong. Full note on the last page of the Worksheet.</p>

<p><strong>What it does not provide:</strong> quantitative thresholds, direct answers, normative verdicts, a substitute for the bearer's judgement, or cross-scale uniform thresholds. It judges structure, not right and wrong.</p>

<p><strong>Citation.</strong> Please cite the concept DOI rather than a version DOI, so the reference resolves to the current version.</p>"""


def call(method, url, **kw):
    last = None
    for i in range(4):
        try:
            r = requests.request(method, url, timeout=120, **kw)
            return r
        except Exception as e:
            last = e
            print(f"   retry {i+1}/4: {e}")
            time.sleep(4)
    raise SystemExit(f"network failed: {last}")


def find_paper():
    """在 Zenodo 公开记录里找论文，返回 (concept_doi, title)。找不到返回 (None, None)。"""
    for url, params in [
        ("https://zenodo.org/api/records",
         {"q": 'title:"General Structural Grammar"', "size": 10}),
        ("https://zenodo.org/api/records",
         {"q": "General Structural Grammar", "size": 20}),
    ]:
        r = call("GET", url, params=params)
        if r.status_code != 200:
            print(f"   搜索返回 {r.status_code}")
            continue
        try:
            hits = r.json().get("hits", {}).get("hits", [])
        except Exception:
            continue
        print(f"   命中 {len(hits)} 条")
        for h in hits:
            md = h.get("metadata", {})
            t = md.get("title", "") or ""
            if "Structural Grammar" in t and "Governance of Complex Systems" in t:
                doi = h.get("conceptdoi") or md.get("conceptdoi") or h.get("doi")
                return doi, t
    return None, None


print("① 查找论文 record…")
paper_doi, paper_title = find_paper()
if not paper_doi:
    print("✗ 未找到论文 record。为避免发出无关联的 record，停止。")
    print("  请手动把论文 DOI 写进 zenodo-toolkit/paper_doi.txt 后重试。")
    alt = os.path.join(HERE, "paper_doi.txt")
    if os.path.exists(alt):
        paper_doi = open(alt).read().strip()
        print("  已从 paper_doi.txt 读取:", paper_doi)
    else:
        sys.exit(1)
print("   论文 DOI:", paper_doi)
print("   论文标题:", paper_title)

print("② 新建 deposition…")
r = call("POST", API, data=json.dumps({}), headers=H_JSON)
if r.status_code >= 400:
    print("   ✗", r.status_code, r.text[:500]); sys.exit(2)
d = r.json()
did = d["id"]
bucket = d["links"]["bucket"]
print("   draft id:", did)

print("③ 上传 zip（bucket PUT，octet-stream）…")
path = os.path.join(HERE, ZIP)
if not os.path.exists(path):
    print("   ✗ 找不到", path); sys.exit(2)
size = os.path.getsize(path)
print(f"   {ZIP}  {size/1048576:.2f} MB")
with open(path, "rb") as fh:
    content = fh.read()
r = call("PUT", f"{bucket}/{quote(ZIP)}", data=content,
         headers={**H_AUTH, "Content-Type": "application/octet-stream"})
if r.status_code not in (200, 201):
    print("   ✗", r.status_code, r.text[:500]); sys.exit(2)
print("   上传 OK")

print("④ 写元数据…")
meta = {
    "metadata": {
        "title": TITLE,
        "upload_type": "other",
        "publication_date": PUB_DATE,
        "description": DESC,
        "creators": [{
            "name": "Ning, Kaifeng",
            "affiliation": "Independent Researcher",
            "orcid": "0009-0001-4414-6058",
        }],
        "keywords": KEYWORDS,
        "license": "cc-by-4.0",
        "access_right": "open",
        "language": "eng",
        "version": "1.0",
        "related_identifiers": [{
            "relation": "isSupplementTo",
            "identifier": paper_doi,
            "resource_type": "publication",
        }],
    }
}
r = call("PUT", f"{API}/{did}", data=json.dumps(meta), headers=H_JSON)
if r.status_code >= 400:
    print("   ✗", r.status_code, r.text[:800]); sys.exit(2)
print("   元数据 OK")

print("⑤ 发布…")
r = call("POST", f"{API}/{did}/actions/publish")
if r.status_code != 202:
    print("   ✗", r.status_code, r.text[:500]); sys.exit(2)
rec = r.json()
print("✅ 发布成功")
print("   version DOI :", rec.get("doi"))
print("   concept DOI :", rec.get("conceptdoi"))
print("   record id   :", rec.get("id"))
print("   record_html :", rec.get("links", {}).get("record_html"))
print("   isSupplementTo ->", paper_doi)
