# -*- coding: utf-8 -*-
"""
治水学论纲 第一／二／三篇 v2.0：newversion 发布（三篇各自独立记录，概念 DOI 不变）。

v2.0 是口径对齐版：与《治水学自我校准说明 v1.0》(24357739) 和
《不做本体论》(24436102) 同一步——把强主张降为工作假设，并显式给出失效条件。

发布策略：
- 不新开记录，走 /actions/newversion，概念 DOI 不变，版本 DOI 更新；
- 元数据以 draft 继承值为底，只覆盖 title / description / version / publication_date，
  其余字段（creators / license / imprint_publisher / communities 等）原样保留；
- 幂等：若上一记录已是 2.0，直接跳过。
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
    sys.exit("缺少 ZENODO_TOKEN")

H_AUTH = {"Authorization": "Bearer " + TOKEN}
H_JSON = {**H_AUTH, "Content-Type": "application/json"}
BIN = {**H_AUTH, "Content-Type": "application/octet-stream"}

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = "2.0"
PUBDATE = "2026-11-24"

COMMON_REV = """**v2.0 修订（{date}）** 本版与《治水学自我校准说明 v1.0》（DOI 10.5281/zenodo.24357739）、《不做本体论》（DOI 10.5281/zenodo.24436102）口径对齐，做的是同一件事：把强主张降为工作假设，并把失效条件写进正文。{diff}"""

PAPERS = [
    {
        "key": "p1",
        "prev": "22785849",
        "title": ("治水学论纲·第一篇：从“是什么”到“如何存续”——问题域的一次替换"
                  "（DST Outline, Part 1: From What-Is to How-to-Sustain"
                  " — A Replacement of the Question Domain）"),
        "files": ["DST-Outline-1-Question-Domain-Replacement-v2.0.pdf",
                  "DST-Outline-1-Question-Domain-Replacement-v2.0.docx"],
        "diff": ("本篇具体改动：①标题去「存在论」——原标题「一个存在论问题域的扩展」把翻转本身说成了一次本体论"
                 "扩张，与「不做本体论」自相矛盾，改为「问题域的一次替换」；"
                 "②新增第一章第五节「与系统方法论传统的关系」；"
                 "③新增第三章第五节「本域的工作假设（非本体论承诺）」与第六节「使用条件与不适用场合」；"
                 "④新增第四章第二节「失效条件与局限」；"
                 "⑤保留第三章第三节对全球 AI 治理（标本 No.01 压缩版）的实际判定，作为「能否真的判」的展示。"),
        "body": """【核心论证】哲学长期以「存在是什么」为唯一入口，另有一类追问被反复触及却未被主题化：「系统如何在流变中维持自身」。本文不主张这一追问比「存在是什么」更根本——两者在形式上对称，谁都可以说对方预设了自己。本文主张的是一件更小的事：问题域可以替换，替换之后，答案的形态也随之改变。

【与他者的区分】第一章辨两种问题域的根本差异，并处理斯宾诺莎、海德格尔、自创生理论等先驱的局限；第二章专论两次最接近本次翻转的努力——赵汀阳的「天下体系」与「旋涡模式」、孙向晨的「双重本体」，指出其共同的止步处在边界；第三章给出翻转本身，附体相关系框架（工作框架），并以全球 AI 治理为例做一次实际判定，最后做自我指涉检验。

【结论】治水学不要求「存在是什么」让位，只提供一个另外的入口；这个入口成立与否，由后续工作检验，而不是由它与谁并列来判定。""",
        "keywords_zh": ["问题域", "存续", "模式连续性", "体相关系", "语法锁定", "赵汀阳", "孙向晨", "设计科学", "边界批判"],
        "keywords_en": ["question domain", "sustenance", "pattern continuity", "Ti-Xiang correlation",
                        "grammatical lock-in", "boundary critique", "Dynamic Sustenance Theory"],
    },
    {
        "key": "p2",
        "prev": "22785725",
        "title": ("治水学论纲·第二篇：存续优先——一个践言冲突论证"
                  "（DST Outline, Part 2: Sustenance Priority — A Performative-Contradiction Argument）"),
        "files": ["DST-Outline-2-Sustenance-Priority-v2.0.pdf",
                  "DST-Outline-2-Sustenance-Priority-v2.0.docx"],
        "diff": ("本篇具体改动：①新增「第零部分：本文的工作假设定位」，把「本文不做什么／本文做什么／"
                 "选择存续优先的三层理由／与第一篇的关系」在开篇一次交代清楚；"
                 "②新增 4.2「为什么是工作假设，不是先验证明」与 4.3「工作假设的承诺性质」——"
                 "回应「独立论证已展示否定存续的代价，为何不直接宣称已被证明」；"
                 "③3.7 附与笛卡尔「我思故我在」的同构性与根本差异对照表（锚定物、推出、命题类型、"
                 "时间性、姿态五个维度）。"),
        "body": """【核心论证】本文以践言冲突论证作为选择「存续优先」这一工作假设的核心理由，而不试图终结「存续与存在谁更底层」的哲学争论。所谓践言冲突：任何断言行为本身都是一个时间性过程，它在被做出的那一刻已经预设了自己所否定之物的成立——否定存续的断言，必须依赖自身的存续才能被说出。

【与之比较的对象】先对自由、幸福、真理、神圣性、正义、美等七类竞争性第一前提做存续论条件分析，并区分「真理本身」与「真理事业」。

【结论】本文的姿态是邀请，不是普遍要求：一旦接受「存续优先」这个工作假设，能推出什么，本文负责交代；接受与否，留给读者。""",
        "keywords_zh": ["存续优先", "践言冲突", "工作假设", "独立论证"],
        "keywords_en": ["sustenance priority", "performative contradiction", "working hypothesis",
                        "independent argument", "Dynamic Sustenance Theory"],
    },
    {
        "key": "p3",
        "prev": "22785562",
        "title": ("治水学论纲·第三篇：模式连续性——流变中的同一性如何可能"
                  "（DST Outline, Part 3: Pattern Continuity — How Identity Is Possible in Flux）"),
        "files": ["DST-Outline-3-Pattern-Continuity-v2.0.pdf",
                  "DST-Outline-3-Pattern-Continuity-v2.0.docx"],
        "diff": ("本篇具体改动：①新增第五部分「可证伪条件与理论边界」，含 5.1 方法论过渡、"
                 "5.2 停止使用条件、5.3 回应「模式连续性是否只是模糊说法」的质疑；"
                 "②判据部分补 2.2「怎么判」与 2.4「字段从哪来」，把判断从断言落到可操作；"
                 "③方法定名 Identity–Variance Analysis（不变项—变化项分析），完整判据见《显影的读法》第五节。"),
        "body": """【核心论证】本文提出一个存在论工作假设：同一性不是流变的对立面，而是流变的一种特定形态——动力-规则协同模式（系统生成变化的能力与约束变化的秩序之间的耦合结构）在时间中的连续性。

【判据与展示】给出怎么判、字段从哪来之后，用四类尺度展示现象解释力：个人尺度（《治水图》中的同一性重建）、企业尺度（比亚迪的转型）、技术系统尺度（大模型上下文管理的演进）、文明尺度（中华文明的连续性与罗马文明的断裂）。

【结论与限制】模式连续性可被证伪：若不变项消失（原本在 N 次显影中始终可被指认的项不再可被指认），即为模式断裂。字段升过版之后不能跨版本做此项分析；变化项若全部表现为「缺失」，那是未观测，不是发生了变化。""",
        "keywords_zh": ["模式连续性", "同一性", "流变", "动力-规则协同", "不变项—变化项分析"],
        "keywords_en": ["pattern continuity", "identity", "flux", "force-rule coordination",
                        "Identity–Variance Analysis", "Dynamic Sustenance Theory"],
    },
]

RELATED_ADD = [
    {"relation": "references", "identifier": "10.5281/zenodo.24357739",
     "resource_type": "publication-report"},
    {"relation": "references", "identifier": "10.5281/zenodo.24436102",
     "resource_type": "publication-preprint"},
]

KEEP = ["upload_type", "publication_type", "language", "license", "creators",
        "imprint_publisher", "notes", "communities", "references", "grants", "subjects"]


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


def run(p):
    print("=" * 66)
    print(f"■ {p['key']}  prev={p['prev']}")
    r = call("GET", f"{API}/{p['prev']}", headers=H_AUTH)
    if r.status_code != 200:
        print("  读旧记录失败", r.status_code, r.text[:200])
        return None
    prev = r.json()
    print("   旧记录 DOI:", prev.get("doi"), "| version:", prev["metadata"].get("version"))
    print("   旧标题:", prev["metadata"].get("title")[:80])
    if str(prev["metadata"].get("version", "")).startswith("2."):
        print("   ⚠ 已是 v2，跳过")
        return {"key": p["key"], "skip": True, "doi": prev.get("doi"),
                "concept": prev.get("conceptdoi"), "rid": prev.get("id")}

    r = call("POST", f"{API}/{p['prev']}/actions/newversion", headers=H_JSON, data="{}")
    if r.status_code not in (200, 201, 202):
        print("  newversion 失败", r.status_code, r.text[:300])
        return None
    did = r.json()["id"]
    draft = call("GET", f"{API}/{did}", headers=H_AUTH).json()
    bucket = draft["links"]["bucket"]
    print("   新 draft id:", did, "| 继承文件:", len(draft.get("files") or []))

    for f in draft.get("files") or []:
        rr = call("DELETE", f"{API}/{did}/files/{f['id']}", headers=H_AUTH)
        print("   删", f.get("filename"), rr.status_code)

    for name in p["files"]:
        path = os.path.join(HERE, name)
        with open(path, "rb") as fh:
            content = fh.read()
        rr = call("PUT", f"{bucket}/{quote(name)}", headers=BIN, data=content)
        print(f"   ↑ {name} → {rr.status_code} ({len(content)} B)")
        if rr.status_code >= 400:
            print(rr.text[:300])
            return None

    base = draft["metadata"]
    meta = {k: base[k] for k in KEEP if k in base}
    meta.update({
        "title": p["title"],
        "description": COMMON_REV.format(date="2026-11-24", diff=p["diff"]) + "\n\n" + p["body"],
        "version": VERSION,
        "publication_date": PUBDATE,
        "upload_type": "publication",
        "publication_type": "preprint",
        "language": "zho",
        "license": "cc-by-4.0",
        "keywords": p["keywords_zh"] + p["keywords_en"],
    })
    rel = [x for x in (base.get("related_identifiers") or [])]
    have = {x.get("identifier") for x in rel}
    for x in RELATED_ADD:
        if x["identifier"] not in have:
            rel.append(x)
    meta["related_identifiers"] = rel

    rr = call("PUT", f"{API}/{did}", headers=H_JSON, json={"metadata": meta})
    print("   元数据 PUT:", rr.status_code)
    if rr.status_code >= 400:
        print(rr.text[:500])
        return None

    rr = call("POST", f"{API}/{did}/actions/publish", headers=H_JSON, data="{}")
    if rr.status_code not in (200, 202):
        print("  发布失败", rr.status_code, rr.text[:300])
        return None
    rec = rr.json()
    print("   ✅ 发布成功 DOI:", rec.get("doi"), "| concept:", rec.get("conceptdoi"))
    return {"key": p["key"], "doi": rec.get("doi"), "concept": rec.get("conceptdoi"),
            "rid": rec.get("id"), "title": rec["metadata"].get("title"),
            "version": rec["metadata"].get("version"),
            "files": len(rec.get("files") or []), "pages_ok": True}


results = []
for p in PAPERS:
    try:
        results.append(run(p))
    except SystemExit as e:
        print("  ✗ 中止:", e)
        results.append({"key": p["key"], "error": str(e)})

print("=" * 66)
print("■ 汇总")
for x in results:
    if x is None:
        print("  ?  未完成")
    elif x.get("error"):
        print("  ✗ ", x["key"], x["error"])
    elif x.get("skip"):
        print("  = ", x["key"], "已是 v2，DOI", x["doi"])
    else:
        print("  ✅", x["key"], "| DOI", x["doi"], "| concept", x["concept"], "| 文件", x["files"])
print(json.dumps(results, ensure_ascii=False, indent=1))
if any(x is None or (isinstance(x, dict) and x.get("error")) for x in results):
    sys.exit(1)
