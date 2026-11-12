#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 3 条 Zenodo v1 记录里的旧站链接（ningkaifeng.github.io → zhishuixue.com）
用户指令（2026-11-12）：不能删记录，只改 IsPartOf 等关键元数据；description 改不掉的就留着。
走 GitHub Actions 执行（沙箱 IP 被 Zenodo 限流）。
"""
import os, sys, json, time, html

import requests

TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
API = "https://zenodo.org/api/deposit/depositions"

OLD = "ningkaifeng.github.io"
NEW = "https://zhishuixue.com/"
NEW_HOST = "zhishuixue.com"

TARGETS = [22088571, 22783960, 22785125]

H = {"Authorization": f"Bearer {TOKEN}"}
TIMEOUT = 60

# 只提交白名单字段（剔除 dates / prereserve_doi / communities 等只读或易报错字段）
KEEP = [
    "title", "upload_type", "publication_type", "image_type", "publication_date",
    "description", "creators", "contributors", "keywords", "license",
    "access_right", "access_conditions", "embargo_date", "imprint_publisher",
    "language", "version", "related_identifiers", "references", "communities",
    "grants", "subjects", "notes", "journal", "meeting", "imprint_place",
    "imprint_isbn", "partof_pages", "thesis_supervisors", "thesis_university",
]


def call(method, url, **kw):
    """带重试的请求"""
    last = None
    for i in range(4):
        try:
            r = requests.request(method, url, headers={**H, "Content-Type": "application/json"},
                                 timeout=TIMEOUT, **kw)
            return r
        except Exception as e:
            last = e
            print(f"    [retry {i+1}] {type(e).__name__}: {e}")
            time.sleep(4)
    raise last


def brief(r):
    try:
        j = r.json()
        if isinstance(j, dict):
            msg = j.get("message") or j.get("status") or ""
            errs = j.get("errors")
            return f"HTTP {r.status_code} | {msg} | errors={json.dumps(errs, ensure_ascii=False)[:300] if errs else '-'}"
        return f"HTTP {r.status_code} | {r.text[:200]}"
    except Exception:
        return f"HTTP {r.status_code} | {r.text[:200]}"


def fix_record(dep_id):
    print(f"\n{'='*70}\n>>> deposition {dep_id}\n{'='*70}")

    # 1) 读当前状态
    r = call("GET", f"{API}/{dep_id}")
    print(f"[1] GET  {brief(r)}")
    if r.status_code != 200:
        return {"id": dep_id, "ok": False, "stage": "get", "detail": brief(r)}
    rec = r.json()
    print(f"    state={rec.get('state')}  submitted={rec.get('submitted')}  version={rec.get('metadata',{}).get('version')}")

    # 2) 进入编辑
    r = call("POST", f"{API}/{dep_id}/actions/edit", data=json.dumps({}))
    print(f"[2] EDIT {brief(r)}")
    edit_ok = r.status_code in (200, 201, 202)
    if not edit_ok:
        print("    >>> 无法进入编辑（旧版本可能已锁定）")
        # 读一下是否仍可改：试新接口 draft
        r2 = call("GET", f"https://zenodo.org/api/records/{dep_id}/draft")
        print(f"[2b] GET draft {brief(r2)}")

    # 3) 取最新元数据（编辑态）
    r = call("GET", f"{API}/{dep_id}")
    if r.status_code != 200:
        return {"id": dep_id, "ok": False, "stage": "get2", "detail": brief(r)}
    cur = r.json()
    md = cur.get("metadata", {})

    desc_before = md.get("description", "") or ""
    rels_before = md.get("related_identifiers", []) or []

    old_in_desc = OLD in desc_before
    old_in_rels = any(OLD in str(x.get("identifier", "")) for x in rels_before)
    print(f"[3] 改前：description含旧站={old_in_desc}  关联含旧站={old_in_rels}  关联条数={len(rels_before)}")
    for x in rels_before:
        if OLD in str(x.get("identifier", "")):
            print(f"      → {x.get('relation')} = {x.get('identifier')}")

    if not old_in_desc and not old_in_rels:
        print("    已干净，无需修改")
        if edit_ok:
            call("POST", f"{API}/{dep_id}/actions/publish", data=json.dumps({}))
        return {"id": dep_id, "ok": True, "stage": "already_clean"}

    # 4) 改造 metadata
    new_md = {}
    for k in KEEP:
        if k in md:
            new_md[k] = md[k]

    # 4a) description：能改就改
    new_desc = desc_before.replace(f"https://{OLD}/", NEW).replace(f"http://{OLD}/", NEW).replace(OLD, NEW_HOST)
    if new_desc != desc_before:
        new_md["description"] = new_desc
        print("[4a] description 已替换链接")
    else:
        print("[4a] description 无变化")

    # 4b) related_identifiers：IsPartOf 改指向，其他含旧站的一并换
    new_rels = []
    changed_rel = 0
    for x in rels_before:
        y = dict(x)
        ident = str(y.get("identifier", ""))
        if OLD in ident:
            if y.get("relation") == "isPartOf":
                y["identifier"] = NEW
            else:
                y["identifier"] = ident.replace(f"https://{OLD}/", NEW).replace(f"http://{OLD}/", NEW).replace(OLD, NEW_HOST)
            changed_rel += 1
            print(f"[4b] {y.get('relation')}: {ident} → {y.get('identifier')}")
        new_rels.append(y)
    # 简单去重（同 relation + identifier）
    seen, dedup = set(), []
    for y in new_rels:
        key = (y.get("relation"), y.get("identifier"))
        if key in seen:
            print(f"[4b] 去重重复项: {key}")
            continue
        seen.add(key)
        dedup.append(y)
    new_md["related_identifiers"] = dedup

    # 5) 提交
    r = call("PUT", f"{API}/{dep_id}", data=json.dumps({"metadata": new_md}, ensure_ascii=False).encode("utf-8"))
    print(f"[5] PUT  {brief(r)}")
    if r.status_code not in (200, 201, 202):
        return {"id": dep_id, "ok": False, "stage": "put", "detail": brief(r),
                "edit_ok": edit_ok, "changed_rel": changed_rel}

    # 6) 发布
    r = call("POST", f"{API}/{dep_id}/actions/publish", data=json.dumps({}))
    print(f"[6] PUBLISH {brief(r)}")
    pub_ok = r.status_code in (200, 201, 202)

    # 7) 复核
    time.sleep(3)
    r = call("GET", f"{API}/{dep_id}")
    ok_verify = False
    if r.status_code == 200:
        m2 = r.json().get("metadata", {})
        d2 = m2.get("description", "") or ""
        rel2 = m2.get("related_identifiers", []) or []
        still_desc = OLD in d2
        still_rel = any(OLD in str(x.get("identifier", "")) for x in rel2)
        ok_verify = (not still_rel)
        print(f"[7] 复核：description仍含旧站={still_desc}  关联仍含旧站={still_rel}")
        for x in rel2:
            if x.get("relation") in ("isPartOf", "isVersionOf", "isSupplementTo"):
                print(f"      {x.get('relation')} = {x.get('identifier')}")

    return {"id": dep_id, "ok": pub_ok and ok_verify, "stage": "done",
            "edit_ok": edit_ok, "changed_rel": changed_rel,
            "desc_cleaned": not still_desc if r.status_code == 200 else None,
            "rel_cleaned": not still_rel if r.status_code == 200 else None}


def main():
    if not TOKEN:
        print("!! 缺少 ZENODO_TOKEN")
        sys.exit(1)
    print(f"目标 {len(TARGETS)} 条：{TARGETS}")
    results = []
    for d in TARGETS:
        try:
            results.append(fix_record(d))
        except Exception as e:
            print(f"!! {d} 异常: {type(e).__name__}: {e}")
            results.append({"id": d, "ok": False, "stage": "exception", "detail": str(e)})
        time.sleep(2)

    print(f"\n{'#'*70}\n汇总\n{'#'*70}")
    for x in results:
        print(json.dumps(x, ensure_ascii=False))
    n_ok = sum(1 for x in results if x.get("ok"))
    print(f"\n成功 {n_ok}/{len(results)}")
    # 只读成功不阻断（失败仅报告，便于用户决定）


if __name__ == "__main__":
    main()
