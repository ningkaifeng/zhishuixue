#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zenodo 外链精确审计（详细版）
逐条打印：related_identifiers 全量、description 中官网链接的上下文
没有 .apply 文件时只审计；有 .apply 才修复。
"""
import os, sys, json, time, re
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
    (22088571, "论纲第一篇"), (22783960, "论纲第二篇"), (22785125, "论纲第三篇"),
    (20372186, "治水学V15.0 母本"), (20278692, "V15.0 方法论补全版"), (22225452, "V15.0 元辩护版"),
    (24124184, "思想显影库 v3.0"), (24099834, "思想显影库 v2.0"), (24099286, "思想显影库 v2.0"),
    (23981177, "Existence and Sustenance"),
    (23766352, "思想显影库 概念DOI"), (23981176, "Existence 概念DOI"),
]


def get(did):
    for i in range(3):
        try:
            r = requests.get(f"{BASE}/{did}", headers=H, timeout=60)
            if r.status_code == 200:
                return r.json()
            return {"__err__": f"HTTP {r.status_code}"}
        except Exception as e:
            print("  retry", str(e)[:50]); time.sleep(4)
    return {"__err__": "网络异常"}


print(f"### MODE = {'APPLY' if APPLY else 'AUDIT ONLY'}\n")
report = []
for did, label in TARGETS:
    d = get(did)
    print("=" * 70)
    if "__err__" in d:
        print(f"{did} | {label} | {d['__err__']}（概念 DOI 无独立 deposition，属正常）")
        report.append({"id": did, "label": label, "err": d["__err__"]})
        continue
    md = d.get("metadata", {})
    title = (md.get("title") or "")[:40]
    desc = md.get("description") or ""
    rels = md.get("related_identifiers") or []
    # 官网链接在 description 里的位置
    idx = desc.find("zhishuixue.com")
    ctx = ""
    if idx >= 0:
        ctx = re.sub(r"<[^>]+>", " ", desc[max(0, idx - 90): idx + 40])
        ctx = re.sub(r"\s+", " ", ctx).strip()
    old_hits = [r.get("identifier") for r in rels if OLD_HOST in str(r.get("identifier", ""))]
    print(f"{did} | {label} | {title}")
    print(f"   desc 长度 {len(desc)} | 官网出现 {desc.count('zhishuixue.com')} 次"
          + (f" | 上下文: …{ctx}…" if ctx else " | 无官网链接"))
    print(f"   related_identifiers 共 {len(rels)} 条:")
    for it in rels:
        mark = "  <== 旧站！" if OLD_HOST in str(it.get("identifier", "")) else ""
        print(f"      - {it.get('relation')}: {it.get('identifier')}{mark}")
    if not rels:
        print("      （空）")
    report.append({"id": did, "label": label, "desc_len": len(desc),
                   "site_hits": desc.count("zhishuixue.com"),
                   "rels": [f"{r.get('relation')}:{r.get('identifier')}" for r in rels],
                   "old_in_rels": old_hits})

print("\n" + "=" * 70)
print("### 汇总")
print("  desc 无官网:", [f"{r['id']}({r['label']})" for r in report if r.get("site_hits") == 0] or "无")
print("  related 含旧站:", [f"{r['id']}({r['label']})" for r in report if r.get("old_in_rels")] or "无")
print("  概念 DOI 无 deposition:", [f"{r['id']}" for r in report if r.get("err")] or "无")
