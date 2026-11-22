# -*- coding: utf-8 -*-
"""
给《不做本体论》的 Zenodo 记录补一条「读法声明」，放在描述第一句。

Zenodo 允许发布后改元数据：/actions/edit → PUT metadata → /actions/publish。
不产生新版本，DOI 不变。可重复运行（检测到已有声明就跳过）。
"""
import json
import os
import sys
import time

import requests

RID = "24436103"
API = "https://zenodo.org/api/deposit/depositions"
TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOKEN:
    sys.exit("缺少 ZENODO_TOKEN")

H_AUTH = {"Authorization": "Bearer " + TOKEN}
H_JSON = {**H_AUTH, "Content-Type": "application/json"}

NOTE = ("**读法声明：「不做本体论」是一个动作，不是一句断言。** 它说的是治水学**选择不做**这件事，"
        "而不是「治水学没有本体论」；把后者当作结论，就等于又坐回了本体论的位置。"
        "本文 §2 专门处理这个区别，并列出三种不可说的话。\n\n")


def call(method, url, **kw):
    for i in range(5):
        try:
            r = requests.request(method, url, timeout=120, **kw)
            if r.status_code < 500:
                return r
            print("   5xx 重试", r.status_code)
        except Exception as e:
            print("   网络异常:", str(e)[:80])
        time.sleep(5)
    raise SystemExit("请求失败 " + url)


print("① 取当前记录…")
r = call("GET", f"{API}/{RID}", headers=H_AUTH)
if r.status_code != 200:
    print(r.status_code, r.text[:300]); sys.exit(2)
rec = r.json()
md = rec["metadata"]
print("   state:", rec.get("state"), "| title:", md.get("title")[:40])
desc = md.get("description") or ""

if "读法声明" in desc[:400]:
    print("   ⚠ 描述开头已有读法声明，跳过")
    print("   前 120 字:", desc[:120])
    sys.exit(0)

print("② 进入编辑态…")
r = call("POST", f"{API}/{RID}/actions/edit", headers=H_JSON, data="{}")
print("   ", r.status_code)
if r.status_code not in (200, 201, 202):
    print(r.text[:300]); sys.exit(2)

print("③ 重写描述…")
new_meta = {
    "title": md["title"],
    "description": NOTE + desc,
    "creators": md.get("creators"),
    "keywords": md.get("keywords"),
    "related_identifiers": md.get("related_identifiers"),
    "language": md.get("language"),
    "license": md.get("license"),
    "upload_type": md.get("upload_type"),
    "publication_type": md.get("publication_type"),
    "version": md.get("version"),
    "publication_date": md.get("publication_date"),
}
new_meta = {k: v for k, v in new_meta.items() if v not in (None, "", [])}
r = call("PUT", f"{API}/{RID}", data=json.dumps({"metadata": new_meta}, ensure_ascii=False), headers=H_JSON)
print("   ", r.status_code)
if r.status_code >= 400:
    print(r.text[:600]); sys.exit(2)

print("④ 重新发布（不产生新版本）…")
r = call("POST", f"{API}/{RID}/actions/publish", headers=H_JSON, data="{}")
print("   ", r.status_code)
if r.status_code not in (200, 202):
    print(r.text[:400]); sys.exit(2)

print("⑤ 核验…")
r = call("GET", f"{API}/{RID}", headers=H_AUTH)
rec = r.json(); md = rec["metadata"]
print("   state:", rec.get("state"), "| submitted:", rec.get("submitted"))
print("   DOI:", rec.get("doi"), "| concept:", rec.get("conceptdoi"))
print("   title:", md.get("title"))
print("   version:", md.get("version"), "| pub_date:", md.get("publication_date"))
print("   desc 开头:", (md.get("description") or "")[:90])
print("   desc 长度:", len(md.get("description") or ""))
print("   文件数:", len(rec.get("files") or []))
print("✅ 完成")
