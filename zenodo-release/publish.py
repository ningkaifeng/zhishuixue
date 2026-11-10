#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 GitHub Actions 里发布思想显影库 v2.0 到 Zenodo。

流程：复用/新建 draft → 删旧文件 → bucket PUT 上传新文件 → 改元数据 → publish。
文件上传用 bucket 直传（Zenodo 官方推荐，不依赖 multipart /files 端点），
bucket 地址来自 draft 的 links.bucket。
"""
import json, os, sys, time
from urllib.parse import quote
import requests

TOKEN = os.environ["ZENODO_TOKEN"]
API = "https://zenodo.org/api/deposit/depositions"
H_JSON = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}
H_AUTH = {"Authorization": "Bearer " + TOKEN}
V1_REC = "23766353"
CONCEPT = "23766352"
CONCEPT_DOI = "10.5281/zenodo.23766352"
SITE = "https://zhishuixue.com/"
HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    ("Thought-Shadowing-Library-v2.0.pdf", "application/pdf"),
    ("Thought-Shadowing-Library-v2.0.docx",
     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("thoughts-index.json", "application/json"),
    ("README.md", "text/markdown"),
]

DESC = (
    "思想显影库（Thought Shadowing Library）是用「五段框架」对方案、体系与理论做结构提取的连续样本集。"
    "v2.0 收录四篇重写后的显影：尼采（上升存续系统）、孙子兵法（先胜存续系统）、商君书（一孔存续系统）、"
    "道德经（损存续系统）。每篇以五段框架显影其背后的结构判断——边界画在哪、把什么当最大威胁、靠什么推动、"
    "用什么操作、压成一句什么判断，并附视野边界、剩余物与厚度锚点。本库不评价思想高低，只还原不同边界预设下的结构差异；"
    "显影是入口而非出口。v1.0（X-0001 至 X-0018）已作废并重写，原文保留于官网逐篇页作为改写记录。\n\n"
    "The Thought Shadowing Library is a running series of structural shadowings: each entry extracts, via a five-part frame, "
    "the structural judgment behind an intellectual system, program, or theory. v2.0 collects four rewritten shadowings — "
    "Nietzsche, Sunzi, Shang Yang, and Laozi. This library does not rank ideas; it restores the structural differences beneath "
    "different boundary presuppositions. v1.0 has been deprecated and rewritten; the originals remain on the website as a record."
)


def call(method, url, headers=None, **kw):
    h = headers or H_AUTH
    last = None
    for i in range(5):
        try:
            r = requests.request(method, url, headers=h, timeout=180, **kw)
            if r.status_code < 500:
                return r
            last = r
        except Exception as e:
            last = e
        time.sleep(5)
    print("!! 请求失败:", method, url, getattr(last, "status_code", ""), str(last)[:300])
    sys.exit(2)


def dump(r, label):
    print(f"   [{label}] {r.status_code} {r.reason}")
    try:
        print("   body:", r.text[:800])
    except Exception:
        print("   body:", r.content[:800])


print("① 定位/创建 draft…")
r = call("GET", API + "?size=200", headers=H_AUTH)
deps = r.json()
orphan = [d for d in deps
          if str(d.get("conceptrecid")) == CONCEPT and d.get("state") == "unsubmitted"]
if orphan:
    did = orphan[0]["id"]
    print("   复用已有草稿 draft id:", did)
else:
    r = call("POST", f"{API}/{V1_REC}/actions/newversion")
    did = r.json()["id"]
    print("   新建 draft id:", did)

r = call("GET", f"{API}/{did}", headers=H_AUTH)
draft = r.json()
bucket = draft["links"]["bucket"]
old_files = draft.get("files", [])
print("   bucket:", bucket)
print("   草稿内旧文件:", len(old_files), "个")

print("② 删除旧文件…")
for f in old_files:
    call("DELETE", f"{API}/{did}/files/{f['id']}", headers=H_AUTH)
    print("   删", f.get("filename"))

print("③ bucket PUT 上传新文件…")
for name, ctype in FILES:
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        print("   ✗ 缺失", name); sys.exit(2)
    with open(path, "rb") as fh:
        content = fh.read()
    url = f"{bucket}/{quote(name)}"
    r = call("PUT", url, headers={**H_AUTH, "Content-Type": ctype}, data=content)
    if r.status_code >= 400:
        dump(r, f"上传 {name}")
    else:
        print(f"   传 {name} {r.status_code}")

print("④ 更新元数据…")
payload = {
    "metadata": {
        "title": "思想显影库(Thought Shadowing Library v2.0)",
        "description": DESC,
        "version": "2.0",
        "publication_date": "2026-11-10",
        "upload_type": "dataset",
        "language": "zho",
        "license": "cc-by-4.0",
        "creators": [{
            "name": "Ning, Kaifeng",
            "affiliation": "Independent Researcher",
            "orcid": "0009-0001-4414-6058",
        }],
        "keywords": [
            "Dynamic Sustenance Theory", "治水学", "structural shadowing", "思想显影",
            "five-part frame", "存续", "governance syntax",
        ],
        "related_identifiers": [
            {"relation": "isNewVersionOf", "identifier": CONCEPT_DOI, "resource_type": "dataset"},
            {"relation": "references", "identifier": "10.5281/zenodo.20372186", "resource_type": "publication-preprint"},
            {"relation": "references", "identifier": "10.5281/zenodo.23056450", "resource_type": "publication-preprint"},
            {"relation": "references", "identifier": "10.5281/zenodo.23609363", "resource_type": "publication-preprint"},
            {"relation": "references", "identifier": "10.5281/zenodo.23664767", "resource_type": "dataset"},
            {"relation": "isSupplementTo", "identifier": SITE, "resource_type": "other"},
        ],
    }
}
r = call("PUT", f"{API}/{did}", data=json.dumps(payload), headers=H_JSON)
if r.status_code >= 400:
    dump(r, "元数据")
    sys.exit(2)
print("   元数据 OK")

print("⑤ 发布…")
r = call("POST", f"{API}/{did}/actions/publish")
if r.status_code != 202:
    dump(r, "发布")
    sys.exit(2)
rec = r.json()
print("✅ 发布成功")
print("   version DOI:", rec.get("doi"))
print("   concept DOI:", rec.get("conceptdoi"))
print("   record id:", rec.get("id"))
print("   record_html:", rec["links"].get("record_html"))
