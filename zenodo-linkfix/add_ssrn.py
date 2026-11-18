#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 SSRN 关联从 isAlternateIdentifier 改为 isIdenticalTo（DataCite 标准类型），
看 Zenodo 是否会把它转发到 DataCite。

目标记录：23328739（A General Structural Grammar 的版本记录；
         概念 DOI 23328738 在 depositions API 下 404）

幂等：已是 isIdenticalTo 则跳过。metadata-only：不换文件、不升版本。
"""
import os, sys, time
import requests

TOK = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOK:
    print("!! 缺少 ZENODO_TOKEN"); sys.exit(1)

H = {"Authorization": f"Bearer {TOK}"}
BASE = "https://zenodo.org/api/deposit/depositions"
DID = 23328739
SSRN = "10.2139/ssrn.7601778"

WRITABLE = ["title", "doi", "publication_date", "description", "access_right",
            "access_conditions", "creators", "keywords", "notes", "language",
            "license", "upload_type", "imprint_publisher", "related_identifiers",
            "version", "subjects", "locations"]

for i in range(3):
    r = requests.get(f"{BASE}/{DID}", headers=H, timeout=60)
    if r.status_code == 200:
        break
    print("retry GET", r.status_code, r.text[:120]); time.sleep(5)
else:
    sys.exit("GET 失败")

md = r.json().get("metadata", {})
rels = md.get("related_identifiers") or []
print("现有 related_identifiers:")
for it in rels:
    print(f"   {it.get('relation')}: {it.get('identifier')}")

if any(it.get("relation") == "isIdenticalTo" and "ssrn" in str(it.get("identifier", "")).lower() for it in rels):
    print("\n== 已是 isIdenticalTo，无需改动 ==")
    sys.exit(0)

new_rels, changed = [], False
for it in rels:
    ident = str(it.get("identifier", ""))
    if "ssrn" in ident.lower():
        print(f"\n改造: {it.get('relation')} -> isIdenticalTo （{ident}）")
        new_rels.append({"relation": "isIdenticalTo", "identifier": ident})
        changed = True
    else:
        new_rels.append(it)
if not changed:
    print(f"\n未找到 SSRN 条目，追加 isIdenticalTo: {SSRN}")
    new_rels.append({"relation": "isIdenticalTo", "identifier": SSRN})

r1 = requests.post(f"{BASE}/{DID}/actions/edit", headers=H, timeout=60)
print("edit:", r1.status_code)
if r1.status_code not in (200, 201, 202):
    print(r1.text[:300]); sys.exit(1)

payload = {k: md[k] for k in WRITABLE if k in md}
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
    print("✅ 完成 | doi =", r3.json().get("doi"))
    for it in r3.json().get("metadata", {}).get("related_identifiers", []):
        print(f"   {it.get('relation')}: {it.get('identifier')}")
else:
    print(r3.text[:400])
