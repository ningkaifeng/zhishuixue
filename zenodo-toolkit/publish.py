#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布《通用结构语法 · 工具包 v1.0》到 Zenodo（新建独立 record）。

v2：复用已有 draft；publish 走多端点回落（legacy → InvenioRDM 新接口）。
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
            return requests.request(method, url, timeout=180, **kw)
        except Exception as e:
            last = e
            print(f"   retry {i+1}/4: {e}")
            time.sleep(4)
    raise SystemExit(f"network failed: {last}")


def find_paper():
    alt = os.path.join(HERE, "paper_doi.txt")
    if os.path.exists(alt):
        d = open(alt).read().strip()
        if d:
            print("   从 paper_doi.txt 读取:", d)
            return d, "(from file)"
    for params in [{"q": 'title:"General Structural Grammar"', "size": 10},
                   {"q": "General Structural Grammar", "size": 20}]:
        r = call("GET", "https://zenodo.org/api/records", params=params)
        if r.status_code != 200:
            continue
        try:
            hits = r.json().get("hits", {}).get("hits", [])
        except Exception:
            continue
        for h in hits:
            md = h.get("metadata", {})
            t = md.get("title", "") or ""
            if "Structural Grammar" in t and "Governance of Complex Systems" in t:
                return (h.get("conceptdoi") or md.get("conceptdoi") or h.get("doi")), t
    return None, None


print("① 查找论文 record…")
paper_doi, paper_title = find_paper()
if not paper_doi:
    print("✗ 未找到论文 record，停止（避免发出无关联的 record）")
    sys.exit(1)
print("   论文 DOI:", paper_doi)

print("② 查找/新建 draft…")
did, bucket = None, None
r = call("GET", API, params={"size": 50, "sort": "mostrecent"})
if r.status_code == 200:
    data = r.json()
    items = data.get("hits", {}).get("hits", []) if isinstance(data, dict) else data
    for it in items or []:
        if not isinstance(it, dict):
            continue
        t = (it.get("title") or it.get("metadata", {}).get("title") or "")
        state = it.get("state") or it.get("status") or ""
        if t.strip() == TITLE and state not in ("done", "published"):
            did = it.get("id")
            bucket = (it.get("links") or {}).get("bucket")
            print("   复用已存在的 draft:", did, "state=", state)
            break
if not did:
    r = call("POST", API, data=json.dumps({}), headers=H_JSON)
    if r.status_code >= 400:
        print("   ✗ 建 draft 失败", r.status_code, r.text[:400]); sys.exit(2)
    d = r.json()
    did = d["id"]; bucket = d["links"]["bucket"]
    print("   新建 draft:", did)
else:
    if not bucket:
        r2 = call("GET", f"{API}/{did}", headers=H_AUTH)
        bucket = r2.json()["links"]["bucket"]

print("③ 上传 zip…")
path = os.path.join(HERE, ZIP)
size = os.path.getsize(path)
# 先删同名旧文件（避免 409）
r = call("GET", f"{API}/{did}/files", headers=H_AUTH)
if r.status_code == 200:
    fl = r.json()
    files = fl if isinstance(fl, list) else fl.get("entries", [])
    for f in files or []:
        fid = f.get("id") or f.get("key")
        if fid:
            call("DELETE", f"{API}/{did}/files/{fid}", headers=H_AUTH)
            print("   删除旧文件", fid)
with open(path, "rb") as fh:
    content = fh.read()
r = call("PUT", f"{bucket}/{quote(ZIP)}", data=content,
         headers={**H_AUTH, "Content-Type": "application/octet-stream"})
print(f"   {ZIP} {size/1048576:.2f} MB -> HTTP {r.status_code}")
if r.status_code not in (200, 201):
    print("   ✗", r.text[:400]); sys.exit(2)

print("④ 写元数据…")
meta = {"metadata": {
    "title": TITLE,
    "upload_type": "other",
    "publication_date": PUB_DATE,
    "description": DESC,
    "creators": [{"name": "Ning, Kaifeng",
                  "affiliation": "Independent Researcher",
                  "orcid": "0009-0001-4414-6058"}],
    "keywords": KEYWORDS,
    "license": "cc-by-4.0",
    "access_right": "open",
    "language": "eng",
    "version": "1.0",
    "related_identifiers": [{"relation": "isSupplementTo",
                             "identifier": paper_doi,
                             "resource_type": "publication"}],
}}
r = call("PUT", f"{API}/{did}", data=json.dumps(meta), headers=H_JSON)
print("   元数据 HTTP", r.status_code)
if r.status_code >= 400:
    print("   ✗", r.text[:600]); sys.exit(2)

print("⑤ 发布…")
tries = [
    ("POST", f"{API}/{did}/actions/publish", {}),
    ("POST", f"https://zenodo.org/api/records/{did}/draft/publish", {}),
    ("POST", f"https://zenodo.org/api/records/{did}/draft/actions/publish", {}),
]
ok = None
for m, u, kw in tries:
    r = call(m, u, headers=H_JSON, data=json.dumps(kw))
    print(f"   {u.split('/api/')[-1]:45} -> {r.status_code}")
    if r.status_code in (200, 202):
        ok = r.json(); break

if ok:
    print("✅ 发布成功")
    print("   version DOI :", ok.get("doi"))
    print("   concept DOI :", ok.get("conceptdoi"))
    print("   record id   :", ok.get("id"))
    print("   html        :", (ok.get("links") or {}).get("record_html") or ok.get("links", {}).get("self_html"))
    print("   isSupplementTo ->", paper_doi)
else:
    print("⚠️  自动发布被拒（token 缺 deposit:actions 权限）。")
    print("   draft 已完整：文件 + 元数据都已就位，只差点一下发布。")
    print(f"   编辑/发布链接： https://zenodo.org/deposit/{did}")
    print("   或更新 ZENODO_TOKEN（需勾选 deposit:write + deposit:actions）后重跑。")
