#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 GitHub Actions 里发布思想显影库 v4.0 到 Zenodo。

流程：复用/新建 draft → 删旧文件 → bucket PUT 上传新文件 → 改元数据 → publish。
文件上传用 bucket 直传（Zenodo 官方推荐，不依赖 multipart /files 端点），
bucket 地址来自 draft 的 links.bucket。bucket PUT 只接受 application/octet-stream。
"""
import json, os, sys, time
from urllib.parse import quote
import requests

TOKEN = os.environ["ZENODO_TOKEN"]
API = "https://zenodo.org/api/deposit/depositions"
H_JSON = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}
H_AUTH = {"Authorization": "Bearer " + TOKEN}
V1_REC = "24124184"          # v3.0 的 record（新版作为它的 next version）
CONCEPT = "23766352"
CONCEPT_DOI = "10.5281/zenodo.23766352"
SITE = "https://zhishuixue.com/"
HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    ("Thought-Shadowing-Library-v4.0.pdf", "application/pdf"),
    ("Thought-Shadowing-Library-v4.0.docx",
     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("thoughts-index.json", "application/json"),
    ("README.md", "text/markdown"),
]

DESC = (
    "思想显影库（Thought Shadowing Library）是用「五段框架」对方案、体系与理论做结构提取的连续样本集。"
    "v4.0 收录二十篇，覆盖四类归目各至少两篇，为现行最完整版本。\n\n"
    "每篇以五段框架显影其背后的结构判断——边界画在哪、把什么当最大威胁、靠什么推动、用什么操作、压成一句什么判断，"
    "并附视野边界、剩余物与厚度锚点。本库不评价思想高低，只还原不同边界预设下的结构差异；显影是入口而非出口。"
    "需要明确的是：本库是对这些思想家与经典的结构显影，不是对其学说的研究、解释或评价。\n\n"
    "**本版显影对象（中英对照）**：\n"
    "尼采 Nietzsche｜孙子兵法 Sun Tzu, The Art of War｜商君书 Shang Yang, The Book of Lord Shang｜"
    "道德经 Laozi, Daodejing｜论语 Confucius, Analects｜亚里士多德逻辑学 Aristotle, Organon｜"
    "陈来《仁学本体论》Chen Lai｜林毅夫《新结构经济学》Justin Yifu Lin, New Structural Economics｜"
    "马基雅维利《君主论》Machiavelli, The Prince｜黑格尔辩证法 Hegel, Dialectics｜"
    "达尔文进化论 Darwin, Evolution｜牛顿经典力学 Newton, Classical Mechanics｜"
    "爱因斯坦相对论 Einstein, Relativity｜笛卡尔《谈谈方法》Descartes, Discourse on Method｜"
    "易经 I Ching, Book of Changes｜阴阳五行 Yin-Yang and the Five Elements｜"
    "墨子 Mozi, Mohism｜龙树《中论》Nagarjuna, Madhyamaka｜柏拉图《理想国》Plato, Republic｜"
    "康德《纯粹理性批判》Kant, Critique of Pure Reason。\n\n"
    "**四类归目**：系统方案（孙子兵法、商君书、道德经、论语、墨子、理想国、君主论）／"
    "思维工具（亚里士多德逻辑学、笛卡尔谈谈方法）／辩证方法（黑格尔辩证法、易经）／"
    "解释框架（尼采、仁学本体论、新结构经济学、进化论、经典力学、相对论、阴阳五行、龙树中论、纯粹理性批判）。\n\n"
    "v1.0（X-0001 至 X-0018）已作废并重写，原文保留于官网逐篇页作为改写记录。\n\n"
    "The Thought Shadowing Library is a running series of structural shadowings: each entry extracts, via a five-part frame, "
    "the structural judgment behind an intellectual system, program, or theory. v4.0 collects twenty entries spanning "
    "Chinese classics (Sunzi, Shang Yang, Laozi, Analects, I Ching, Yin-Yang and the Five Elements, Mozi), Indian Madhyamaka "
    "(Nagarjuna), ancient Greek thought (Aristotle, Plato), German idealism (Hegel, Kant), modern Western thought "
    "(Nietzsche, Machiavelli, Darwin, Newton, Einstein, Descartes), and contemporary theory (Chen Lai, Justin Yifu Lin). "
    "The same five-part frame is applied across all of them to test its portability across carriers. "
    "This library does not rank ideas; it restores the structural differences beneath different boundary presuppositions. "
    "Each entry is a structural shadowing of the thinker or classic concerned, not a study, interpretation, or evaluation "
    "of their doctrine. v1.0 has been deprecated and rewritten; the originals remain on the website as a record."
)

KEYWORDS = [
    # —— 方法层（中英） ——
    "治水学", "Dynamic Sustenance Theory", "DST",
    "思想显影", "Thought Shadowing Library", "structural shadowing",
    "五段框架", "five-part frame", "存续", "sustenance", "governance syntax",
    # —— 显影对象（人名／典籍，英文便于国际检索） ——
    "Nietzsche", "Sun Tzu", "Art of War", "Shang Yang", "Laozi", "Daodejing",
    "Confucius", "Analects", "Aristotle", "Organon",
    "Chen Lai", "Justin Yifu Lin", "New Structural Economics",
    "Machiavelli", "The Prince", "Hegel", "Dialectics",
    "Darwin", "Evolution", "Newton", "Classical Mechanics",
    "Einstein", "Relativity", "Descartes", "Discourse on Method",
    "I Ching", "Book of Changes", "Yin-Yang", "Five Elements",
    "Mozi", "Mohism", "Nagarjuna", "Madhyamaka",
    "Plato", "Republic", "Kant", "Critique of Pure Reason",
]


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
r = call("GET", API, headers=H_AUTH)
data = r.json()
if isinstance(data, dict):
    hits = data.get("hits")
    deps = hits.get("hits", []) if isinstance(hits, dict) else []
    if not deps:
        print("   !! 列表返回异常:", json.dumps(data, ensure_ascii=False)[:600])
else:
    deps = data
print("   deps 类型:", type(data).__name__, "| 条数:", len(deps) if isinstance(deps, list) else "?")
orphan = [d for d in deps
          if isinstance(d, dict)
          and str(d.get("conceptrecid")) == CONCEPT and d.get("state") == "unsubmitted"]
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
    # Zenodo bucket 只接受 application/octet-stream
    r = call("PUT", url, headers={**H_AUTH, "Content-Type": "application/octet-stream"}, data=content)
    if r.status_code >= 400:
        dump(r, f"上传 {name}")
    else:
        print(f"   传 {name} {r.status_code} ({len(content)} B)")

print("④ 更新元数据…")
payload = {
    "metadata": {
        "title": "思想显影库(Thought Shadowing Library v4.0)",
        "description": DESC,
        "version": "4.0",
        "publication_date": "2026-11-14",
        "upload_type": "dataset",
        "language": "zho",
        "license": "cc-by-4.0",
        "creators": [{
            "name": "Ning, Kaifeng",
            "affiliation": "Independent Researcher",
            "orcid": "0009-0001-4414-6058",
        }],
        "keywords": KEYWORDS,
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
print("   元数据 OK | keywords:", len(KEYWORDS), "个")

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
