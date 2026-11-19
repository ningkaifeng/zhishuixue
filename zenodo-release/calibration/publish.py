# -*- coding: utf-8 -*-
"""
发布《治水学自我校准说明 v1.0》到 Zenodo（新建独立记录，非新版本）。

沙箱 IP 被 Zenodo 限流，故在 GitHub Actions 中执行（ZENODO_TOKEN 存 repo secret）。

流程：POST /depositions 新建 → bucket PUT 传文件 → PUT metadata → POST publish
要点：bucket PUT 只接受 Content-Type: application/octet-stream；
      重复运行前先查是否已发布同名记录，避免产生第二个 DOI。
"""
import json
import os
import sys
import time
from urllib.parse import quote

import requests

API = "https://zenodo.org/api/deposit/depositions"
TOKEN = os.environ.get("ZENODO_TOKEN", "").strip()
if not TOKEN:
    sys.exit("缺少环境变量 ZENODO_TOKEN")

H_AUTH = {"Authorization": "Bearer " + TOKEN}
H_JSON = {**H_AUTH, "Content-Type": "application/json"}
BIN = {**H_AUTH, "Content-Type": "application/octet-stream"}

HERE = os.path.dirname(os.path.abspath(__file__))

TITLE_MARK = "自我校准"
TITLE = "治水学自我校准说明（Self-Calibration Statement of Dynamic Sustenance Theory, v1.0）"

FILES = [
    "DST-Self-Calibration-Statement-v1.0.pdf",
    "DST-Self-Calibration-Statement-v1.0.docx",
]


DESC = """本文档是治水学（Dynamic Sustenance Theory, DST）的自我校准说明，发布日 2026-11-19，校准对象为治水学母本 v15.0（含 v15.2 增补）与《治水学论纲》系列已发布文本（第 0 卷及第一至三十九篇）。

【要解决的问题】治水学的文本中长期并存两种语气：一种是限定的（"工作假设""不声称解决存在论难题""不是形而上学体系"），一种是抬高的（"元理论""元问题""存在论事实""第一哲学问题"）。两种表述各自都成立，问题出在它们相邻而存、可以随时切换——被质疑"凭什么"时引前者，被质疑"不过又一个框架"时引后者。这种可切换性，在学术上叫"可撤退性缺失"。

【本文档做什么】不推翻任何内容，只做一件事：把每句话归回它该在的层级。内容一个字不删；改的是"这句话属于哪一层、按哪一种语气读"。总口径一句话：上游松（起点是假设），下游紧（工具可失败），中间靠接口连。

【取代范围的精确界定】取代的是层级判定，不取代内容论证。四项层级表述自发布之日起终止使用：以"元理论"作为治水学的已完成身份；以"元问题"作"第一哲学问题"；以"存在论事实"描述"存续优先"；以"可证伪条件"承诺"每个核心命题都可被证伪"。保留的是内容论证：三浪不可还原、三元穷尽、动力-规则共生、尺度不可平移、载体独立性、文明四维、体相耦合、分层异步、语法锁定、要素归纳法与自诊七步、术语表、全部判例与历史材料。

【失效边界三判据】本文档给出"这套语法自己什么时候算失效"的判定标准——F1 模式断裂（系统层）、F2 功能损害累积（后果层）、F3 语法失效（工具层）。每条给出"观测什么 → 怎么判 → 落哪档 → 最小示例"，并附默认阈值（观测周期：个人按月、组织/企业按季、国家/文明按年；N＝3；F2 同类损害重复 ≥2 次；F3 触发 3 例）。阈值为默认值、立即生效，不标"待核"，可经修订程序调整。

【阅读规则】原文照读（除校准表内标"改/撤回"处，其余按原文读）；叠加读法（标"改/撤回"处原文保留作为思想记录，但按现判定理解）；指针优先（站点、GitHub、PDF 发布时在相应位置加指向本文档的锚点）。原文记录思想，补丁规定读法。

机器可读形态：https://zhishuixue.com/criteria.json 的 calibration 与 failure_boundaries 两段；人读要点页：https://zhishuixue.com/calibration.md

【English】A self-calibration statement for Dynamic Sustenance Theory (DST), published 2026-11-19, applied to the master text v15.0 and the published Outline series. It revises no substantive content; it reassigns each disputed expression to the layer it belongs to. Three overreaching claims are retracted — DST as a completed "metatheory", "sustenance-first" as an ontological fact or as the first philosophical question, and "falsifiability" as a promise covering every core proposition — while all substantive arguments are retained (irreducibility of the three forces, exhaustiveness of the three meta-operations, force-rule symbiosis, non-transferability across scales, carrier independence, the four dimensions of civilization, Ti-Xiang coupling, layered asynchrony, syntax lock-in, terminology, and all cases). It then specifies three failure-boundary criteria by which the framework itself is to be judged failing: F1 pattern rupture (system level), F2 cumulative functional damage (consequence level), F3 syntax failure (tool level), each with what to observe, how to judge, the resulting tier, a minimal example, and default thresholds. Reading rule: original text stands as intellectual record; flagged expressions are read through the calibrated layer."""

KEYWORDS = [
    "治水学", "Dynamic Sustenance Theory", "DST", "自我校准", "失效边界",
    "可证伪性", "元理论", "层级降格", "存续", "概念校准",
]

RELATED = [
    {"relation": "references", "identifier": "10.5281/zenodo.20372186",
     "resource_type": "publication-preprint"},          # 治水学母本
    {"relation": "references", "identifier": "10.5281/zenodo.23486787",
     "resource_type": "publication"},                   # 结构显影的判据
    {"relation": "isSupplementTo", "identifier": "https://zhishuixue.com/calibration.md",
     "resource_type": "other"},                         # 站点要点页
]

META = {
    "title": TITLE,
    "description": DESC,
    "version": "1.0",
    "publication_date": "2026-11-19",
    "upload_type": "publication",
    "publication_type": "report",
    "language": "zho",
    "license": "cc-by-4.0",
    "creators": [{
        "name": "Ning, Kaifeng",
        "affiliation": "Independent Researcher",
        "orcid": "0009-0001-4414-6058",
    }],
    "keywords": KEYWORDS,
    "related_identifiers": RELATED,
}


def call(method, url, **kw):
    for i in range(5):
        try:
            r = requests.request(method, url, timeout=120, **kw)
            if r.status_code < 500:
                return r
            print("   5xx，重试", r.status_code)
        except Exception as e:
            print("   网络异常，重试:", str(e)[:80])
        time.sleep(5)
    raise SystemExit("请求失败: " + url)


print("① 查重：是否已发布同名记录…")
r = call("GET", API, headers=H_AUTH, params={"size": 100, "sort": "mostrecent"})
if r.status_code == 200:
    data = r.json()
    hits = data.get("hits", {}).get("hits") if isinstance(data, dict) else data
    for h in hits or []:
        md = h.get("metadata", {}) or {}
        if TITLE_MARK in (md.get("title") or ""):
            print("   ⚠ 已存在记录，跳过发布")
            print("   DOI:", h.get("doi"))
            print("   record:", h.get("links", {}).get("html") or h.get("id"))
            sys.exit(0)
    print("   未发现已发布同名记录（草稿不计）")
else:
    print("   查重接口返回", r.status_code, "（继续）")

print("② 新建 deposition…")


def try_legacy(body_meta):
    """旧版 depositions API：POST 建 draft。返回 (did, bucket) 或 None。"""
    body = json.dumps({"metadata": body_meta}, ensure_ascii=False) if body_meta else json.dumps({})
    for node in (API, API + "/"):
        r = requests.post(node, headers=H_JSON, data=body, timeout=120)
        print(f"   POST {node} → {r.status_code}")
        if r.status_code in (200, 201):
            d = r.json()
            return d["id"], d["links"]["bucket"]
        if r.status_code >= 400:
            print("   body:", r.text[:300])
    return None


def try_new_api(body_meta):
    """新版 InvenioRDM records API（legacy 失败时兜底）。"""
    url = "https://zenodo.org/api/records"
    body = json.dumps({
        "access": {"files": "public", "record": "public"},
        "files": {"enabled": True},
        "metadata": {
            "title": body_meta["title"],
            "description": body_meta["description"],
            "publication_date": body_meta["publication_date"],
            "resource_type": {"id": "publication-report"},
            "creators": [{"person_or_org": {"type": "personal", "name": "Ning, Kaifeng",
                                            "identifiers": [{"scheme": "orcid", "identifier": "0009-0001-4414-6058"}]},
                          "affiliations": [{"name": "Independent Researcher"}]}],
            "publisher": "Zenodo",
            "subjects": [{"subject": k} for k in body_meta["keywords"]],
            "rights": [{"id": "cc-by-4.0"}],
            "languages": [{"id": "zho"}],
            "version": body_meta["version"],
        },
    }, ensure_ascii=False)
    r = requests.post(url, headers=H_JSON, data=body, timeout=120)
    print(f"   POST {url} → {r.status_code}")
    if r.status_code not in (200, 201):
        print("   body:", r.text[:400])
        return None
    return r.json()


did, bucket, newapi = None, None, None

res = try_legacy(META)
if res:
    did, bucket = res
    print("   draft id:", did)

if did is None:
    print("   旧版 API 失败，尝试新版 /api/records …")
    newapi = try_new_api(META)
    if newapi:
        did = newapi["id"]
        print("   draft id:", did, "(新版 API)")

if did is None:
    sys.exit("② 失败：两条 API 都无法创建 draft")

print("③ 上传文件…")
if bucket:
    for name in FILES:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            sys.exit("缺失文件: " + name)
        with open(path, "rb") as fh:
            content = fh.read()
        r = call("PUT", f"{bucket}/{quote(name)}", headers=BIN, data=content)
        print(f"   {name} → {r.status_code} ({len(content)} B)")
        if r.status_code >= 400:
            print(r.text[:400])
            sys.exit(2)
else:
    # InvenioRDM：PUT 建文件对象 → POST commit
    base_files = f"https://zenodo.org/api/records/{did}/draft/files"
    for name in FILES:
        path = os.path.join(HERE, name)
        with open(path, "rb") as fh:
            content = fh.read()
        r = call("PUT", f"{base_files}/{quote(name)}", headers=BIN, data=content)
        print(f"   PUT {name} → {r.status_code}")
        r = call("POST", f"{base_files}/{quote(name)}/commit", headers=H_JSON, data="{}")
        print(f"   commit {name} → {r.status_code}")
    r = call("GET", f"https://zenodo.org/api/records/{did}/draft", headers=H_AUTH)
    print("   draft 内文件:", len(r.json().get("files", {}).get("entries", {})))

print("④ 更新元数据…")
if bucket:
    payload = {"metadata": META}
    r = call("PUT", f"{API}/{did}", data=json.dumps(payload, ensure_ascii=False), headers=H_JSON)
    if r.status_code >= 400:
        print(r.status_code, r.text[:600])
        sys.exit(2)
    print("   元数据 OK")
else:
    print("   新版 API 已在创建时带元数据，跳过")

print("⑤ 发布…")
pub_url = (f"https://zenodo.org/api/records/{did}/draft/actions/publish" if not bucket
           else f"{API}/{did}/actions/publish")
r = call("POST", pub_url, headers=H_JSON, data="{}")
if r.status_code not in (200, 202):
    print(r.status_code, r.text[:400])
    sys.exit(2)
rec = r.json()
print("✅ 发布成功")
print("   version DOI:", rec.get("doi"))
print("   concept DOI:", rec.get("conceptdoi"))
print("   record id:", rec.get("id"))
print("   record_html:", rec.get("links", {}).get("record_html"))
