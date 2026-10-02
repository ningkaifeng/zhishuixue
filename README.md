# 治水学主页（自动生成）

本仓库是治水学的学术主页。页面与机器可读文件由 `papers.yml` **自动生成**。

## 文件一览
| 文件 | 说明 |
|---|---|
| `papers.yml` | **唯一数据源**（作品、术语、站点信息）。你只需要改这个。 |
| `build.py` | 生成脚本，别动。 |
| `index.html` `glossary.html` `glossary.md` `llms.txt` `citations.bib` `sitemap.xml` | 自动生成，**请勿手动编辑**（下次会被覆盖）。 |
| `robots.txt` `CITATION.cff` `preview.png` | 固定资源。 |

## 怎么发一篇新论文
1. 打开 `papers.yml`，在 `works:` 下面照葫芦加一条（标题、DOI、日期、摘要、关键词）。
2. 提交（commit）。
3. GitHub 会自动运行 `build.py`，上面那几个文件自动更新、自动上线。

## 怎么改主页文案 / 换域名
改 `papers.yml` 顶部的 `site:` 部分即可（例如 `base_url`）。
