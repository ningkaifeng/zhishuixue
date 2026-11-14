#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zenodo 外链修复（一次性任务）
  1) related_identifiers 里指向旧站 ningkaifeng.github.io 的 → 改为 zhishuixue.com
  2) description 里没有官网链接的 → 末尾追加一行官网链接

安全设计：
  - 默认 DRY RUN，只在日志里打印计划，不写任何东西
  - 同目录存在 .apply 文件时才真正执行
  - 只传 Zenodo 可写字段白名单（剔除 dates，否则报 Invalid date）
"""
import os, sys, json, time
import requests

TOK = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOK:
    print("!! 缺少 ZENODO_TOKEN"); sys.exit(1)

H = {"Authorization": f"Bearer {TOK}"}
BASE = "https://zenodo.org/api/deposit/depositions"
HERE = os.path.dirname(os.path.abspath(__file__))
APPLY = os.path.exists(os.path.join(HERE, ".apply"))
SITE = "https://zhishuixue.com/"
OLD_HOST = "ningkaifeng.github.io"

TARGETS = [
    (22088571, "论纲第一篇"),
    (22783960, "论纲第二篇"),
    (22785125, "论纲第三篇"),
    (20372186, "治水学V15.0 母本"),
    (20278692, "治水学V15.0 方法论补全版"),
    (22225452, "治水学V15.0 元辩护版"),
    (23766352, "思想显影库v2.0 概念DOI"),
    (24124184, "思想显影库v2.0"),
    (24099834, "思想显影库v2.0"),
    (24099286, "思想显影库v2.0"),
    (23981176, "Existence and Sustenance"),
    (23981177, "Existence and Sustenance"),
]

WRITABLE = ["title", "doi", "publication_date", "description", "access_right",
            "access_conditions", "creators", "keywords", "notes", "language",
            "license", "upload_type", "imprint_publisher", "related_identifiers",
            "version", "subjects", "locations"]


def get(did):
    for i in range(3):
        try:
            r = requests.get(f"{BASE}/{did}", headers=H, timeout=60)
            if r.status_code == 200:
                return r.json()
            print(f"  !! GET {did} HTTP {r.status_code} {r.text[:150]}")
            return None
        except Exception as e:
            print("  retry", str(e)[:60]); time.sleep(4)
    return None


print(f"### MODE = {'APPLY（会写入）' if APPLY else 'DRY RUN（只打印）'}")
ok = fail = skip = 0

for did, label in TARGETS:
    d = get(did)
    if not d:
        fail += 1
        continue
    md = d.get("metadata", {})
    print("=" * 66)
    print(f"{did} | {label} | {(md.get('title') or '')[:38]}")
    print(f"   state={d.get('state')} submitted={d.get('submitted')} version={md.get('version')}")

    # ---- 1. related_identifiers 去掉旧站 ----
    rels = md.get("related_identifiers") or []
    new_rels, rel_changed = [], False
    for it in rels:
        ident = it.get("identifier", "") or ""
        if OLD_HOST in ident:
            fixed = ident.replace("https://" + OLD_HOST + "/", SITE).replace(OLD_HOST, "zhishuixue.com")
            print(f"   [related] {ident}  ->  {fixed}")
            new_rels.append(dict(it, identifier=fixed))
            rel_changed = True
        else:
            new_rels.append(it)

    # ---- 2. description 缺官网链接则追加 ----
    desc = md.get("description") or ""
    desc_changed = False
    if "zhishuixue.com" not in desc:
        add = f'<p><strong>Official site / 官方主页:</strong> <a href="{SITE}">zhishuixue.com</a></p>'
        print(f"   [desc] 缺官网链接（原长 {len(desc)}）→ 末尾追加一行")
        desc = (desc.rstrip() + "\n" + add) if desc.strip() else add
        desc_changed = True
    else:
        print("   [desc] 已含官网链接，不动")

    if not (rel_changed or desc_changed):
        print("   => 无需改动")
        skip += 1
        continue

    if not APPLY:
        print("   => DRY RUN，未写入")
        continue

    # ---- 3. 执行 edit → PUT → publish ----
    try:
        r1 = requests.post(f"{BASE}/{did}/actions/edit", headers=H, timeout=60)
        print(f"   edit: HTTP {r1.status_code}")
        if r1.status_code not in (200, 201, 202):
            print("   !! edit 失败:", r1.text[:200]); fail += 1; continue

        payload = {k: md[k] for k in WRITABLE if k in md}
        payload["description"] = desc
        if rel_changed or "related_identifiers" in md:
            payload["related_identifiers"] = new_rels

        r2 = requests.put(f"{BASE}/{did}", json={"metadata": payload}, headers=H, timeout=90)
        print(f"   PUT:  HTTP {r2.status_code}")
        if r2.status_code >= 300:
            print("   !! PUT 失败:", r2.text[:400]); fail += 1; continue

        r3 = requests.post(f"{BASE}/{did}/actions/publish", headers=H, timeout=90)
        print(f"   publish: HTTP {r3.status_code}  doi={(r3.json().get('doi') if r3.status_code<300 else '')}")
        if r3.status_code >= 300:
            print("   !! publish 失败:", r3.text[:300]); fail += 1; continue
        ok += 1
    except Exception as e:
        print("   !! 异常", str(e)[:120]); fail += 1
    time.sleep(1)

print("\n" + "=" * 66)
print(f"### 结果：成功 {ok} / 失败 {fail} / 无需改 {skip}（共 {len(TARGETS)} 条）")
