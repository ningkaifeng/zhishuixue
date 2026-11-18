#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：读 Zenodo 记录元数据并打印（用于官网 works 条目）"""
import json, requests

IDS = {
    "paper-en": "23328738",
    "toolkit": "24327222",
}

for name, rid in IDS.items():
    print("=" * 60)
    print(name, rid)
    print("=" * 60)
    for url in (f"https://zenodo.org/api/records/{rid}",
                f"https://zenodo.org/api/deposit/depositions/{rid}"):
        try:
            r = requests.get(url, timeout=60)
            print("  GET", url.split("/api/")[-1], "->", r.status_code)
            if r.status_code != 200:
                continue
            d = r.json()
            md = d.get("metadata", {})
            print("  title       :", md.get("title"))
            print("  pub_date    :", md.get("publication_date") or md.get("publication_date"))
            print("  doi         :", d.get("doi"))
            print("  conceptdoi  :", d.get("conceptdoi") or md.get("conceptdoi"))
            print("  version     :", md.get("version"))
            print("  resource    :", json.dumps(md.get("resource_type", {}), ensure_ascii=False))
            print("  language    :", md.get("language"))
            print("  license     :", json.dumps(md.get("rights") or md.get("license"), ensure_ascii=False)[:160])
            print("  keywords    :", md.get("keywords"))
            rel = md.get("related_identifiers") or []
            print("  related     :", json.dumps(rel, ensure_ascii=False)[:400])
            fnames = []
            if "files" in d:
                for f in d["files"]:
                    fnames.append(f.get("key") or f.get("filename"))
            if not fnames:
                try:
                    fr = requests.get(url.split("/records/")[0] + "/deposit/depositions/"
                                      + rid + "/files", timeout=60)
                    if fr.status_code == 200:
                        fnames = [x.get("filename") for x in fr.json()]
                except Exception:
                    pass
            print("  files       :", fnames)
            desc = md.get("description") or ""
            print("  desc_len    :", len(desc))
            print("  desc_head   :", desc[:300].replace("\n", " "))
            break
        except Exception as e:
            print("  ERR", e)
