#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 SSRN 英文版论文与 Zenodo 记录打通（机器可读关联 + 描述正文提示）。

目标记录：23328738 = A General Structural Grammar（concept DOI）
关联对象：10.2139/ssrn.7601778 = SSRN 英文版（Crossref 注册，与 DataCite 互不相认）

幂等：已含 ssrn 则跳过。metadata-only：不换文件、不升版本。
"""
import os, sys, time
import requests

TOK = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOK:
    print("!! 缺少 ZENODO_TOKEN"); sys.exit(1)

H = {"Authorization": f"Bearer {TOK}"}
BASE = "https://zenodo.org/api/deposit/depositions"
DID = 23328738
SSRN = "10.2139/ssrn.7601778"
TOOLKIT = "10.5281/zenodo.24327221"

WRITABLE = ["title", "doi", "publication_date", "description", "access_right",
            "access_conditions", "creators", "keywords", "notes", "language",
            "license", "upload_type", "imprint_publisher", "related_identifiers",
            "version", "subjects", "locations"]

for i in range(3):
    r = requests.get(f"{BASE}/{DID}", headers=H, timeout=60)
    if r.status_code == 200:
        break
    print("retry GET", r.status_code); time.sleep(5)
else:
    sys.exit("GET 失败")

d = r.json(); md = d.get("metadata", {})
desc = md.get("description") or ""
rels = md.get("related_identifiers") or []
print("记录:", md.get("title"))
print("描述长度:", len(desc), "| related:", len(rels))

if "ssrn.7601778" in desc.lower() or any("ssrn" in str(x.get("identifier", "")).lower() for x in rels):
    print("\n== 已存在 SSRN 关联，无需改动 ==")
    sys.exit(0)

new_desc = desc.rstrip() + (
    "\nSSRN 版 / SSRN version: https://doi.org/" + SSRN +
    "\n配套工具包 / Companion toolkit: https://doi.org/" + TOOLKIT
)
new_rels = rels + [{"relation": "isAlternateIdentifier", "identifier": SSRN}]

r1 = requests.post(f"{BASE}/{DID}/actions/edit", headers=H, timeout=60)
print("edit:", r1.status_code)
if r1.status_code not in (200, 201, 202):
    print(r1.text[:300]); sys.exit(1)

payload = {k: md[k] for k in WRITABLE if k in md}
payload["description"] = new_desc
payload["related_identifiers"] = new_rels
if "version" in md:
    payload["version"] = md["version"]

r2 = requests.put(f"{BASE}/{DID}", json={"metadata": payload}, headers=H, timeout=90)
print("PUT:", r2.status_code)
if r2.status_code >= 300:
    print(r2.text[:500]); sys.exit(1)

r3 = requests.post(f"{BASE}/{DID}/actions/publish", headers=H, timeout=90)
print("publish:", r3.status_code)
if r3.status_code < 300:
    j = r3.json()
    print("✅ 完成 | doi =", j.get("doi"))
    print("related_identifiers:")
    for it in j.get("metadata", {}).get("related_identifiers", []):
        print(f"   {it.get('relation')}: {it.get('identifier')}")
else:
    print(r3.text[:400])
