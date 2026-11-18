#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修订两个已发布 Zenodo record 的元数据：
   1) 工具包 24327222：related 加 isPartOf -> https://zhishuixue.com；描述加项目页
   2) 论文   23328738：描述加项目页 + 指向工具包；related 加 isSupplementedBy -> 工具包
不改文件、不产生新版本（edit -> PUT metadata -> publish）。
"""
import json, os, sys, time
import requests

TOKEN = os.environ["ZENODO_TOKEN"]
API = "https://zenodo.org/api/deposit/depositions"
H_AUTH = {"Authorization": "Bearer " + TOKEN}
H_JSON = {**H_AUTH, "Content-Type": "application/json"}

SITE = "https://zhishuixue.com/"
TOOLKIT_DOI = "10.5281/zenodo.24327221"
PAPER_DOI = "10.5281/zenodo.23328738"

TOOLKIT_BLOCK = (
    '<p><strong>Project page:</strong> <a href="https://zhishuixue.com/">zhishuixue.com</a> '
    '— 中文说明与全部相关文献。<br/>'
    '<em>This record is part of the project site above; the methodology paper is its companion record.</em></p>'
)
PAPER_BLOCK = (
    '<p><strong>Project page:</strong> <a href="https://zhishuixue.com/">zhishuixue.com</a> '
    '— 中文版与全部相关文献。<br/>'
    f'<strong>Companion toolkit:</strong> <a href="https://doi.org/{TOOLKIT_DOI}">'
    'Structural Grammar Toolkit v1.0</a>（工作表 · 提示卡 · 填好的样例，中英双语）.</p>'
)

WRITABLE = ["title", "publication_date", "description", "access_right", "creators",
            "keywords", "related_identifiers", "language", "license",
            "upload_type", "imprint_publisher", "version"]


def call(method, url, **kw):
    for i in range(4):
        try:
            return requests.request(method, url, timeout=120, **kw)
        except Exception as e:
            print(f"   retry {i+1}/4: {e}")
            time.sleep(4)
    raise SystemExit("network failed")


def revise(rid, extra_rel, block, tag):
    print("=" * 55)
    print(tag, rid)
    r = call("POST", f"{API}/{rid}/actions/edit", headers=H_AUTH)
    print("  edit ->", r.status_code)
    if r.status_code >= 400:
        print("  ", r.text[:300]); return False

    r = call("GET", f"{API}/{rid}", headers=H_AUTH)
    md = r.json()["metadata"]
    print("  title:", md.get("title", "")[:60])

    # 描述：已含官网则跳过追加
    desc = md.get("description", "") or ""
    if "zhishuixue.com" in desc:
        print("  描述已含官网链接，跳过")
    else:
        desc = desc.rstrip() + "\n\n" + block
        print("  描述追加官网块")

    rel = md.get("related_identifiers") or []
    have = {(x.get("relation"), x.get("identifier")) for x in rel}
    for x in extra_rel:
        if (x["relation"], x["identifier"]) not in have:
            rel.append(x)
            print("  related +", x["relation"], x["identifier"])

    body = {k: md.get(k) for k in WRITABLE if md.get(k) is not None}
    body["description"] = desc
    body["related_identifiers"] = rel

    r = call("PUT", f"{API}/{rid}", data=json.dumps({"metadata": body}), headers=H_JSON)
    print("  PUT ->", r.status_code)
    if r.status_code >= 400:
        print("  ", r.text[:600]); return False

    r = call("POST", f"{API}/{rid}/actions/publish", headers=H_AUTH)
    print("  publish ->", r.status_code)
    if r.status_code not in (200, 202):
        print("  ", r.text[:300]); return False
    print("  ✅", r.json().get("doi"))
    return True


ok1 = revise(
    24327222,
    [{"relation": "isPartOf", "identifier": SITE, "resource_type": "other"}],
    TOOLKIT_BLOCK,
    "工具包",
)
ok2 = revise(
    23328738,
    [{"relation": "isSupplementedBy", "identifier": TOOLKIT_DOI, "resource_type": "other"}],
    PAPER_BLOCK,
    "论文",
)
print("=" * 55)
print("结果:", "工具包 OK" if ok1 else "工具包 失败", "|", "论文 OK" if ok2 else "论文 失败")
sys.exit(0 if (ok1 and ok2) else 2)
