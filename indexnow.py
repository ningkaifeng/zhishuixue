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
    locs = [u.strip() for u in re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read()) if u.strip()]
    if not locs:
        print("sitemap 无 URL，跳过")
        return
 
    body = json.dumps({
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}/{key}.txt",
        "urlList": locs,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            print(f"IndexNow 提交成功：{len(locs)} 个 URL，HTTP {r.status}")
    except Exception as e:
        print(f"IndexNow 提交失败（不阻断构建）：{e}")
 
 
if __name__ == "__main__":
    main()
