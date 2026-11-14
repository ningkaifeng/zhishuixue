#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexNow 提交器
------------------------------------------------------------
作用：把 sitemap.xml 里的全部 URL 批量提交给 IndexNow
（Bing / Yandex / Seznam / Naver 等即时索引协议），
让新发布的论文与判例更快被搜索引擎与 AI 检索层收录。

用法：  python3 indexnow.py
位置：  在 GitHub Actions 里于 build.py 之后运行。
说明：  提交失败不阻断构建（网络问题不应让站点构建失败）。
       key 文件 <indexnow_key>.txt 由 build.py 自动生成并随仓库发布。
"""
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    try:
        import yaml
        with open(os.path.join(ROOT, "papers.yml"), encoding="utf-8") as f:
            d = yaml.safe_load(f)
        key = d["site"]["indexnow_key"]
        host = d["site"]["base_url"].split("//")[-1].strip("/")
    except Exception as e:
        print("读取 papers.yml 失败：", e)
        return

    sm = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(sm):
        print("缺少 sitemap.xml，跳过")
        return
    # 只提交「当日有变更」的 URL —— IndexNow 是增量通知协议，
    # 每天把全站重推一遍会被引擎视为噪音，反而降低可信度（2026-11-14 改）。
    import datetime
    xml = open(sm, encoding="utf-8").read()
    today = datetime.date.today().isoformat()
    locs = []
    for blk in re.findall(r"<url>(.*?)</url>", xml, re.S):
        m_loc = re.search(r"<loc>(.*?)</loc>", blk)
        m_lm = re.search(r"<lastmod>(.*?)</lastmod>", blk)
        if not m_loc:
            continue
        lm = (m_lm.group(1).strip() if m_lm else "")
        if lm >= today:           # 字符串比较对 ISO 日期成立
            locs.append(m_loc.group(1).strip())
    print(f"IndexNow：今日（{today}）有变更的 URL {len(locs)} 个")
    if not locs:
        print("  今日无变更，跳过提交（不制造噪音）")
        return

    body = json.dumps({
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}/{key}.txt",
        "urlList": locs,
    }).encode("utf-8")

    # 多端点提交：任一成功即可。实测（2026-10-24）api.indexnow.org 与
    # www.bing.com/indexnow 可能返回 403 UserForbiddedToAccessSite
    # （自造 key 未在 Bing 站长平台登记时会发生），而 yandex.com/indexnow 返回 202；
    # IndexNow 为共享协议，提交至任一端点后其他参与引擎亦可获知该 URL。
    ENDPOINTS = [
        "https://api.indexnow.org/indexnow",
        "https://www.bing.com/indexnow",
        "https://yandex.com/indexnow",
    ]
    ok, lines = 0, []
    for ep in ENDPOINTS:
        req = urllib.request.Request(
            ep, data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                lines.append(f"  {ep} -> HTTP {r.status}")
                if r.status in (200, 202):
                    ok += 1
        except Exception as e:
            lines.append(f"  {ep} -> 失败：{e}")

    print(f"IndexNow 提交：{len(locs)} 个 URL，成功端点 {ok}/{len(ENDPOINTS)}")
    for ln in lines:
        print(ln)
    if ok == 0:
        print("  提示：全部端点失败时，请到 Bing 站长平台 IndexNow 页生成官方 key，"
              "替换 papers.yml 的 site.indexnow_key 后重试。")


if __name__ == "__main__":
    main()
