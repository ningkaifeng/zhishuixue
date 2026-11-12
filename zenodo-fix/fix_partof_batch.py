#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量补齐 Zenodo 版本记录的 IsPartOf（指向 https://zhishuixue.com/）
- 只改【历史版本】（is_last=false），最新版本一律跳过并报告
- 概要里没有官网的，追加一段官网声明
- 已有 isPartOf 但指向别处的，替换为新站
"""
import os, sys, json, time, re

import requests

TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
API = "https://zenodo.org/api/deposit/depositions"
NEW = "https://zhishuixue.com/"
NEWH = "zhishuixue.com"
OLD = "ningkaifeng.github.io"

# 19 条仅概要缺 IsPartOf + 7 条两处都无 = 26 条候选（版本记录）
CANDIDATES = [
    21753086, 21897465, 22008333, 22009627, 22067164, 22122291, 22176425,
    22242409, 22301915, 22304515, 22659486, 22699999, 23185396, 23609363,
    23613865, 23664768, 23766353, 23848814, 23911374,
    20278692, 20372186, 22225452, 23981177, 24099286, 24099834, 24124184,
]

H = {"Authorization": f"Bearer {TOKEN}"}
TIMEOUT = 60

KEEP = [
    "title", "upload_type", "publication_type", "image_type", "publication_date",
    "description", "creators", "contributors", "keywords", "license",
    "access_right", "access_conditions", "embargo_date", "imprint_publisher",
    "language", "version", "related_identifiers", "references", "communities",
    "grants", "subjects", "notes", "journal", "meeting", "imprint_place",
    "imprint_isbn", "partof_pages", "thesis_supervisors", "thesis_university",
]

OFFICIAL_BLOCK = (
    '<p><strong>官方网站 / Official site:</strong> '
    f'<a href="{NEW}">{NEW}</a> '
    '(术语母表 · 决策显影库判例 · 思想显影库 · 治水历定位刻度 / '
    'Terminology Master Table, Decision Shadowing Library, Thought Shadowing Library, Shui-Li Calendar)</p>'
)


def call(method, url, **kw):
    last = None
    for i in range(4):
        try:
            return requests.request(method, url, headers={**H, "Content-Type": "application/json"},
                                    timeout=TIMEOUT, **kw)
        except Exception as e:
            last = e
            print(f"    [retry {i+1}] {type(e).__name__}")
            time.sleep(4)
    raise last


def brief(r):
    try:
        j = r.json()
        if isinstance(j, dict):
            return f"HTTP {r.status_code} | {j.get('message','')} | {json.dumps(j.get('errors'), ensure_ascii=False)[:200] if j.get('errors') else '-'}"
        return f"HTTP {r.status_code}"
    except Exception:
        return f"HTTP {r.status_code} | {r.text[:150]}"


def latest_id_of(rec):
    """从 links.latest 解析最新版本 id"""
    links = rec.get("links") or {}
    u = links.get("latest") or ""
    m = re.search(r"/depositions/(\d+)$", u) or re.search(r"/records/(\d+)$", u)
    return int(m.group(1)) if m else None


def process(dep_id):
    print(f"\n{'-'*68}\n>>> {dep_id}")
    r = call("GET", f"{API}/{dep_id}")
    if r.status_code != 200:
        print(f"[!] GET 失败 {brief(r)}")
        return {"id": dep_id, "status": "get_failed", "detail": brief(r)}

    rec = r.json()
    lid = latest_id_of(rec)
    is_last = (lid == dep_id)
    title = ((rec.get("metadata") or {}).get("title") or "")[:36]
    print(f"    标题={title}")
    print(f"    latest={lid}  当前={dep_id}  → {'★最新版本' if is_last else '历史版本'}")

    if is_last:
        print("    >>> 跳过（最新版本，编辑会升版本号）")
        return {"id": dep_id, "status": "skipped_latest", "title": title}

    # 进入编辑
    r = call("POST", f"{API}/{dep_id}/actions/edit", data=json.dumps({}))
    print(f"[edit] {brief(r)}")
    if r.status_code not in (200, 201, 202):
        return {"id": dep_id, "status": "edit_failed", "detail": brief(r), "title": title}

    r = call("GET", f"{API}/{dep_id}")
    cur = r.json() if r.status_code == 200 else {}
    md = cur.get("metadata", {}) or {}
    desc = md.get("description", "") or ""
    rels = md.get("related_identifiers", []) or []

    new_md = {k: md[k] for k in KEEP if k in md}

    actions = []

    # 1) 概要补官网
    if NEWH not in desc:
        new_md["description"] = desc.rstrip() + "\n" + OFFICIAL_BLOCK
        actions.append("概要补官网声明")
    else:
        new_md["description"] = desc

    # 2) IsPartOf 补/改
    new_rels = []
    part_fixed = False
    for x in rels:
        y = dict(x)
        rel = (y.get("relation") or "")
        ident = str(y.get("identifier") or "")
        if rel.lower() == "ispartof":
            if NEWH not in ident:
                y["identifier"] = NEW
                y["scheme"] = "url"
                part_fixed = True
                actions.append(f"IsPartOf 改指向（原 {ident[:50]}）")
        elif OLD in ident:
            y["identifier"] = ident.replace(OLD, NEWH)
            actions.append(f"{rel} 去旧站")
        new_rels.append(y)

    if not any((x.get("relation") or "").lower() == "ispartof" for x in new_rels):
        new_rels.append({"relation": "isPartOf", "identifier": NEW, "scheme": "url"})
        part_fixed = True
        actions.append("IsPartOf 新增")

    new_md["related_identifiers"] = new_rels

    if not actions:
        print("    无需改动")
        call("POST", f"{API}/{dep_id}/actions/publish", data=json.dumps({}))
        return {"id": dep_id, "status": "no_change", "title": title}

    print("    动作:", " | ".join(actions))

    r = call("PUT", f"{API}/{dep_id}",
             data=json.dumps({"metadata": new_md}, ensure_ascii=False).encode("utf-8"))
    print(f"[put] {brief(r)}")
    if r.status_code not in (200, 201, 202):
        return {"id": dep_id, "status": "put_failed", "detail": brief(r), "title": title}

    r = call("POST", f"{API}/{dep_id}/actions/publish", data=json.dumps({}))
    print(f"[publish] {brief(r)}")
    ok = r.status_code in (200, 201, 202)

    time.sleep(2)
    r = call("GET", f"{API}/{dep_id}")
    v_ok = False
    if r.status_code == 200:
        m2 = r.json().get("metadata", {}) or {}
        d2 = m2.get("description", "") or ""
        r2 = m2.get("related_identifiers", []) or []
        v_ok = (NEWH in d2) and any((x.get("relation") or "").lower() == "ispartof" and NEWH in str(x.get("identifier"))
                                    for x in r2)
        print(f"[verify] 概要含新站={NEWH in d2}  IsPartOf含新站={any(NEWH in str(x.get('identifier')) for x in r2 if (x.get('relation') or '').lower()=='ispartof')}")

    return {"id": dep_id, "status": "ok" if (ok and v_ok) else "verify_failed",
            "title": title, "actions": actions, "publish_ok": ok, "verify_ok": v_ok}


def main():
    if not TOKEN:
        print("!! 缺少 ZENODO_TOKEN"); sys.exit(1)
    print(f"候选 {len(CANDIDATES)} 条（只改历史版本）")
    res = []
    for d in CANDIDATES:
        try:
            res.append(process(d))
        except Exception as e:
            print(f"!! {d} 异常 {type(e).__name__}: {e}")
            res.append({"id": d, "status": "exception", "detail": str(e)})
        time.sleep(1.5)

    print(f"\n{'#'*70}\n汇总\n{'#'*70}")
    from collections import Counter
    c = Counter(x["status"] for x in res)
    for k, v in c.items():
        print(f"  {k}: {v}")
    print("\n--- 逐条 ---")
    for x in res:
        print(json.dumps(x, ensure_ascii=False))
    print("\n--- 跳过的最新版本（需人工决定）---")
    for x in res:
        if x["status"] == "skipped_latest":
            print(f"  {x['id']}  {x.get('title','')}")


if __name__ == "__main__":
    main()
