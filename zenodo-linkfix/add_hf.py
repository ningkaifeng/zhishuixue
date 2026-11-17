#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给 Zenodo 思想显影库 v4.0（24211659）加一条指向 Hugging Face 数据集的关联声明。
IsSupplementedBy —— 与决策显影库 v1.1 的写法完全一致。

幂等：已有 HF 关联则跳过。
metadata-only：不换文件、不升版本号（2026-11-13 用 26 条验证过）。
"""
import os, sys, time
import requests

TOK = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOK:
    print("!! 缺少 ZENODO_TOKEN"); sys.exit(1)

H = {"Authorization": f"Bearer {TOK}"}
BASE = "https://zenodo.org/api/deposit/depositions"
DID = 24211659          # 思想显影库 v4.0
HF = "https://huggingface.co/datasets/zhishuixue/dst-decision-disclosure"

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

d = r.json()
md = d.get("metadata", {})
print("记录:", md.get("title"), "| version =", md.get("version"), "| state =", d.get("state"))
rels = md.get("related_identifiers") or []
print(f"现有 related_identifiers {len(rels)} 条：")
for it in rels:
    print(f"   {it.get('relation')}: {it.get('identifier')}")

if any("huggingface.co" in str(it.get("identifier", "")) for it in rels):
    print("\n== 已存在 Hugging Face 关联，无需改动 ==")
    sys.exit(0)

new_item = {"relation": "isSupplementedBy", "identifier": HF}
print(f"\n将追加: {new_item}")

r1 = requests.post(f"{BASE}/{DID}/actions/edit", headers=H, timeout=60)
print("edit:", r1.status_code)
if r1.status_code not in (200, 201, 202):
    print(r1.text[:300]); sys.exit(1)

payload = {k: md[k] for k in WRITABLE if k in md}
payload["related_identifiers"] = rels + [new_item]
# version 必须显式带，否则会被清成 None
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
    print("✅ 完成 | doi =", j.get("doi"), "| version =", j.get("metadata", {}).get("version"))
    print("最终 related_identifiers:")
    for it in j.get("metadata", {}).get("related_identifiers", []):
        print(f"   {it.get('relation')}: {it.get('identifier')}")
else:
    print(r3.text[:400])
